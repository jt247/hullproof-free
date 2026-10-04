"""Tests for the helper scripts: the lockfile recipes in recipes.md and run_rules.sh.

  python3 -m unittest tools/hullproof/tests/test_helpers.py
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
HELPERS = HERE.parent / "helpers"
LOCKS = HERE / "lockfiles"


def recipe(rid, name):
    """Return the bash block that follows <!-- recipe:ID --> in recipes.md, with NAME set."""
    text = (HELPERS / "recipes.md").read_text()
    m = re.search(r"<!-- recipe:" + re.escape(rid) + r" -->\n```bash\n(.*?)\n```", text, re.S)
    assert m, f"recipe {rid} not found"
    return re.sub(r"(?m)^NAME=\S+$", f"NAME={name}", m.group(1), count=1)


def run_bash(script, cwd):
    return subprocess.run(["bash", "-c", script], cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)


class LockfileRecipes(unittest.TestCase):
    def need(self, *tools):
        for t in tools:
            if not shutil.which(t):
                self.skipTest(f"{t} not installed")

    def test_pnpm_dev_only_chain(self):
        out = run_bash(recipe("pnpm-who", "ms"), LOCKS).stdout
        self.assertIn("RESULT dev only", out)
        self.assertIn(". (devDependencies)", out)

    def test_pnpm_runtime_chain_through_scoped_and_peer_suffix_keys(self):
        out = run_bash(recipe("pnpm-who", "nanoid"), LOCKS).stdout
        self.assertIn("RESULT runtime", out)
        self.assertIn("apps/web (dependencies)", out)

    def test_pnpm_direct_dev_dependency(self):
        out = run_bash(recipe("pnpm-who", "vitest"), LOCKS).stdout
        self.assertIn("RESULT dev only", out)

    def test_pnpm_unknown_package(self):
        out = run_bash(recipe("pnpm-who", "does-not-exist"), LOCKS).stdout
        self.assertIn("RESULT not reachable", out)

    def test_npm_marks_dev_only_packages(self):
        self.need("jq")
        dev = run_bash(recipe("npm-who", "ms"), LOCKS).stdout
        self.assertIn("node_modules/ms dev=true", dev)
        self.assertIn("depended on by: node_modules/debug", dev)
        rt = run_bash(recipe("npm-who", "nanoid"), LOCKS).stdout
        self.assertIn("node_modules/nanoid dev=false", rt)

    def test_yarn_lists_manifest_fields_that_reach_the_package(self):
        self.need("jq")
        dev = run_bash(recipe("yarn-who", "ms"), LOCKS).stdout
        self.assertIn("devDependencies vitest", dev)
        self.assertNotIn(" dependencies ", dev)
        rt = run_bash(recipe("yarn-who", "nanoid"), LOCKS).stdout
        self.assertIn("package.json dependencies next", rt)

    def test_package_json_fields(self):
        self.need("jq")
        out = run_bash(recipe("package-json-fields", "vitest"), LOCKS).stdout
        self.assertEqual(out.split(), ["package.json", "devDependencies"])


class RunRules(unittest.TestCase):
    def setUp(self):
        for t in ("semgrep", "jq", "git"):
            if not shutil.which(t):
                self.skipTest(f"{t} not installed")

    def make_repo(self, tmp):
        repo = pathlib.Path(tmp) / "repo"
        (repo / "tests").mkdir(parents=True)
        (repo / "app").mkdir()
        # a distinctive marker string, to prove matched text is never printed
        (repo / "app" / "a.ts").write_text(
            "declare const pool: any;\nexport const f = (n: string) => pool.query(`SELECT 1 /* MARKER_TEXT_9 */ WHERE a = '${n}'`);\n")
        # hidden three ways: a tests folder, a semgrepignore entry and a nosemgrep comment
        (repo / "tests" / "b.ts").write_text("declare const pool: any;\nexport const g = (n: string) => pool.query(`SELECT 2 WHERE a = '${n}'`);\n")
        (repo / "app" / "c.ts").write_text("declare const pool: any;\nexport const h = (n: string) => pool.query(`SELECT 3 WHERE a = '${n}'`); // nosemgrep\n")
        (repo / ".semgrepignore").write_text("app/c.ts\n")
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        return repo

    def test_counts_only_nothing_hidden_and_temp_folder_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(tmp)
            tmpdir = pathlib.Path(tmp) / "scratch"
            tmpdir.mkdir()
            env = dict(os.environ, TMPDIR=str(tmpdir))
            locs = pathlib.Path(tmp) / "locs.json"
            proc = subprocess.run([str(HELPERS / "run_rules.sh"), str(repo), str(locs)], capture_output=True, text=True, env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("MARKER_TEXT_9", proc.stdout + proc.stderr)
            self.assertNotIn("SELECT", proc.stdout)
            self.assertIn("SEC-API-017", proc.stdout)
            self.assertEqual([x.name for x in tmpdir.iterdir() if x.name.startswith("tmp.")], [], "private temp folder was not removed")
            found = json.loads(locs.read_text())
            files = sorted({f["file"] for f in found if f["rule"] == "hullproof-raw-sql-concat"})
            # the tests folder, the semgrepignore entry and the nosemgrep comment must not hide anything
            self.assertEqual(files, ["app/a.ts", "app/c.ts", "tests/b.ts"])
            self.assertNotIn("MARKER_TEXT_9", locs.read_text())


if __name__ == "__main__":
    unittest.main()
