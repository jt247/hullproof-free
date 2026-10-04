"""Tests for tools/hullproof/gitleaks.toml.

Every secret in these tests is synthetic. The values are built at run time from hashes, never written to a
file in this repository, so the kit does not trip its own scanner or a host's push protection.

  python3 -m unittest tools/hullproof/tests/test_gitleaks_config.py

Each case plants one value, runs gitleaks with the shipped config, and checks which rules reported it.
A planted value that is not found is a failing test, which is the planted value check of the standard.
"""
import base64
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
CONFIG = HERE.parent / "gitleaks.toml"
DOCS = HERE.parents[2] / "docs" / "hullproof"
ALNUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
HEX = "0123456789abcdef"


def rnd(tag, n, alphabet=ALNUM):
    out, i = "", 0
    while len(out) < n:
        digest = hashlib.sha256(f"{tag}:{i}".encode()).digest()
        out += "".join(alphabet[b % len(alphabet)] for b in digest)
        i += 1
    return out[:n]


def url(scheme, rest):
    # Built from parts so that the source file holds no connection URL with a password.
    return scheme + "://" + rest


def b64(obj):
    return base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).decode().rstrip("=")


def jwt(role, extra=None, ref_len=20):
    payload = {"iss": "supabase", "ref": rnd("ref", ref_len).lower(), "role": role, "iat": 1700000000, "exp": 2000000000}
    payload.update(extra or {})
    return b64({"alg": "HS256", "typ": "JWT"}) + "." + b64(payload) + "." + rnd("sig" + role, 43)


