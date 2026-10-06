"""Tests for the Hullproof Codex hook adapter. Runs the adapter on sample Codex hook inputs. Standard library only. Needs node.

  python3 -m unittest tools/hullproof/tests/test_codex_adapter.py
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

import w3b_util as u

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE.parents[2]
ADAPTER = KIT / "tools" / "hullproof" / "hooks" / "codex-adapter.mjs"
HOOK = KIT / ".claude" / "hooks" / "hullproof-readonly-bash.mjs"


def run(adapter, raw, audit=True, env_extra=None):
    """Runs the adapter with audit mode on (HULLPROOF_AUDIT=1) unless audit is False. The marker file is looked for in the adapter's own project root."""
    env = {k: v for k, v in os.environ.items() if k != "HULLPROOF_AUDIT"}
    if audit:
        env["HULLPROOF_AUDIT"] = "1"
    env.update(env_extra or {})
    return subprocess.run(["node", str(adapter)], input=raw, capture_output=True, text=True, timeout=60, env=env)


def shell(command):
    return json.dumps({"session_id": "s", "cwd": str(KIT), "hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}})


def other(name):
    return json.dumps({"tool_name": name, "tool_input": {"command": "*** Begin Patch"}})

def allowed(r):
    """Codex: exit 0 with no output allows, exit 2 with a reason on stderr blocks."""
    if r.returncode == 0:
        return r.stdout.strip() == ""
    assert r.returncode == 2 and r.stderr.strip(), (r.returncode, r.stderr)
    return False


class AdapterTests(unittest.TestCase):
    def test_read_only_commands_allowed(self):
        for cmd in ["ls docs", "grep -rn password docs", "git ls-files docs"]:
            with self.subTest(cmd=cmd):
                self.assertTrue(allowed(run(ADAPTER, shell(cmd))), cmd)

    def test_write_network_and_unknown_commands_denied(self):
        for cmd in ["rm -rf docs", "echo hi > a.txt", "curl https://example.com", "npm install left-pad", "frobnicate --now", "git push", "ls docs; rm x"]:
            with self.subTest(cmd=cmd):
                self.assertFalse(allowed(run(ADAPTER, shell(cmd))), cmd)

    def test_other_tools_denied(self):
        for name in ["apply_patch", "Edit", "Write", "mcp__fs__write"]:
            with self.subTest(tool=name):
                self.assertFalse(allowed(run(ADAPTER, other(name))), name)

    def test_malformed_input_denied(self):
        bad = ["", "{bad", "null", "[]", "5", "{}", '{"tool_name": "Bash"}', '{"tool_name": "Bash", "tool_input": {"command": 5}}', '{"tool_name": "Bash", "tool_input": null}']
        for raw in bad:
            with self.subTest(raw=raw[:40]):
                self.assertFalse(allowed(run(ADAPTER, raw)), raw[:40])

    def _installed(self, hook_text):
        tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "tools" / "hullproof" / "hooks").mkdir(parents=True)
        shutil.copy(ADAPTER, tmp / "tools" / "hullproof" / "hooks" / ADAPTER.name)
        if hook_text is not None:
            (tmp / ".claude" / "hooks").mkdir(parents=True)
            (tmp / ".claude" / "hooks" / HOOK.name).write_text(hook_text)
        return tmp / "tools" / "hullproof" / "hooks" / ADAPTER.name

    def test_missing_hook_denies(self):
        self.assertFalse(allowed(run(self._installed(None), shell("ls docs"))))

    def test_crashing_hook_denies(self):
        self.assertFalse(allowed(run(self._installed("process.exit(1);"), shell("ls docs"))))
        self.assertFalse(allowed(run(self._installed("throw new Error('x');"), shell("ls docs"))))

    def test_adapter_answer_follows_the_hook(self):
        self.assertTrue(allowed(run(self._installed("process.exit(0);"), shell("rm -rf /"))))
        self.assertFalse(allowed(run(self._installed("process.stderr.write('no');process.exit(2);"), shell("ls docs"))))


PROTECTED_EDIT = '{"tool_name": "Edit", "tool_input": {"file_path": "tools/hullproof/hooks/codex-adapter.mjs"}}'
PLAIN_WRITE = '{"tool_name": "Write", "tool_input": {"file_path": "src/a.ts", "content": "x"}}'
BAD_COMMAND = '{"tool_name": "Bash", "tool_input": {"command": 5}}'


class AuditModeTests(unittest.TestCase):
    def test_audit_off_allows_normal_work(self):
        for raw in [shell("npm install left-pad"), shell("rm -rf build"), shell("echo hi > a.txt"), shell("curl https://example.com"), shell("cat .env.example"), PLAIN_WRITE, other("apply_patch")]:
            with self.subTest(raw=raw[:60]):
                self.assertTrue(allowed(run(ADAPTER, raw, audit=False)), raw[:60])

    def test_audit_off_still_denies_always_on_list(self):
        for cmd in ["cat .env", "grep KEY .env.local", "head -n1 config/.env.production", "cat server.pem", "cat ~/.ssh/id_rsa", "sed -i s/a/b/ .claude/hooks/hullproof-readonly-bash.mjs", "rm tools/hullproof/hooks/codex-adapter.mjs", "echo x > .claude/settings.json"]:
            with self.subTest(cmd=cmd):
                self.assertFalse(allowed(run(ADAPTER, shell(cmd), audit=False)), cmd)
        self.assertFalse(allowed(run(ADAPTER, PROTECTED_EDIT, audit=False)))

    def test_audit_off_still_denies_malformed_input(self):
        for raw in ["", "{bad", "null", "[]", "{}", BAD_COMMAND]:
            with self.subTest(raw=raw[:40]):
                self.assertFalse(allowed(run(ADAPTER, raw, audit=False)), raw[:40])

    def test_audit_on_denies_write_network_and_unknown(self):
        for raw in [shell("rm -rf docs"), shell("curl https://example.com"), shell("frobnicate --now"), PLAIN_WRITE, other("mcp__fs__write")]:
            with self.subTest(raw=raw[:60]):
                self.assertFalse(allowed(run(ADAPTER, raw, audit=True)), raw[:60])

    def test_audit_on_allows_read_only(self):
        for cmd in ["ls docs", "grep -rn password docs"]:
            self.assertTrue(allowed(run(ADAPTER, shell(cmd), audit=True)), cmd)

    def test_audit_on_denies_malformed_input(self):
        for raw in ["", "{bad", "null", "{}", BAD_COMMAND]:
            self.assertFalse(allowed(run(ADAPTER, raw, audit=True)), raw[:40])

    def test_marker_file_switches_audit_mode(self):
        td = u.installed_tree("codex", marker=False)
        self.addCleanup(td.cleanup)
        self.assertTrue(allowed(run(pathlib.Path(td.name) / "tools/hullproof/hooks/codex-adapter.mjs", shell("rm -rf build"), audit=False)))
        marker = pathlib.Path(td.name) / "docs/security/.audit-mode"
        marker.write_text("on\n", encoding="utf8")
        self.assertFalse(allowed(run(pathlib.Path(td.name) / "tools/hullproof/hooks/codex-adapter.mjs", shell("rm -rf build"), audit=False)))
        self.assertTrue(allowed(run(pathlib.Path(td.name) / "tools/hullproof/hooks/codex-adapter.mjs", shell("ls docs"), audit=False)))
        marker.unlink()
        self.assertTrue(allowed(run(pathlib.Path(td.name) / "tools/hullproof/hooks/codex-adapter.mjs", shell("rm -rf build"), audit=False)))

    def test_active_config_is_not_read_only(self):
        ed = KIT / "editors" / "codex" / ".codex"
        self.assertFalse((ed / "config.toml").exists())
        self.assertIn('sandbox_mode = "read-only"', (ed / "hullproof-audit.config.toml").read_text(encoding="utf8"))
        tool = json.loads((KIT / "editors" / "codex" / "TOOL.json").read_text(encoding="utf8"))
        self.assertNotIn(".codex/config.toml", [f["dest"] for f in tool["files"]])


if __name__ == "__main__":
    unittest.main()
