"""Tests for the GitHub Copilot files: the hook adapter on fixtures (CLI and VS Code formats), both hook files, TOOL.json and the text files.

  python3 -m unittest tools/hullproof/tests/test_copilot_editor.py
"""
import json
import sys
import unittest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import w3b_util as u  # noqa: E402

FOLDER = u.EDITORS / "copilot"
GH = FOLDER / ".github"
CLI = lambda tool, args: {"sessionId": "s", "timestamp": 1, "cwd": "/p", "toolName": tool, "toolArgs": args}
LOCAL = lambda tool, inp: {"hook_event_name": "PreToolUse", "session_id": "s", "tool_name": tool, "tool_input": inp, "tool_use_id": "t"}


class AdapterAuditOn(unittest.TestCase):
    def allowed(self, payload):
        r = u.run_adapter("copilot", payload)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, ""), r.stderr)  # no output: Copilot keeps its own permission flow

    def denied(self, payload):
        r = u.run_adapter("copilot", payload)
        self.assertEqual(r.returncode, 2, r.stdout)
        out = json.loads(r.stdout.strip())
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertTrue(out["permissionDecisionReason"] and r.stderr.strip())

    def test_read_only_allowed_in_both_formats(self):
        self.allowed(CLI("bash", {"command": "ls docs"}))
        self.allowed(CLI("bash", json.dumps({"command": "ls docs"})))  # toolArgs as a JSON string
        self.allowed(LOCAL("Bash", {"command": "ls docs"}))
        self.allowed(CLI("view", {"path": str(u.KIT / "docs" / "hullproof" / "STANDARD.md")}))
        self.allowed(CLI("grep", {"pattern": "x", "path": "docs"}))
        self.allowed(CLI("ask_user", {"question": "which folder"}))

    def test_writes_denied(self):
        for tool in ("create", "edit", "str_replace_editor", "apply_patch", "Write", "Edit"):
            self.denied(CLI(tool, {"path": "a.txt"}))
        for c in ("rm -rf x", "echo a > b", "touch a", "git commit -m x", "sed -i s/a/b/ f"):
            self.denied(CLI("bash", {"command": c}))

    def test_network_denied(self):
        for c in ("curl https://example.com", "wget http://x/y"):
            self.denied(CLI("bash", {"command": c}))
        self.denied(CLI("web_fetch", {"url": "https://example.com"}))
        self.denied(CLI("web_search", {"query": "x"}))

    def test_unknown_and_other_tools_denied(self):
        for tool in ("powershell", "task", "Agent", "run_in_terminal", "something_new", ""):
            self.denied(CLI(tool, {"command": "ls"}))
        self.denied(LOCAL("run_in_terminal", {"command": "ls"}))  # a Local tool name the adapter does not know

    def test_secret_reads_denied(self):
        self.denied(CLI("view", {"path": str(u.KIT / ".env")}))
        self.denied(LOCAL("Read", {"file_path": str(u.KIT / ".env")}))

    def test_bad_arguments_denied(self):
        self.denied(CLI("bash", {}))
        self.denied(CLI("bash", {"command": 5}))
        self.denied(CLI("bash", "not json"))
        self.denied(CLI("bash", None))
        self.denied(CLI("view", {}))
        self.denied(CLI("grep", {"pattern": "x", "path": 5}))

    def test_malformed_input_denied(self):
        for raw in ("", "not json", "{bad", "[]", "null", "5", '"x"'):
            r = u.run_adapter("copilot", raw)
            self.assertEqual(r.returncode, 2, raw)

    def test_empty_object_is_denied(self):
        self.denied({})


class AdapterAuditOff(unittest.TestCase):
    def test_everything_well_formed_is_allowed(self):
        for p in (CLI("edit", {"path": "a"}), CLI("bash", {"command": "rm -rf x"}), LOCAL("Write", {})):
            r = u.run_adapter("copilot", p, audit=False)
            self.assertEqual((r.returncode, r.stdout), (0, ""), p)

    def test_malformed_input_still_denied(self):
        self.assertEqual(u.run_adapter("copilot", "not json", audit=False).returncode, 2)