V = {
    "service_role": jwt("service_role"),
    "service_role_long_ref": jwt("service_role", ref_len=21),
    "service_role_extra_anon": b64({"alg": "HS256", "typ": "JWT"}) + "." + b64(
        {"iss": "supabase", "meta": {"role": "anon"}, "role": "service_role"}) + "." + rnd("sigx", 43),
    "anon": jwt("anon"),
    "anon_long_ref": jwt("anon", ref_len=22),
    "sb_secret": "sb_secret_" + rnd("sbs", 22) + "_" + rnd("sbc", 8),
    "sb_publishable": "sb_publishable_" + rnd("sbp", 22) + "_" + rnd("sbq", 8),
    "paddle_live": "pdl_live_apikey_01" + rnd("p1", 24, "abcdefghijklmnopqrstuvwxyz0123456789") + "_" + rnd("p2", 22) + "_" + rnd("p3", 3),
    "paddle_sdbx": "pdl_sdbx_apikey_01" + rnd("p4", 24, "abcdefghijklmnopqrstuvwxyz0123456789") + "_" + rnd("p5", 22) + "_" + rnd("p6", 3),
    "paddle_ntf": "pdl_ntfset_01" + rnd("p7", 24, "abcdefghijklmnopqrstuvwxyz0123456789") + "_" + rnd("p8", 32),
    "paystack": "sk_live_" + rnd("ps", 40, HEX),
    "resend": "re_" + rnd("r1", 8) + "_" + rnd("r2", 24),
    "render": "rnd_" + rnd("rn", 32),
    "posthog_personal": "phx_" + rnd("ph1", 43),
    "posthog_secret": "phs_" + rnd("ph2", 43),
    "posthog_project": "phc_" + rnd("ph3", 43),
    "sentry_org": "sntrys_" + rnd("s1", 64),
    "sentry_user": "sntryu_" + rnd("s2", 64, HEX),
    "openai": "sk-proj-" + rnd("oa", 64),
    "anthropic": "sk-ant-api03-" + rnd("an", 93) + "AA",
    "google": "AIza" + rnd("gg", 35),
    "r2": rnd("r2s", 64, HEX),
    "upstash": "A" + rnd("up", 44) + "=",
    "vercel": rnd("vc", 24),
    "aws_id": "AKIA" + rnd("aw", 16, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
    "agent_literal": rnd("al", 40),
}

# (file path, content template, accepted rule ids). A case passes when at least one accepted rule reports the file.
POSITIVE = [
    ("app/page.js", 'var k="{service_role}";', {"hullproof-supabase-service-role-jwt"}),
    ("app/page2.js", 'var k="{service_role_long_ref}";', {"hullproof-supabase-service-role-jwt"}),
    ("app/page3.js", 'var k="{service_role_extra_anon}";', {"hullproof-supabase-service-role-jwt"}),
    (".env.local", "NEXT_PUBLIC_SUPABASE_ANON_KEY={service_role}\n", {"hullproof-supabase-service-role-jwt"}),
    ("lib/admin.js", 'var k="{sb_secret}";', {"hullproof-supabase-secret-key"}),
    ("lib/pay.js", 'var k="{paddle_live}";', {"hullproof-paddle-api-key"}),
    ("lib/pay2.js", 'var k="{paddle_sdbx}";', {"hullproof-paddle-api-key"}),
    ("lib/hook.js", 'var k="{paddle_ntf}";', {"hullproof-paddle-webhook-secret"}),
    ("lib/ps.js", 'var k="{paystack}";', {"stripe-access-token", "hullproof-paystack-secret-key"}),
    ("lib/mail.js", 'var k="{resend}";', {"hullproof-resend-api-key"}),
    ("lib/host.js", 'var k="{render}";', {"hullproof-render-api-key"}),
    ("lib/ph1.js", 'var k="{posthog_personal}";', {"hullproof-posthog-secret-key"}),
    ("lib/ph2.js", 'var k="{posthog_secret}";', {"hullproof-posthog-secret-key"}),
    ("lib/sentry1.js", 'var k="{sentry_org}";', {"hullproof-sentry-org-auth-token"}),
    ("lib/sentry2.js", 'var k="{sentry_user}";', {"sentry-user-token"}),
    ("lib/ai1.js", 'var k="{openai}";', {"hullproof-openai-project-key", "openai-api-key"}),
    ("lib/ai2.js", 'var k="{anthropic}";', {"anthropic-api-key"}),
    ("lib/g.js", 'var k="{google}";', {"gcp-api-key"}),
    ("lib/r2.js", 'const R2_SECRET_ACCESS_KEY="{r2}";', {"hullproof-r2-secret-access-key"}),
    ("lib/up.js", 'const UPSTASH_REDIS_REST_TOKEN="{upstash}";', {"hullproof-upstash-token"}),
    ("lib/vc.js", 'const VERCEL_TOKEN="{vercel}";', {"hullproof-vercel-token"}),
    ("config/db.js", 'const u="' + url("postgres", "app:Hunter2Pass@db.internal.example:5432/app") + '";', {"hullproof-url-with-password"}),
    ("config/db2.json", '{"url":"' + url("mysql", "root:Summer2024x@10.0.0.5/db") + '"}', {"hullproof-url-with-password"}),
    ("config/db3.js", 'const u="' + url("mongodb+srv", "svc:Wq9mZ3pLx7@cluster0.example.net/app") + '";', {"hullproof-url-with-password"}),
    ("config/cache.js", 'const u="' + url("rediss", "default:Zk4vN8qRt2@eu1-calm.upstash.io:6379") + '";', {"hullproof-url-with-password"}),
    (".mcp.json", '{"mcpServers":{"s":{"env":{"AWS_ACCESS_KEY_ID":"{aws_id}"}}}}', {"hullproof-aws-key-in-agent-config"}),
    (".claude/settings.local.json", '{"env":{"SOME_API_KEY":"{agent_literal}"}}', {"hullproof-agent-config-literal-secret"}),
]

# Build output folders are scanned on purpose. The same value must be found in each.
BUILD_FOLDERS = [".next/static/chunks/app.js", "dist/index.js", "build/static/main.js", ".vercel/output/static/a.js",
                 "coverage/lcov-report/a.js", "designs/mock.js", ".turbo/cache.js", ".expo/web/a.js"]

NEGATIVE = [
    ("app/client.js", 'var k="{anon}";'),
    ("app/client2.js", 'var k="{anon_long_ref}";'),
    (".env", "NEXT_PUBLIC_SUPABASE_ANON_KEY={anon}\n"),
    (".env.example", "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY={sb_publishable}\n"),
    ("app/pub.js", 'var k="{sb_publishable}";'),
    ("app/ph.js", 'posthog.init("{posthog_project}")'),
    ("docs/a.md", "Use postgresql://postgres:[YOUR-PASSWORD]@db.example.supabase.co:5432/postgres\n"),
    ("docs/b.md", "DATABASE_URL=postgres://user:${DB_PASSWORD}@localhost:5432/app\n"),
    ("docs/c.md", "DATABASE_URL=postgres://user:password@localhost:5432/app\n"),
    ("src/names.js", "const re_render_something_long_name_for_state = 1;\n"),
    (".mcp.json", '{"mcpServers":{"s":{"env":{"SOME_API_KEY":"${SOME_API_KEY}"}}}}'),
    ("src/dsn.js", 'Sentry.init({dsn:"https://abcdef0123456789abcdef0123456789@o1.ingest.sentry.io/123"})'),
    ("node_modules/pkg/index.js", 'var k="{sb_secret}";'),
]


def fill(template):
    out = template
    for k, v in V.items():
        out = out.replace("{" + k + "}", v)
    return out


def scan(root, mode="dir", config=CONFIG, extra=()):
    if not shutil.which("gitleaks"):
        raise unittest.SkipTest("gitleaks not installed")
    cmd = ["gitleaks", mode, str(root), "--no-banner", "--redact", "--exit-code", "0",
           "--config", str(config), "-f", "json", "-r", "-", *extra]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(proc.stdout or "[]")


def by_file(findings, root):
    out = {}
    for f in findings:
        rel = str(pathlib.Path(f["File"]).resolve().relative_to(pathlib.Path(root).resolve())) if f.get("File") else ""
        out.setdefault(rel, set()).add(f["RuleID"])
    return out


def write(root, rel, content):
    p = pathlib.Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


class ConfigShapes(unittest.TestCase):
    def test_each_planted_secret_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            for rel, tpl, _ in POSITIVE:
                write(tmp, rel, fill(tpl))
            found = by_file(scan(tmp), tmp)
        missing = [f"{rel} expected one of {sorted(accepted)}, got {sorted(found.get(rel, []))}"
                   for rel, _, accepted in POSITIVE if not (found.get(rel, set()) & accepted)]
        self.assertEqual(missing, [])

    def test_build_output_folders_are_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            for rel in BUILD_FOLDERS:
                write(tmp, rel, fill('var k="{paddle_live}";'))
            found = by_file(scan(tmp), tmp)
        missing = [rel for rel in BUILD_FOLDERS if "hullproof-paddle-api-key" not in found.get(rel, set())]
        self.assertEqual(missing, [])

    def test_public_keys_and_placeholders_do_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            for rel, tpl in NEGATIVE:
                write(tmp, rel, fill(tpl))
            found = by_file(scan(tmp), tmp)
        self.assertEqual(found, {})

    def test_service_role_hidden_behind_anon_variable_name_is_found(self):
        # The old config skipped any line that named the anon key variable.
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "app/a.js", fill('const NEXT_PUBLIC_SUPABASE_ANON_KEY = "{service_role}";'))
            found = by_file(scan(tmp), tmp)
        self.assertIn("hullproof-supabase-service-role-jwt", found.get("app/a.js", set()))


