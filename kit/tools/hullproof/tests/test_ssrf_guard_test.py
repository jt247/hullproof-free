"""Tests for helpers/ssrf_guard_test.py. Standard library only, no network.

  python3 -m unittest tools/hullproof/tests/test_ssrf_guard_test.py
"""
import importlib.util
import ipaddress
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE.parent / "helpers" / "ssrf_guard_test.py"
spec = importlib.util.spec_from_file_location("ssrf_guard_test", SCRIPT)
h = importlib.util.module_from_spec(spec)
sys.modules["ssrf_guard_test"] = h
spec.loader.exec_module(h)

CASES = h.build_cases()
BY_URL = {c["url"]: c for c in CASES}


class Oracle(unittest.TestCase):
    def test_pinned_verdicts(self):
        pinned = {
            "http://169.254.169.254/": "block", "http://100.64.0.1/": "block", "http://100.63.255.255/": "allow", "http://172.32.0.1/": "allow",
            "http://[::ffff:127.0.0.1]/": "block", "http://[::ffff:8.8.8.8]/": "allow", "http://[::]/": "block", "http://[::1]/": "block",
            "http://2130706433/": "block", "http://0177.0.0.1/": "block", "http://0x7f.0.0.1/": "block", "http://127.1/": "block",
            "http://example.test@127.0.0.1/": "block", "http://127.0.0.1@example.test/": "allow", "http://localhost./": "block",
            "http://8.8.8.8/": "allow", "file:///etc/passwd": "block", "http://168.63.129.16/": "block", "http://[64:ff9b::7f00:1]/": "block",
        }
        for url, want in pinned.items():
            self.assertEqual(BY_URL[url]["expected"], want, url)

    def test_legacy_ipv4_forms(self):
        self.assertEqual(h.parse_ipv4_legacy("2130706433"), ipaddress.IPv4Address("127.0.0.1"))
        self.assertEqual(h.parse_ipv4_legacy("0251.0376.0251.0376"), ipaddress.IPv4Address("169.254.169.254"))
        self.assertEqual(h.parse_ipv4_legacy("0x7f.1"), ipaddress.IPv4Address("127.0.0.1"))
        self.assertEqual(h.parse_ipv4_legacy("0"), ipaddress.IPv4Address("0.0.0.0"))
        for bad in ("256.1.1.1", "1.2.3.4.5", "0xzz", "08.1.1.1", "example.com", "", "1..2"):
            self.assertIsNone(h.parse_ipv4_legacy(bad), bad)

    def test_the_table_is_at_least_as_strict_as_python_ipaddress(self):
        for c in CASES:
            scheme, host = h.host_of(c["url"])
            if host is None or scheme not in ("http", "https"):
                continue
            kind, ip = h.classify_host(host)
            if kind != "ip":
                continue
            inner = ip
            if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
                inner = ip.ipv4_mapped
            embedded = isinstance(inner, ipaddress.IPv6Address) and (inner in h.SIXTOFOUR or inner in h.NAT64)
            if c["expected"] == "allow" and not embedded:
                self.assertTrue(inner.is_global, c["url"])
            if not embedded and (inner.is_loopback or inner.is_link_local or inner.is_unspecified or inner.is_multicast or inner.is_private):
                self.assertEqual(c["expected"], "block", c["url"])

    def test_every_blocked_range_has_a_blocked_member_and_the_next_address_is_judged_on_its_own(self):
        for net, _ in h.NETS_V4 + h.NETS_V6:
            self.assertTrue(h.ip_blocked(net[0]), str(net))
            self.assertTrue(h.ip_blocked(net[-1]), str(net))
        self.assertFalse(h.ip_blocked(ipaddress.ip_address("100.128.0.1")))

    def test_cases_cover_every_required_family(self):
        text = " ".join(c["url"] + " " + c["group"] + " " + c["note"] for c in CASES).lower()
        for needle in ("10.0.0.1", "127.0.0.1", "169.254.169.254", "100.64.0.1", "::ffff:", "[::]", "[::1]", "@", "0177", "0x7f", "2130706433", "localhost.", "metadata"):
            self.assertIn(needle, text, needle)
        self.assertGreaterEqual(len(CASES), 100)
        self.assertEqual(len({c["id"] for c in CASES}), len(CASES))
        self.assertTrue(any(c["expected"] == "allow" for c in CASES))

    def test_hostnames_use_stub_answers_only(self):
        for c in CASES:
            scheme, host = h.host_of(c["url"])
            if host and h.classify_host(host)[0] == "name" and not host.lower().startswith("localhost") and not host.lower().endswith(".localhost"):
                self.assertIn(h.classify_host(host)[1], c["resolve"] or {"none.test": []}, c["url"])


class Harness(unittest.TestCase):
    def run_main(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_reference_guard_passes_every_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = pathlib.Path(tmp, "good_guard.py")
            guard.write_text("import sys, json, os\nsys.path.insert(0, %r)\nimport ssrf_guard_test as h\n"
                             "print(h.expected_verdict(sys.stdin.read(), json.loads(os.environ['SSRF_RESOLVE'])))\n" % str(SCRIPT.parent))
            r = self.run_main("--cmd", f"{sys.executable} {guard}")
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("0 differ", r.stdout)

    def test_a_naive_prefix_guard_is_caught_on_many_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = pathlib.Path(tmp, "naive_guard.py")
            guard.write_text("import sys\nu = sys.stdin.read()\nbad = ('http://127.', 'http://localhost', 'http://10.', 'http://192.168.')\n"
                             "print('block' if u.startswith(bad) else 'allow')\n")
            r = self.run_main("--cmd", f"{sys.executable} {guard}")
            self.assertEqual(r.returncode, 1)
            self.assertIn("OPEN (guard allowed a blocked URL)", r.stdout)
            self.assertGreater(len([l for l in r.stdout.splitlines() if l.startswith("SSRF-")]), 40)

    def test_python_guard_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            pathlib.Path(tmp, "mine.py").write_text("def allow_all(url, resolve):\n    return True\n")
            r = subprocess.run([sys.executable, str(SCRIPT), "--guard", "mine:allow_all"], capture_output=True, text=True, cwd=tmp,
                               env={**__import__("os").environ, "PYTHONPATH": tmp})
            self.assertEqual(r.returncode, 1)
            self.assertIn("OPEN", r.stdout)

    def test_emit_formats(self):
        data = json.loads(self.run_main("--emit", "json").stdout)
        self.assertEqual(len(data["cases"]), len(CASES))
        tsv = self.run_main("--emit", "tsv").stdout.splitlines()
        self.assertEqual(len(tsv), len(CASES))
        self.assertTrue(all(len(l.split("\t")) == 5 for l in tsv))

    def test_rebind_note_and_no_network_code(self):
        self.assertIn("DNS rebinding", self.run_main("--rebind-note").stdout)
        src = SCRIPT.read_text()
        for bad in ("import socket", "import urllib.request", "http.client", "import requests", "gethostbyname", "getaddrinfo"):
            self.assertNotIn(bad, src)
        self.assertNotIn(chr(0x2014), src)
        self.assertNotIn(chr(0x2013), src)


if __name__ == "__main__":
    unittest.main()