class AdapterInstalledTree(unittest.TestCase):
    def test_marker_file_decides(self):
        on = u.installed_tree("copilot", marker=True)
        off = u.installed_tree("copilot", marker=False)
        self.addCleanup(on.cleanup)
        self.addCleanup(off.cleanup)
        self.assertEqual(u.run_adapter("copilot", CLI("bash", {"command": "rm x"}), root=on.name).returncode, 2)
        self.assertEqual(u.run_adapter("copilot", CLI("bash", {"command": "ls"}), root=on.name).returncode, 0)
        self.assertEqual(u.run_adapter("copilot", CLI("bash", {"command": "rm x"}), root=off.name).returncode, 0)

    def test_missing_hook_fails_closed(self):
        td = u.installed_tree("copilot", marker=True, with_hook=False)
        self.addCleanup(td.cleanup)
        r = u.run_adapter("copilot", CLI("bash", {"command": "ls"}), root=td.name)
        self.assertEqual(r.returncode, 2)
        self.assertIn("missing", r.stderr)


class Configs(unittest.TestCase):
    def test_cli_hook_file(self):
        d = json.loads((GH / "hooks" / "hullproof-cli.json").read_text(encoding="utf8"))
        self.assertEqual(d["version"], 1)
        self.assertEqual(set(d), {"version", "hooks"})
        self.assertEqual(set(d["hooks"]), {"preToolUse"})
        for e in d["hooks"]["preToolUse"]:
            self.assertEqual(e["type"], "command")
            self.assertEqual(e["bash"], "node tools/hullproof/hooks/copilot-adapter.mjs")
            self.assertEqual(e["powershell"], e["bash"])
            self.assertLessEqual(e["timeoutSec"], 30)
            self.assertTrue(set(e) <= {"type", "bash", "powershell", "command", "cwd", "env", "timeoutSec", "timeout", "exec", "args"})

    def test_vscode_local_hook_file(self):
        d = json.loads((GH / "hooks" / "hullproof-vscode.json").read_text(encoding="utf8"))
        self.assertEqual(set(d), {"hooks"})
        self.assertEqual(set(d["hooks"]), {"PreToolUse"})
        for e in d["hooks"]["PreToolUse"]:
            self.assertEqual(e["type"], "command")
            self.assertEqual(e["command"], "node tools/hullproof/hooks/copilot-adapter.mjs")
            self.assertTrue(set(e) <= {"type", "command", "windows", "linux", "osx", "cwd", "env", "timeout"})
        self.assertTrue((u.HOOKS / "copilot-adapter.mjs").is_file())

    def test_no_prompt_file(self):
        self.assertFalse((GH / "prompts").exists())  # prompt files are deprecated for Agent Host sessions


class Packaging(unittest.TestCase):
    def test_tool_json(self):
        d = u.check_tool_json(self, "copilot", {"vscode", "cli", "cloud", "desktop"})
        self.assertEqual(d["files"][0]["merge"], "append")
        self.assertIn("audit mode", d["enforcementNote"])

    def test_text_rules(self):
        u.check_text(self, FOLDER)

    def test_instructions_and_ids(self):
        p = GH / "copilot-instructions.md"
        text = p.read_text(encoding="utf8")
        self.assertIn("## Hard rules", text)
        self.assertIn("GitHub Copilot", text)
        self.assertNotIn("Only the Claude Code edition of Hullproof has the read only hook", text)
        u.sec_ids_exist(self, [p])

    def test_skill_and_agent(self):
        skill = GH / "skills" / "hullproof-audit" / "SKILL.md"
        fm = u.frontmatter(skill)
        self.assertEqual(fm["name"], skill.parent.name)
        self.assertRegex(fm["name"], r"^[a-z0-9-]{1,64}$")
        self.assertTrue(0 < len(fm["description"]) <= 1024)
        body = skill.read_text(encoding="utf8")
        self.assertIn("prompts/HULLPROOF-AUDIT-PROMPT.md", body)
        agent = u.frontmatter(GH / "agents" / "hullproof-auditor.agent.md")
        self.assertEqual(agent["tools"], "['read', 'search']")

    def test_readme_sections(self):
        text = (FOLDER / "README.md").read_text(encoding="utf8")
        for h in ("## Surfaces", "## Install", "## First run", "## Trust note", "## What is enforced", "## What it cannot do"):
            self.assertIn(h, text)
        self.assertIn("node tools/hullproof/install.mjs --tool copilot", text)


if __name__ == "__main__":
    unittest.main()