class ConfigControl(unittest.TestCase):
    def test_inline_allow_comment_is_ignored_with_the_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "a.js", fill('var k="{paddle_live}"; // gitleaks:allow\n'))
            found = by_file(scan(tmp, extra=["--ignore-gitleaks-allow"]), tmp)
        self.assertIn("hullproof-paddle-api-key", found.get("a.js", set()))

    def test_repository_own_config_is_not_used_when_config_is_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, ".gitleaks.toml", '[extend]\nuseDefault = false\n[allowlist]\npaths = ["""(^|/)lib/"""]\n')
            write(tmp, "lib/a.js", fill('var k="{paddle_live}";'))
            found = by_file(scan(tmp), tmp)
        self.assertIn("hullproof-paddle-api-key", found.get("lib/a.js", set()))

    def test_history_scan_finds_a_deleted_secret(self):
        if not shutil.which("git"):
            self.skipTest("git not installed")
        with tempfile.TemporaryDirectory() as tmp:
            run = lambda *a: subprocess.run(["git", "-C", tmp, *a], capture_output=True, check=True)
            run("init", "-q")
            run("config", "user.email", "t@example.invalid")
            run("config", "user.name", "t")
            write(tmp, "old.js", fill('var k="{paddle_live}";'))
            run("add", "-A")
            run("commit", "-q", "-m", "add")
            (pathlib.Path(tmp) / "old.js").unlink()
            run("add", "-A")
            run("commit", "-q", "-m", "remove")
            findings = scan(tmp, mode="git")
        self.assertTrue(any(f["RuleID"] == "hullproof-paddle-api-key" for f in findings))

    def test_kit_documents_scan_clean(self):
        if not DOCS.is_dir():
            self.skipTest("kit docs not found next to the tools folder")
        findings = scan(DOCS)
        self.assertEqual([(f["File"], f["RuleID"]) for f in findings], [])


if __name__ == "__main__":
    unittest.main()
