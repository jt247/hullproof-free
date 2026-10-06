"""Tests for the Windsurf and Devin files: the hook adapter on fixtures (Cascade and Devin formats), every config, TOOL.json and the rules.

  python3 -m unittest tools/hullproof/tests/test_windsurf_editor.py
"""
import json
import re
import sys
import unittest

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import w3b_util as u  # noqa: E402

FOLDER = u.EDITORS / "windsurf"
DEVIN = FOLDER / ".devin"
CASCADE_EVENTS = {"pre_read_code", "post_read_code", "pre_write_code", "post_write_code", "pre_run_command", "post_run_command",
                  "pre_mcp_tool_use", "post_mcp_tool_use", "pre_user_prompt", "post_cascade_response",
                  "post_cascade_response_with_transcript", "post_setup_worktree"}
DEVIN_EVENTS = {"PreToolUse", "PostToolUse", "PermissionRequest", "UserPromptSubmit", "Stop", "PostCompaction", "SessionStart", "SessionEnd"}
CAS = lambda ev, **info: {"agent_action_name": ev, "trajectory_id": "t", "execution_id": "e", "tool_info": info}
DEV = lambda tool, inp=None: {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp if inp is not None else {}, "session_id": "s"}


class AdapterAuditOn(unittest.TestCase):
    def allowed(self, payload):
        r = u.run_adapter("windsurf", payload)
        self.assertEqual(r.returncode, 0, r.stderr)

    def denied(self, payload):
        r = u.run_adapter("windsurf", payload)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertTrue(r.stderr.strip())
        return r

    def test_cascade_read_only_allowed(self):
        self.allowed(CAS("pre_run_command", command_line="ls docs", cwd="/p"))
        self.allowed(CAS("pre_read_code", file_path=str(u.KIT / "docs" / "hullproof" / "STANDARD.md")))

    def test_cascade_writes_network_and_unknown_denied(self):
        self.denied(CAS("pre_write_code", file_path="/p/a.py", edits=[{"old_string": "a", "new_string": "b"}]))
        self.denied(CAS("pre_mcp_tool_use", mcp_server_name="github", mcp_tool_name="create_issue", mcp_tool_arguments={}))
        for c in ("rm -rf x", "curl https://example.com", "wget http://x/y", "npm install p", "echo a > b"):
            self.denied(CAS("pre_run_command", command_line=c))
        self.denied(CAS("pre_run_command"))
        self.denied(CAS("pre_run_command", command_line=5))
        self.denied(CAS("pre_read_code", file_path=str(u.KIT / ".env")))
        self.denied(CAS("pre_read_code"))
        self.denied(CAS("post_run_command", command_line="ls"))
        self.denied({"agent_action_name": "pre_run_command", "tool_info": "x"})

    def test_devin_read_only_allowed(self):
        self.allowed(DEV("exec", {"command": "ls docs"}))
        self.allowed(DEV("read", {"file_path": str(u.KIT / "docs" / "hullproof" / "STANDARD.md")}))
        self.allowed(DEV("grep", {"pattern": "x", "path": "docs"}))
        for tool in ("skill", "todo_write", "get_output", "exit_plan_mode"):
            self.allowed(DEV(tool))

    def test_devin_writes_network_and_unknown_denied(self):
        for c in ("rm -rf x", "curl https://example.com", "git push", "touch a"):
            r = self.denied(DEV("exec", {"command": c}))
            self.assertEqual(json.loads(r.stdout.strip().splitlines()[0])["decision"], "block")
        for tool in ("edit", "write", "apply_patch", "notebook_edit", "webfetch", "run_subagent", "write_to_process", "kill_shell",
                     "mcp__github__create_issue", "mcp_call_tool", "request_scope", ""):
            self.denied(DEV(tool))
        self.denied(DEV("exec"))
        self.denied(DEV("exec", {"command": ["ls"]}))
        self.denied(DEV("read", {"file_path": str(u.KIT / ".env")}))
        self.denied(DEV("read"))
        self.denied({"hook_event_name": "PostToolUse", "tool_name": "exec", "tool_input": {"command": "ls"}})

    def test_malformed_input_denied(self):
        for raw in ("", "not json", "{bad", "[]", "null", "5", '"x"', "{}"):
            self.denied(raw)


class AdapterAuditOff(unittest.TestCase):
    def test_everything_well_formed_is_allowed(self):
        for p in (CAS("pre_write_code", file_path="a"), CAS("pre_run_command", command_line="rm -rf x"), DEV("edit"), DEV("exec", {"command": "curl x"})):
            r = u.run_adapter("windsurf", p, audit=False)
            self.assertEqual(r.returncode, 0, p)

    def test_malformed_input_still_denied(self):
        self.assertEqual(u.run_adapter("windsurf", "not json", audit=False).returncode, 2)


class AdapterInstalledTree(unittest.TestCase):
    def test_marker_file_decides(self):
        on = u.installed_tree("windsurf", marker=True)
        off = u.installed_tree("windsurf", marker=False)
        self.addCleanup(on.cleanup)
        self.addCleanup(off.cleanup)
        self.assertEqual(u.run_adapter("windsurf", DEV("exec", {"command": "rm x"}), root=on.name).returncode, 2)
        self.assertEqual(u.run_adapter("windsurf", DEV("exec", {"command": "ls"}), root=on.name).returncode, 0)
        self.assertEqual(u.run_adapter("windsurf", DEV("exec", {"command": "rm x"}), root=off.name).returncode, 0)

    def test_missing_hook_fails_closed(self):
        td = u.installed_tree("windsurf", marker=True, with_hook=False)
        self.addCleanup(td.cleanup)
        r = u.run_adapter("windsurf", CAS("pre_run_command", command_line="ls"), root=td.name)
        self.assertEqual(r.returncode, 2)
        self.assertIn("missing", r.stderr)


