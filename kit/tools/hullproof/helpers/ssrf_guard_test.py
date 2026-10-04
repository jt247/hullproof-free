#!/usr/bin/env python3
"""SSRF guard test harness. Python 3 standard library only. It makes no network call and resolves no name.

It holds a table of blocked address ranges and a set of test URLs. The expected verdict (block or allow) of every URL is
computed from the table with the `ipaddress` module, so the expectations come from one place and can be exported to a test
in any language. Hostnames never reach a resolver: each case that uses a name carries its own stub answers.

  python3 tools/hullproof/helpers/ssrf_guard_test.py --list                 # print the cases and the expected verdicts
  python3 tools/hullproof/helpers/ssrf_guard_test.py --emit json > cases.json   # for a test in the app's own language
  python3 tools/hullproof/helpers/ssrf_guard_test.py --cmd 'node tools/guard-cli.mjs'   # run a guard program against every case
  python3 tools/hullproof/helpers/ssrf_guard_test.py --guard mypkg.guard:is_allowed     # run a Python guard function
  python3 tools/hullproof/helpers/ssrf_guard_test.py --rebind-note

Guard under test. With --cmd the program is started once per case with the URL on standard input and the stub answers in the
environment variable SSRF_RESOLVE (a JSON object, host name to list of addresses; the guard must use it instead of DNS). It
prints `allow` or `block` as the first word of standard output. With --guard the function is called as fn(url, resolve) and
returns True to allow. A guard that cannot take a resolver stub cannot be tested without the network, and that is a finding:
make the resolver injectable. The exit status is 0 when every case matches, 1 when any case differs, 2 on a usage error.
"""
import argparse
import ipaddress
import importlib
import json
import os
import subprocess
import sys
from urllib.parse import unquote

# Blocked ranges. Sources: IANA IPv4 and IPv6 Special-Purpose Address Registries (RFC 6890), RFC 6598 (shared address space),
# RFC 3056 (6to4), RFC 6052 (NAT64), RFC 4380 (Teredo), RFC 4291 (IPv6 addressing), and the cloud provider metadata documentation
# for the two metadata addresses that are not covered by a special purpose range.
BLOCK_V4 = [
    ("0.0.0.0/8", "this network and the unspecified address"),
    ("10.0.0.0/8", "private use"),
    ("100.64.0.0/10", "shared address space (CGNAT), includes the Alibaba Cloud metadata address 100.100.100.200"),
    ("127.0.0.0/8", "loopback"),
    ("169.254.0.0/16", "link local, includes the AWS, Azure and GCP metadata address 169.254.169.254"),
    ("172.16.0.0/12", "private use"),
    ("192.0.0.0/24", "IETF protocol assignments, includes the Oracle Cloud metadata address 192.0.0.192"),
    ("192.0.2.0/24", "documentation (TEST-NET-1)"),
    ("192.88.99.0/24", "6to4 relay anycast (deprecated)"),
    ("192.168.0.0/16", "private use"),
    ("198.18.0.0/15", "benchmarking"),
    ("198.51.100.0/24", "documentation (TEST-NET-2)"),
    ("203.0.113.0/24", "documentation (TEST-NET-3)"),
    ("224.0.0.0/4", "multicast"),
    ("240.0.0.0/4", "reserved, includes the limited broadcast address"),
    ("168.63.129.16/32", "Azure platform address (WireServer), a public address that Azure documents for host services"),
]
BLOCK_V6 = [
    ("::/8", "unspecified, loopback and the deprecated IPv4 compatible range"),
    ("100::/64", "discard only"),
    ("2001::/32", "Teredo"),
    ("2001:db8::/32", "documentation"),
    ("fc00::/7", "unique local, includes the AWS IPv6 metadata address fd00:ec2::254"),
    ("fe80::/10", "link local"),
    ("ff00::/8", "multicast"),
]
NETS_V4 = [(ipaddress.ip_network(c), why) for c, why in BLOCK_V4]
NETS_V6 = [(ipaddress.ip_network(c), why) for c, why in BLOCK_V6]
NAT64 = ipaddress.ip_network("64:ff9b::/96")
SIXTOFOUR = ipaddress.ip_network("2002::/16")


