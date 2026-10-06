"""Tests for the Cursor files: the hook adapter on fixtures, every config, TOOL.json and the rule files.

  python3 -m unittest tools/hullproof/tests/test_cursor_editor.py
"""
import json
import re
import sys
import unittest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import w3b_util as u  # noqa: E402

FOLDER = u.EDITORS / "cursor"
CURSOR = FOLDER / ".cursor"
HOOK_EVENTS = {"preToolUse", "beforeShellExecution", "beforeReadFile"}
SHELL = lambda c: {"hook_event_name": "preToolUse", "tool_name": "Shell", "tool_input": {"command": c, "working_directory": "/p"}}
TOOL = lambda n, i=None: {"hook_event_name": "preToolUse", "tool_name": n, "tool_input": i if i is not None else {}}


def answer(res):
    return json.loads(res.stdout.strip().splitlines()[0])["permission"]


class AdapterAuditOn(unittest.TestCase):
    def allowed(self, payload):
        r = u.run_adapter("cursor", payload)
        self.assertEqual((r.returncode, answer(r)), (0, "allow"), r.stderr)

    def denied(self, payload):
        r = u.run_adapter("cursor", payload)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertEqual(answer(r), "deny")
        self.assertTrue(r.stderr.strip())

    def test_read_only_command_allowed(self):
        self.allowed(SHELL("ls docs"))
        self.allowed({"hook_event_name": "beforeShellExecution", "command": "ls docs", "cwd": "/p", "sandbox": False})

    def test_write_commands_denied(self):
        for c in ("rm -rf src", "echo x > a.txt", "touch a", "mv a b", "sed -i s/a/b/ f", "git commit -m x", "npm install"):
            self.denied(SHELL(c))

    def test_network_denied(self):
        for c in ("curl https://example.com", "wget http://example.com/x", "nc example.com 80"):
            self.denied(SHELL(c))

    def test_unknown_tools_denied(self):
        for name in ("Write", "Delete", "Task", "MCP:github", "WebSearch", "Whatever", ""):
            self.denied(TOOL(name))

    def test_missing_or_odd_command_denied(self):
        self.denied(TOOL("Shell"))
        self.denied(TOOL("Shell", {"command": 5}))
        self.denied({"hook_event_name": "beforeShellExecution"})

    def test_reads(self):
        self.allowed({"hook_event_name": "beforeReadFile", "file_path": str(u.KIT / "docs" / "hullproof" / "STANDARD.md"), "content": "x", "attachments": []})
        self.denied({"hook_event_name": "beforeReadFile", "file_path": str(u.KIT / ".env"), "content": "SECRET=1"})
        self.denied({"hook_event_name": "beforeReadFile", "content": "x"})
        self.denied(TOOL("Read", {"file_path": str(u.KIT / ".env")}))

    def test_search_tools_go_through_the_hook(self):
        self.allowed(TOOL("Grep", {"pattern": "x", "path": "docs"}))
        self.denied(TOOL("Grep", {"pattern": "x", "path": 5}))
        self.denied(TOOL("Grep", "x"))

    def test_unknown_event_denied(self):
        self.denied({"hook_event_name": "afterFileEdit", "file_path": "a"})
        self.denied({"tool_name": "Shell", "tool_input": {"command": "ls"}})

    def test_malformed_input_denied(self):
        for raw in ("", "not json", "{bad", "[]", "null", "5", '"x"'):
            r = u.run_adapter("cursor", raw)
            self.assertEqual((r.returncode, answer(r)), (2, "deny"), raw)


class AdapterAuditOff(unittest.TestCase):
    def test_everything_well_formed_is_allowed(self):
        for p in (SHELL("rm -rf src"), TOOL("Write"), TOOL("MCP:x"), {"hook_event_name": "beforeReadFile", "file_path": ".env"}):
            r = u.run_adapter("cursor", p, audit=False)
            self.assertEqual((r.returncode, answer(r)), (0, "allow"), p)

    def test_malformed_input_still_denied(self):
        r = u.run_adapter("cursor", "not json", audit=False)
        self.assertEqual((r.returncode, answer(r)), (2, "deny"))


