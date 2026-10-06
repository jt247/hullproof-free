"""Tests for the Claude Code tool page and deny rules file: JSON validity, rule shape, TOOL.json, and the existing hook through the new rules' paths.

  python3 -m unittest tools/hullproof/tests/test_claudecode_editor.py
"""
import json
import re
import sys
import unittest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import w3b_util as u  # noqa: E402

FOLDER = u.EDITORS / "claude-code"
RULE = re.compile(r"^(Read|Edit)\(.+\)$")


class DenyRules(unittest.TestCase):
    def setUp(self):
        self.d = json.loads((FOLDER / ".claude" / "settings.json").read_text(encoding="utf8"))

    def test_shape(self):
        self.assertEqual(set(self.d), {"permissions"})
        self.assertEqual(set(self.d["permissions"]), {"deny"})  # allow rules are not applied before trust, so none are shipped
        deny = self.d["permissions"]["deny"]
        self.assertTrue(deny)
        self.assertEqual(len(deny), len(set(deny)))
        for rule in deny:
            self.assertRegex(rule, RULE)

    def test_documented_path_forms_only(self):
        # Write, NotebookEdit, Glob and MultiEdit path rules are accepted but never consulted, so none may appear
        for rule in self.d["permissions"]["deny"]:
            self.assertNotRegex(rule, r"^(Write|NotebookEdit|Glob|MultiEdit)\(")

    def test_example_env_files_carved_out_after_the_deny(self):
        deny = self.d["permissions"]["deny"]
        for example in (".env.example", ".env.sample", ".env.template"):
            self.assertIn(f"Read(!{example})", deny)
            self.assertGreater(deny.index(f"Read(!{example})"), deny.index("Read(.env.*)"))  # a negation only carves out rules listed before it

    def test_covers_secrets_and_the_hook_files(self):
        deny = " ".join(self.d["permissions"]["deny"])
        for needle in ("Read(.env)", "*.pem", "id_rsa", "~/.ssh", "~/.aws", "/.claude/hooks/", "/.claude/settings.json", "/tools/hullproof/hooks/"):
            self.assertIn(needle, deny)

    def test_no_shell_rules(self):
        self.assertNotRegex(" ".join(self.d["permissions"]["deny"]), r"Bash|PowerShell")  # a Bash deny would stop normal work


class ExistingHookStillBlocksWhatTheRulesName(unittest.TestCase):
    def run_hook(self, tool, inp, profile="skill"):
        import subprocess
        import os
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(u.KIT)}
        return subprocess.run(["node", "--", str(u.HOOK), profile], input=json.dumps({"tool_name": tool, "tool_input": inp}),
                              capture_output=True, text=True, timeout=60, env=env).returncode

    def test_secret_reads_and_hook_writes(self):
        self.assertEqual(self.run_hook("Read", {"file_path": ".env"}), 2)
        self.assertEqual(self.run_hook("Write", {"file_path": ".claude/hooks/hullproof-readonly-bash.mjs", "content": "x"}), 2)
        self.assertEqual(self.run_hook("Write", {"file_path": ".claude/settings.json", "content": "{}"}), 2)
        self.assertEqual(self.run_hook("Read", {"file_path": "docs/hullproof/STANDARD.md"}), 0)


class Packaging(unittest.TestCase):
    def test_tool_json(self):
        d = u.check_tool_json(self, "claude-code", {"desktop", "cli", "vscode", "cloud"})
        self.assertEqual([f["src"] for f in d["files"]], [".claude/settings.json"])
        self.assertEqual(d["files"][0]["merge"], "json")
        self.assertIn(".claude/", d["alsoInstalled"])
        self.assertIn("main kit copy", d["alsoInstalled"])

    def test_nothing_is_copied_from_the_existing_kit(self):
        names = {p.name for p in u.files_under(FOLDER)}
        self.assertEqual(names, {"README.md", "TOOL.json", "settings.json"})

    def test_text_rules(self):
        u.check_text(self, FOLDER)

    def test_readme_sections(self):
        text = (FOLDER / "README.md").read_text(encoding="utf8")
        for h in ("## Surfaces", "## Install", "## First run", "## Trust note", "## What is enforced", "## What it cannot do"):
            self.assertIn(h, text)
        for surface in ("desktop app", "CLI", "VS Code"):
            self.assertIn(surface, text)
        self.assertIn("node tools/hullproof/install.mjs --tool claude-code", text)
        self.assertIn("/hullproof-prelaunch", text)
        self.assertTrue((u.KIT / ".claude" / "skills" / "hullproof-prelaunch" / "SKILL.md").is_file())



if __name__ == "__main__":
    unittest.main()