def parse_ipv4_legacy(host):
    """Parse the dotted, decimal, octal and hexadecimal IPv4 forms that URL parsers and inet_aton accept. None if not an IPv4 form."""
    if not host:
        return None
    parts = host.split(".")
    if len(parts) > 4 or any(p == "" for p in parts):
        return None
    nums = []
    for p in parts:
        try:
            if p.lower().startswith("0x"):
                nums.append(int(p[2:] or "0", 16))
            elif len(p) > 1 and p.startswith("0"):
                nums.append(int(p, 8))
            else:
                nums.append(int(p, 10))
        except ValueError:
            return None
    *head, last = nums
    if any(n > 255 for n in head) or last >= 256 ** (4 - len(head)):
        return None
    value = last
    for i, n in enumerate(head):
        value += n << (8 * (3 - i))
    return ipaddress.IPv4Address(value)


def host_of(url):
    """The host a WHATWG style parser uses for an http or https URL: the part after the last `@` of the authority, without port.
    Returns (scheme, host) with host None when the URL is malformed. The authority ends at the first `/`, `\\`, `?` or `#`."""
    scheme, sep, rest = url.partition(":")
    scheme = scheme.lower()
    if not sep or not rest.startswith("//"):
        return scheme, None
    auth = rest[2:]
    for i, ch in enumerate(auth):
        if ch in "/\\?#":
            auth = auth[:i]
            break
    host = auth.rsplit("@", 1)[-1]
    if host.startswith("["):
        end = host.find("]")
        if end < 0:
            return scheme, None
        return scheme, host[: end + 1]
    host = host.rsplit(":", 1)[0] if ":" in host else host
    return scheme, host or None


def classify_host(host):
    """('ip', address) for an IP literal in any accepted form, else ('name', lowercase name without a trailing dot)."""
    if host.startswith("["):
        inner = unquote(host[1:-1]).split("%", 1)[0]
        try:
            return "ip", ipaddress.IPv6Address(inner)
        except ValueError:
            return "bad", host
    h = unquote(host).lower()
    h = h[:-1] if h.endswith(".") else h
    v4 = parse_ipv4_legacy(h)
    if v4 is not None:
        return "ip", v4
    last = h.rsplit(".", 1)[-1]
    if last.isdigit() or (last.startswith("0x") and all(c in "0123456789abcdef" for c in last[2:])):
        return "bad", host  # the last label is a number but the whole host is not an IPv4 form: a URL parser rejects it
    return "name", h


def ip_blocked(ip):
    """True when the address is in a blocked range, after unwrapping the IPv4 inside mapped, 6to4 and NAT64 forms."""
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            return ip_blocked(ip.ipv4_mapped)
        if ip in SIXTOFOUR:
            return ip_blocked(ipaddress.IPv4Address((int(ip) >> 80) & 0xFFFFFFFF))
        if ip in NAT64:
            return ip_blocked(ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF))
        return any(ip in n for n, _ in NETS_V6)
    return any(ip in n for n, _ in NETS_V4)


def expected_verdict(url, resolve=None):
    """`block` or `allow` for a URL. Names are judged by every address in their stub answer; a name with no answer is blocked."""
    scheme, host = host_of(url)
    if scheme not in ("http", "https") or host is None:
        return "block"
    kind, val = classify_host(host)
    if kind == "bad":
        return "block"
    if kind == "ip":
        return "block" if ip_blocked(val) else "allow"
    if val == "localhost" or val.endswith(".localhost"):
        return "block"
    answers = (resolve or {}).get(val) or []
    if not answers:
        return "block"
    for a in answers:
        kind2, ip = classify_host(f"[{a}]" if ":" in a else a)
        if kind2 != "ip" or ip_blocked(ip):
            return "block"
    return "allow"


