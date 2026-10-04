"""Checks that every command the skills run for report provenance is allowed by the read only hook (auditor profile).

The commands are the lines under the <!-- hookcmd --> marker in helpers/recipes.md. Skips when node is missing.
  python3 -m unittest tools/hullproof/tests/test_provenance.py
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
KIT = HERE.parents[2]
HOOK = KIT / ".claude" / "hooks" / "hullproof-readonly-bash.mjs"
RECIPES = HERE.parent / "helpers" / "recipes.md"


def hook_commands():
    m = re.search(r"<!-- hookcmd -->\n```\n(.*?)\n```", RECIPES.read_text(), re.S)
    assert m, "hookcmd block not found in recipes.md"
    return m.group(1).splitlines()


def run_hook(command, profile="auditor"):
    with tempfile.TemporaryDirectory() as tmp:
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
        env = {**os.environ, "CLAUDE_PROJECT_DIR": tmp}
        return subprocess.run(["node", "--", str(HOOK), profile], input=payload, capture_output=True, text=True, env=env, timeout=30)


@unittest.skipUnless(shutil.which("node") and HOOK.exists(), "needs node and the hook")
class ProvenanceCommands(unittest.TestCase):
    def test_every_recipe_command_is_allowed(self):
        cmds = hook_commands()
        self.assertGreaterEqual(len(cmds), 5)
        for c in cmds:
            r = run_hook(c)
            self.assertEqual(r.returncode, 0, f"{c}\n{r.stderr}")

    def test_commands_that_need_the_owner_are_blocked(self):
        for c in ("git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", "git for-each-ref refs/remotes/origin/pr",
                  "shasum -a 256 docs/security/evidence/2026-01-31/semgrep.json", "git cat-file -p HEAD"):
            self.assertEqual(run_hook(c).returncode, 2, c)

    def test_the_skill_profile_allows_the_same_commands(self):
        for c in hook_commands():
            self.assertEqual(run_hook(c, "skill").returncode, 0, c)


if __name__ == "__main__":
    unittest.main()