class Configs(unittest.TestCase):
    def load(self, rel):
        return json.loads((DEVIN / rel).read_text(encoding="utf8"))

    def test_cascade_hooks_json(self):
        d = self.load("hooks.json")
        self.assertEqual(set(d), {"hooks"})
        self.assertEqual(set(d["hooks"]), {"pre_read_code", "pre_write_code", "pre_run_command", "pre_mcp_tool_use"})
        self.assertLessEqual(set(d["hooks"]), CASCADE_EVENTS)
        for entries in d["hooks"].values():
            for e in entries:
                self.assertEqual(e["command"], "node tools/hullproof/hooks/windsurf-adapter.mjs || exit 2")
                self.assertTrue(set(e) <= {"command", "powershell", "show_output", "working_directory"})

    def test_devin_hooks_v1_json(self):
        d = self.load("hooks.v1.json")
        self.assertEqual(set(d), {"PreToolUse"})
        self.assertLessEqual(set(d), DEVIN_EVENTS)
        for group in d["PreToolUse"]:
            self.assertIsInstance(group["matcher"], str)
            re.compile(group["matcher"])
            for h in group["hooks"]:
                self.assertEqual(h["type"], "command")
                self.assertIn("tools/hullproof/hooks/windsurf-adapter.mjs", h["command"])
                self.assertTrue(h["command"].endswith("|| exit 2"))
        self.assertTrue((u.HOOKS / "windsurf-adapter.mjs").is_file())

    def test_permission_files(self):
        token = re.compile(r"^((Read|Write|Exec|Fetch)\(.+\)|read|edit|grep|glob|exec|mcp__.+)$")
        project = self.load("config.json")
        self.assertTrue(set(project) <= {"permissions", "read_config_from", "hooks"})  # the only keys a project file may hold
        for d in (project, self.load("hullproof-audit.config.json")):
            self.assertEqual(set(d), {"permissions"})
            self.assertTrue(set(d["permissions"]) <= {"allow", "deny", "ask"})
            self.assertTrue(d["permissions"]["deny"])
            for t in d["permissions"]["deny"]:
                self.assertRegex(t, token)
        self.assertEqual(self.load("hullproof-audit.config.json")["permissions"]["deny"], ["edit", "exec", "mcp__*"])

    def test_audit_profile_is_not_the_project_config(self):
        denied = " ".join(self.load("config.json")["permissions"]["deny"])
        self.assertNotIn("exec", denied.replace("Exec(", ""))  # always on config must not remove the exec or edit tools
        self.assertNotIn("edit", denied)


class Packaging(unittest.TestCase):
    def test_tool_json(self):
        d = u.check_tool_json(self, "windsurf", {"desktop", "cli", "jetbrains", "vscode"})
        self.assertIn("audit mode", d["enforcementNote"])

    def test_text_rules(self):
        u.check_text(self, FOLDER)

    def test_rule_files(self):
        a = sorted((FOLDER / ".windsurf" / "rules").glob("*.md"))
        b = sorted((DEVIN / "rules").glob("*.md"))
        self.assertEqual([p.name for p in a], [p.name for p in b])
        self.assertEqual(len(a), 6)
        for x, y in zip(a, b):
            text = x.read_text(encoding="utf8")
            self.assertEqual(text, y.read_text(encoding="utf8"))
            self.assertLessEqual(len(text), 12000)
            fm = u.frontmatter(x)
            self.assertIn(fm["trigger"], ("always_on", "glob"))
            if fm["trigger"] == "glob":
                self.assertTrue(fm["globs"])
        self.assertEqual(u.frontmatter(FOLDER / ".devin" / "rules" / "hullproof.md")["trigger"], "always_on")
        u.sec_ids_exist(self, a)

    def test_skill_and_agent(self):
        skill = DEVIN / "skills" / "hullproof-audit" / "SKILL.md"
        fm = u.frontmatter(skill)
        self.assertEqual(fm["name"], "hullproof-audit")
        self.assertTrue(fm["description"])
        body = skill.read_text(encoding="utf8")
        self.assertIn("prompts/HULLPROOF-AUDIT-PROMPT.md", body)
        agent = (DEVIN / "agents" / "hullproof-auditor.md").read_text(encoding="utf8")
        self.assertIn("allowed-tools:\n  - read\n  - grep\n  - glob\n", agent)
        for forbidden in ("  - edit", "  - exec", "  - write"):
            self.assertNotIn(forbidden, agent)

    def test_readme_sections(self):
        text = (FOLDER / "README.md").read_text(encoding="utf8")
        for h in ("## Surfaces", "## Install", "## First run", "## Trust note", "## What is enforced", "## What it cannot do"):
            self.assertIn(h, text)
        self.assertIn("node tools/hullproof/install.mjs --tool windsurf", text)
        self.assertIn("Restricted Mode", text)


if __name__ == "__main__":
    unittest.main()