def _case(group, url, note="", resolve=None):
    return {"group": group, "url": url, "resolve": resolve or {}, "note": note}


PUBLIC = "93.184.216.34"
RAW_CASES = (
    [_case("ipv4 private", f"http://{h}/") for h in ("10.0.0.1", "10.255.255.255", "172.16.0.1", "172.31.255.255", "192.168.0.1", "192.168.255.254")]
    + [_case("ipv4 edge allow", f"http://{h}/", "just outside a blocked range") for h in ("172.32.0.1", "172.15.255.255", "100.63.255.255", "100.128.0.1", "169.255.0.1", "11.0.0.1")]
    + [_case("ipv4 loopback", f"http://{h}/") for h in ("127.0.0.1", "127.255.255.254", "127.0.0.1:8080")]
    + [_case("ipv4 link local and metadata", f"http://{h}/", n) for h, n in (
        ("169.254.169.254", "AWS, Azure and GCP instance metadata"), ("169.254.170.2", "AWS container task metadata"), ("169.254.0.1", ""),
        ("168.63.129.16", "Azure platform address, a public looking address"), ("192.0.0.192", "Oracle Cloud metadata"))]
    + [_case("ipv4 shared address space (CGNAT)", f"http://{h}/", n) for h, n in (
        ("100.64.0.1", ""), ("100.127.255.255", ""), ("100.100.100.200", "Alibaba Cloud metadata"))]
    + [_case("ipv4 unspecified and reserved", f"http://{h}/") for h in (
        "0.0.0.0", "0.1.2.3", "192.0.0.1", "192.0.2.1", "198.18.0.1", "198.19.255.255", "198.51.100.1", "203.0.113.1", "224.0.0.1", "240.0.0.1", "255.255.255.255")]
    + [_case("ipv4 public", f"http://{h}/") for h in ("8.8.8.8", "1.1.1.1", PUBLIC)]
    + [_case("ipv6 loopback and unspecified", f"http://{h}/") for h in ("[::1]", "[::]", "[0:0:0:0:0:0:0:1]", "[::1]:8080")]
    + [_case("ipv6 mapped ipv4", f"http://{h}/", n) for h, n in (
        ("[::ffff:127.0.0.1]", "loopback inside a mapped address"), ("[::ffff:7f00:1]", "same address in hex groups"), ("[0:0:0:0:0:ffff:7f00:1]", "same, written in full"),
        ("[::ffff:169.254.169.254]", "metadata inside a mapped address"), ("[::ffff:a9fe:a9fe]", "same, hex groups"), ("[::ffff:10.0.0.1]", ""),
        ("[::ffff:8.8.8.8]", "public address inside a mapped address, allowed"))]
    + [_case("ipv6 embedded ipv4 (NAT64, 6to4)", f"http://{h}/", n) for h, n in (
        ("[64:ff9b::7f00:1]", "NAT64 prefix around 127.0.0.1"), ("[64:ff9b::a9fe:a9fe]", "NAT64 prefix around the metadata address"), ("[64:ff9b::808:808]", "NAT64 around 8.8.8.8, allowed"),
        ("[2002:7f00:1::]", "6to4 around 127.0.0.1"), ("[2002:a9fe:a9fe::1]", "6to4 around the metadata address"), ("[2002:808:808::]", "6to4 around 8.8.8.8, allowed"))]
    + [_case("ipv6 special ranges", f"http://{h}/", n) for h, n in (
        ("[fe80::1]", "link local"), ("[fe80::1%25eth0]", "link local with a zone id"), ("[fc00::1]", "unique local"), ("[fd00:ec2::254]", "AWS IPv6 metadata"),
        ("[ff02::1]", "multicast"), ("[2001:db8::1]", "documentation"), ("[100::1]", "discard only"), ("[2001:0:4136:e378:8000:63bf:3fff:fdd2]", "Teredo"),
        ("[::7f00:1]", "deprecated IPv4 compatible form"))]
    + [_case("ipv6 public", f"http://{h}/") for h in ("[2606:4700:4700::1111]", "[2001:4860:4860::8888]")]
    + [_case("ipv4 written another way", f"http://{h}/", n) for h, n in (
        ("2130706433", "decimal for 127.0.0.1"), ("3232235521", "decimal for 192.168.0.1"), ("2852039166", "decimal for 169.254.169.254"),
        ("0177.0.0.1", "octal 127.0.0.1"), ("0251.0376.0251.0376", "octal metadata address"), ("017700000001", "one octal number"),
        ("0x7f.0.0.1", "hex first part"), ("0x7f000001", "one hex number"), ("0xA9FEA9FE", "hex metadata address"),
        ("127.1", "short form"), ("127.0.1", "three part form"), ("0x7f.1", "mixed hex and short"), ("0", "zero is 0.0.0.0"),
        ("0x08080808", "hex for 8.8.8.8, allowed"), ("134744072", "decimal for 8.8.8.8, allowed"))]
    + [_case("trailing dot", u, n, r) for u, n, r in (
        ("http://localhost./", "localhost with a trailing dot", None), ("http://127.0.0.1./", "address with a trailing dot", None),
        ("http://example.test./", "public name with a trailing dot, allowed", {"example.test": [PUBLIC]}),
        ("http://internal.test./", "private answer behind a trailing dot", {"internal.test": ["10.1.2.3"]}))]
    + [_case("userinfo and delimiters", u, n, r) for u, n, r in (
        ("http://example.test@127.0.0.1/", "the host is the part after the at sign", {"example.test": [PUBLIC]}),
        ("http://user:pass@169.254.169.254/", "credentials in front of the metadata address", None),
        ("http://example.test:80@127.0.0.1:80/", "name and port in front of the at sign", {"example.test": [PUBLIC]}),
        ("http://127.0.0.1@example.test/", "the host is example.test, allowed", {"example.test": [PUBLIC]}),
        ("http://user:pass@[::1]/", "credentials in front of an IPv6 loopback", None),
        ("http://example.test#@127.0.0.1/", "the at sign sits in the fragment, host is example.test, allowed", {"example.test": [PUBLIC]}),
        ("http://example.test?@127.0.0.1/", "the at sign sits in the query, host is example.test, allowed", {"example.test": [PUBLIC]}),
        ("http://example.test\\@127.0.0.1/", "a backslash ends the authority for http, host is example.test, allowed", {"example.test": [PUBLIC]}))]
    + [_case("names and resolver answers", u, n, r) for u, n, r in (
        ("http://localhost/", "", None), ("http://LOCALHOST/", "", None), ("http://app.localhost/", "", None),
        ("http://public.test/", "allowed", {"public.test": [PUBLIC]}),
        ("http://v6.test/", "allowed", {"v6.test": ["2606:4700:4700::1111"]}),
        ("http://loop.test/", "name that resolves to loopback", {"loop.test": ["127.0.0.1"]}),
        ("http://meta.test/", "name that resolves to the metadata address", {"meta.test": ["169.254.169.254"]}),
        ("http://mapped.test/", "name that resolves to a mapped loopback", {"mapped.test": ["::ffff:127.0.0.1"]}),
        ("http://two.test/", "one public and one private answer: block", {"two.test": [PUBLIC, "10.0.0.5"]}),
        ("http://none.test/", "no answer: block", {}))]
    + [_case("scheme and shape", u, n) for u, n in (
        ("file:///etc/passwd", "only http and https are allowed"), ("gopher://127.0.0.1/", ""), ("ftp://93.184.216.34/", ""), ("data:text/plain,hello", ""),
        ("http://[::1/", "malformed bracket"), ("http:///path", "no host"), ("//93.184.216.34/", "no scheme"), ("http://999.999.999.999/", "out of range numbers"))]
)

