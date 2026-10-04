"""Tests for helpers/enumerate.md: the route enumeration and gate query recipes run against synthetic fixtures.

The shell recipes need bash, find, grep, awk and sed. The SQL recipes run against a throwaway Postgres cluster when the Postgres
server tools are installed, and skip otherwise.
  python3 -m unittest tools/hullproof/tests/test_enumerate.py
"""
import glob
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
DOC = HERE.parent / "helpers" / "enumerate.md"
FIXTURE = HERE / "fixtures" / "enumerate"


def recipe(rid, lang="bash"):
    m = re.search(r"<!-- recipe:" + re.escape(rid) + r" -->\n```" + lang + r"\n(.*?)\n```", DOC.read_text(), re.S)
    assert m, f"recipe {rid} not found"
    return m.group(1)


ENUM_ALL = "enum_all() {\n" + "\n".join(recipe(r) for r in ("enum-app-router", "enum-pages-router", "enum-server-actions", "enum-express")) + "\n}\n"


def run(rid, cwd):
    script = recipe("enum-setup") + "\n" + (ENUM_ALL if rid == "enum-totals" else "") + recipe(rid)
    p = subprocess.run(["bash", "-c", script], cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert p.returncode == 0, p.stderr
    return sorted(p.stdout.splitlines())


class Enumerate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.root = pathlib.Path(cls.tmp) / "repo"
        shutil.copytree(FIXTURE, cls.root)
        # distractors that must never be listed: a dependency folder and a cache folder
        for d in ("node_modules/evil/app/api/evil", ".next/server/app/api/cached"):
            (cls.root / d).mkdir(parents=True)
            (cls.root / d / "route.ts").write_text("export function GET() { return 1 }\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_app_router_lists_monorepo_src_folders_groups_and_reexports(self):
        out = run("enum-app-router", self.root)
        want = sorted([
            "app-route\t./app/api/mcp/route.ts\tPOST",
            "app-route\t./app/api/upload/route.ts\tPOST",
            "app-route\t./apps/web/app/api/auth/[...nextauth]/route.ts\tGET,POST",
            "app-route\t./apps/web/app/api/build/route.ts\tPATCH",
            "app-route\t./apps/web/app/api/empty/route.ts\tnone",
            "app-route\t./apps/web/app/api/items/[id]/route.js\tDELETE",
            "app-route\t./apps/web/app/api/reexport/route.ts\tGET,PUT",
            "app-route\t./apps/web/app/api/users/route.ts\tGET,POST",
            "app-route\t./apps/web/src/app/api/health/route.ts\tGET",
            "edge-gate\t./apps/web/middleware.ts",
        ])
        self.assertEqual(out, want)

    def test_pages_router(self):
        self.assertEqual(run("enum-pages-router", self.root), sorted([
            "pages-api\t./apps/web/pages/api/legacy.ts\tPOST",
            "pages-api\t./apps/web/pages/api/open.js\tany",
            "pages-api\t./packages/api/src/pages/api/hello.js\tDELETE,GET",
        ]))

    def test_server_actions_file_level_and_inline(self):
        self.assertEqual(run("enum-server-actions", self.root), sorted([
            "server-action\t./apps/web/app/actions.ts\tfile-level\t3",
            "server-action\t./apps/web/app/inline.tsx\tinline\t1",
        ]))

    def test_express_counts_registrations_not_map_gets(self):
        self.assertEqual(run("enum-express", self.root), sorted([
            "express\t./services/api/src/routes/users.ts\tDELETE:1,GET:1,POST:1\tmounts=0\tchains=1",
            "express\t./services/api/src/server.ts\tGET:1\tmounts=1\tchains=0",
        ]))

    def test_totals(self):
        self.assertEqual(run("enum-totals", self.root), ["app-route=9", "edge-gate=1", "express=2", "pages-api=3", "server-action=2"])

    def test_recipes_print_no_source_text(self):
        for rid in ("enum-app-router", "enum-pages-router", "enum-server-actions", "enum-express"):
            for line in run(rid, self.root):
                self.assertNotIn("Response", line)
                self.assertNotIn("return", line)

    def test_gate_code_searches(self):
        self.assertEqual(run("code-tools", self.root), ["./app/lib/agent.ts"])
        self.assertEqual(run("code-mcp", self.root), ["./app/api/mcp/route.ts"])
        self.assertEqual(run("code-uploads", self.root), ["./app/api/upload/route.ts"])
        pay = run("code-payments", self.root)
        self.assertIn("./app/lib/billing.ts", pay)
        self.assertIn("./apps/web/package.json", pay)
        fetch = run("code-urlfetch", self.root)
        self.assertIn("./app/lib/fetcher.ts:3", fetch)
        self.assertIn("./app/lib/fetcher.ts:1", fetch)
        self.assertNotIn("./app/lib/fetcher.ts:2", fetch)  # the call with a string literal is not listed as a variable call

    def test_an_empty_folder_prints_nothing(self):
        with tempfile.TemporaryDirectory() as empty:
            for rid in ("enum-app-router", "enum-pages-router", "enum-server-actions", "enum-express", "code-tools", "code-mcp"):
                self.assertEqual(run(rid, empty), [], rid)

    def test_no_dashes_in_the_document(self):
        text = DOC.read_text()
        self.assertNotIn(chr(0x2014), text)
        self.assertNotIn(chr(0x2013), text)


def pg_bin(name):
    found = shutil.which(name)
    if found:
        return found
    for d in sorted(glob.glob("/opt/homebrew/opt/postgresql@*/bin"), reverse=True) + glob.glob("/usr/lib/postgresql/*/bin"):
        if os.path.exists(os.path.join(d, name)):
            return os.path.join(d, name)
    return None


@unittest.skipUnless(pg_bin("initdb") and pg_bin("pg_ctl") and pg_bin("psql"), "needs the Postgres server tools")
class GateSql(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="pg")
        data, cls.sock = os.path.join(cls.tmp, "d"), os.path.join(cls.tmp, "s")
        os.mkdir(cls.sock)
        env = {**os.environ, "LC_ALL": "C"}
        try:
            subprocess.run([pg_bin("initdb"), "-D", data, "-A", "trust", "-U", "test", "-E", "UTF8"], check=True, capture_output=True, env=env, timeout=120)
            subprocess.run([pg_bin("pg_ctl"), "-D", data, "-o", f"-k {cls.sock} -c listen_addresses=''", "-l", os.path.join(cls.tmp, "log"), "start", "-w"],
                           check=True, capture_output=True, env=env, timeout=120)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
            shutil.rmtree(cls.tmp, ignore_errors=True)
            raise unittest.SkipTest(f"could not start a throwaway Postgres: {e}")
        cls.data = data
        cls.psql(["-f", str(FIXTURE / "db/migrations/001_init.sql")])

    @classmethod
    def tearDownClass(cls):
        subprocess.run([pg_bin("pg_ctl"), "-D", cls.data, "stop", "-m", "immediate"], capture_output=True)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def psql(cls, args):
        p = subprocess.run([pg_bin("psql"), "-h", cls.sock, "-U", "test", "-d", "postgres", "-X", "-At", "-v", "ON_ERROR_STOP=1", *args],
                           capture_output=True, text=True, timeout=60)
        assert p.returncode == 0, p.stderr
        return p.stdout.splitlines()

    def queries(self, rid):
        return [q.strip() for q in re.sub(r"(?m)^--.*$", "", recipe(rid, "sql")).split(";") if q.strip()]

    def test_tenant_queries_find_the_sharing_boundaries(self):
        q1, q2, q3 = self.queries("sql-tenants")
        self.assertEqual(self.psql(["-c", q1]), ["memberships|organizations", "projects|organizations"])
        cols = self.psql(["-c", q2])
        self.assertEqual(cols, ["public|memberships|org_id", "public|projects|organization_id"])
        self.assertEqual(self.psql(["-c", q3]), ["public|memberships"])

    def test_payment_queries_find_billing_tables_and_columns(self):
        q1, q2 = self.queries("sql-payments")
        self.assertEqual(self.psql(["-c", q1]), ["public|credits", "public|subscriptions"])
        cols = self.psql(["-c", q2])
        for want in ("public|credits|balance", "public|subscriptions|plan", "public|subscriptions|stripe_customer_id"):
            self.assertIn(want, cols)


if __name__ == "__main__":
    unittest.main()