class AdapterInstalledTree(unittest.TestCase):
    def test_marker_file_turns_enforcement_on_and_off(self):
        td = u.installed_tree("cursor", marker=True)
        self.addCleanup(td.cleanup)
        r = u.run_adapter("cursor", SHELL("rm x"), root=td.name)
        self.assertEqual((r.returncode, answer(r)), (2, "deny"))
        r = u.run_adapter("cursor", SHELL("ls"), root=td.name)
        self.assertEqual((r.returncode, answer(r)), (0, "allow"))
        off = u.installed_tree("cursor", marker=False)
        self.addCleanup(off.cleanup)
        r = u.run_adapter("cursor", SHELL("rm x"), root=off.name)
        self.assertEqual((r.returncode, answer(r)), (0, "allow"))

    def test_missing_hook_fails_closed(self):
        td = u.installed_tree("cursor", marker=True, with_hook=False)
        self.addCleanup(td.cleanup)
        r = u.run_adapter("cursor", SHELL("ls"), root=td.name)
        self.assertEqual((r.returncode, answer(r)), (2, "deny"))
        self.assertIn("missing", r.stderr)


class Configs(unittest.TestCase):
    def load(self, rel):
        return json.loads((CURSOR / rel).read_text(encoding="utf8"))

    def test_hooks_json(self):
        d = self.load("hooks.json")
        self.assertEqual(d["version"], 1)
        self.assertEqual(set(d["hooks"]), HOOK_EVENTS)
        for event, entries in d["hooks"].items():
            self.assertTrue(entries)
            for e in entries:
                self.assertIs(e["failClosed"], True, event)
                self.assertIsInstance(e["timeout"], int)
                self.assertLessEqual(e["timeout"], 30)
                self.assertEqual(e["command"], "node tools/hullproof/hooks/cursor-adapter.mjs")
        self.assertTrue((u.HOOKS / "cursor-adapter.mjs").is_file())

    def test_cli_json_files(self):
        token = re.compile(r"^(Shell|Read|Write|WebFetch|Mcp)\(.+\)$")
        for rel in ("cli.json", "hullproof-audit/cli.json"):
            d = self.load(rel)
            self.assertEqual(d["version"], 1)
            self.assertEqual(set(d), {"version", "permissions"})
            self.assertEqual(d["permissions"]["allow"], [])
            self.assertTrue(d["permissions"]["deny"])
            for t in d["permissions"]["deny"]:
                self.assertRegex(t, token)
        strict = self.load("hullproof-audit/cli.json")["permissions"]["deny"]
        for t in ("Write(**)", "Shell(*)"):
            self.assertIn(t, strict)

    def test_sandbox_json(self):
        d = self.load("hullproof-audit/sandbox.json")
        self.assertEqual(d["type"], "workspace_readonly")
        self.assertTrue(set(d) <= {"type", "networkPolicy", "additionalReadonlyPaths", "disableTmpWrite"})

    def test_audit_files_are_not_active_paths(self):
        # shipping workspace_readonly at .cursor/sandbox.json would block every build
        self.assertFalse((CURSOR / "sandbox.json").exists())


class Packaging(unittest.TestCase):
    def test_tool_json(self):
        d = u.check_tool_json(self, "cursor", {"desktop", "cli", "vscode"})
        self.assertIn(d["enforcement"], {"partial", "enforced"})
        self.assertIn("audit mode", d["enforcementNote"])

    def test_text_rules(self):
        u.check_text(self, FOLDER)

    def test_rule_files(self):
        rules = sorted((CURSOR / "rules").glob("*"))
        self.assertEqual(len(rules), 6)
        for p in rules:
            self.assertEqual(p.suffix, ".mdc")
            self.assertLess(len(p.read_text(encoding="utf8").splitlines()), 500)
            fm = u.frontmatter(p)
            self.assertIn(fm["alwaysApply"], ("true", "false"))
        self.assertEqual(u.frontmatter(CURSOR / "rules" / "hullproof.mdc")["alwaysApply"], "true")
        u.sec_ids_exist(self, rules)

    def test_skill_and_agent(self):
        fm = u.frontmatter(CURSOR / "skills" / "hullproof-audit" / "SKILL.md")
        self.assertEqual(fm["name"], "hullproof-audit")
        self.assertRegex(fm["name"], r"^[a-z0-9-]+$")
        self.assertTrue(fm["description"])
        body = (CURSOR / "skills" / "hullproof-audit" / "SKILL.md").read_text(encoding="utf8")
        self.assertIn("prompts/HULLPROOF-AUDIT-PROMPT.md", body)
        agent = u.frontmatter(CURSOR / "agents" / "hullproof-auditor.md")
        self.assertEqual(agent["readonly"], "true")

    def test_readme_sections(self):
        text = (FOLDER / "README.md").read_text(encoding="utf8")
        for h in ("## Surfaces", "## Install", "## First run", "## Trust note", "## What is enforced", "## What it cannot do"):
            self.assertIn(h, text)
        self.assertIn("node tools/hullproof/install.mjs --tool cursor", text)


if __name__ == "__main__":
    unittest.main()