REBIND_NOTE = """DNS rebinding. A guard that resolves a name, checks the answer and then lets the HTTP client resolve the name again can be beaten:
the first answer is public and the second is private (a record with a time to live of 0). The cases in this file cannot prove
the guard is safe, because each case has one fixed answer. Test it with a resolver stub that returns a public address first and a
private address on every later lookup, then run one request through the full client:

  1. The request must connect to the address that was checked (the guard resolves once and pins the address for the connection),
     or the guard must check again on the connection (the connect hook of the client), not only before it.
  2. A redirect response whose Location names a private address must be refused: every hop goes through the same guard.
  3. Server side renderers (a headless browser, HTML to PDF, SVG conversion) fetch URLs found inside the markup, so they need the
     same guard on their network requests, or an egress rule that blocks the ranges in this table.
  4. The worker that sends webhooks later runs the same check at send time, not only when the URL was saved.

Without a stub and a pinned connection, record the guard as NOT ASSESSED: NEEDS DYNAMIC TEST."""


def build_cases():
    out = []
    for i, c in enumerate(RAW_CASES, 1):
        out.append({"id": f"SSRF-{i:03d}", **c, "expected": expected_verdict(c["url"], c["resolve"])})
    return out


def run_cmd(cmd, case, env_name="SSRF_RESOLVE"):
    env = {**os.environ, env_name: json.dumps(case["resolve"])}
    p = subprocess.run(cmd, shell=True, input=case["url"], capture_output=True, text=True, env=env, timeout=30)
    words = p.stdout.split()
    return words[0].lower() if words else f"error({p.returncode})"


def run_guard(spec):
    mod, _, fn = spec.partition(":")
    func = getattr(importlib.import_module(mod), fn)
    return lambda case: "allow" if func(case["url"], case["resolve"]) else "block"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--emit", choices=("json", "tsv"))
    ap.add_argument("--cmd", help="program that reads a URL on stdin and prints allow or block")
    ap.add_argument("--guard", help="python guard as module:function, called fn(url, resolve) -> bool")
    ap.add_argument("--rebind-note", action="store_true")
    a = ap.parse_args(argv)
    cases = build_cases()
    if a.rebind_note:
        print(REBIND_NOTE)
        return 0
    if a.emit == "json":
        print(json.dumps({"blocked_v4": BLOCK_V4, "blocked_v6": BLOCK_V6, "cases": cases}, indent=2))
        return 0
    if a.emit == "tsv":
        for c in cases:
            print("\t".join([c["id"], c["expected"], c["url"], json.dumps(c["resolve"]), c["group"]]))
        return 0
    if a.list or not (a.cmd or a.guard):
        for c in cases:
            print(f"{c['id']}  {c['expected']:5}  {c['group']:36} {c['url']}  {c['note']}")
        print(f"{len(cases)} cases, {sum(c['expected'] == 'block' for c in cases)} block, {sum(c['expected'] == 'allow' for c in cases)} allow")
        return 0
    if bool(a.cmd) == bool(a.guard):
        print("give exactly one of --cmd and --guard", file=sys.stderr)
        return 2
    judge = (lambda c: run_cmd(a.cmd, c)) if a.cmd else run_guard(a.guard)
    bad = []
    for c in cases:
        got = judge(c)
        if got != c["expected"]:
            bad.append((c, got))
    for c, got in bad:
        kind = "OPEN (guard allowed a blocked URL)" if got == "allow" else "BLOCKED (guard refused an allowed URL)" if got == "block" else "ERROR"
        print(f"{c['id']} {kind}: expected {c['expected']}, got {got}: {c['url']}  [{c['group']}]")
    print(f"{len(cases)} cases, {len(cases) - len(bad)} match, {len(bad)} differ")
    print("Reminder: these cases cannot show DNS rebinding safety. Run --rebind-note.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
