"""Shared helpers for the editor tests (Cursor, Windsurf and Devin, Copilot, Claude Code). Standard library only.

Not a test module. The test_*_editor.py files import it from this folder.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE.parents[2]
HOOKS = KIT / "tools" / "hullproof" / "hooks"
HOOK = KIT / ".claude" / "hooks" / "hullproof-readonly-bash.mjs"
EDITORS = KIT / "editors"
ENFORCEMENT = {"enforced", "partial", "advisory"}
MERGE = {"never", "append", "json"}
WAYS = {"agent", "rules", "prompt", "install-by-chat"}
BAD_DASHES = ("—", "–")
BANNED_WORDS = re.compile(r"\bunverified\b|\bunconfirmed\b", re.I)
SKIP_NAMES = {"README.md", "TOOL.json"}


def run_adapter(name, payload, audit=True, root=None, env_extra=None):
    """Run an adapter with payload (str or JSON able) on stdin. Returns CompletedProcess.

    root None runs the adapter inside the kit with HULLPROOF_AUDIT set to 1 (audit) or unset (off).
    A root path runs the copy of the adapter that lives in that installed tree, so the marker file decides.
    """
    script = (pathlib.Path(root) / "tools" / "hullproof" / "hooks" if root else HOOKS) / f"{name}-adapter.mjs"
    env = {k: v for k, v in os.environ.items() if k not in ("HULLPROOF_AUDIT", "CLAUDE_PROJECT_DIR")}
    if root is None and audit:
        env["HULLPROOF_AUDIT"] = "1"
    env.update(env_extra or {})
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(["node", "--", str(script)], input=text, capture_output=True, text=True, timeout=60, env=env)


def installed_tree(name, marker=True, with_hook=True):
    """Build a temp project that looks like an installed kit. Returns the TemporaryDirectory."""
    td = tempfile.TemporaryDirectory()
    root = pathlib.Path(td.name)
    (root / "tools" / "hullproof" / "hooks").mkdir(parents=True)
    shutil.copy(HOOKS / f"{name}-adapter.mjs", root / "tools" / "hullproof" / "hooks")
    if with_hook:
        (root / ".claude" / "hooks").mkdir(parents=True)
        shutil.copy(HOOK, root / ".claude" / "hooks")
    (root / "docs" / "security").mkdir(parents=True)
    (root / "README.md").write_text("# demo\n", encoding="utf8")
    if marker:
        (root / "docs" / "security" / ".audit-mode").write_text("on\n", encoding="utf8")
    return td


def files_under(folder):
    return sorted(p for p in pathlib.Path(folder).rglob("*") if p.is_file())


def check_tool_json(tc, tool, surfaces_allowed, expect_files=None):
    """Schema and completeness checks for kit/editors/<tool>/TOOL.json. tc is a unittest.TestCase."""
    folder = EDITORS / tool
    data = json.loads((folder / "TOOL.json").read_text(encoding="utf8"))
    for key in ("tool", "displayName", "surfaces", "files", "enforcement", "enforcementNote", "trustNote", "firstRun", "ways"):
        tc.assertIn(key, data, key)
    tc.assertEqual(data["tool"], tool)
    tc.assertIn(data["enforcement"], ENFORCEMENT)
    tc.assertTrue(set(data["surfaces"]) <= surfaces_allowed and data["surfaces"])
    tc.assertTrue(set(data["ways"]) <= WAYS and data["ways"])
    for key in ("displayName", "enforcementNote", "trustNote", "firstRun"):
        tc.assertIsInstance(data[key], str)
        tc.assertTrue(data[key].strip(), key)
    tc.assertNotIn("\n", data["enforcementNote"])
    srcs = []
    kit_files = []
    for f in data["files"]:
        tc.assertTrue({"src", "dest", "merge"} <= set(f) <= {"src", "dest", "merge", "from"})
        tc.assertIn(f["merge"], MERGE)
        tc.assertFalse(f["src"].startswith(("/", "..")) or ".." in f["src"].split("/"))
        if f.get("from") == "kit":
            # a file outside the tool folder (hook script or adapter), copied as is and never overwritten
            tc.assertEqual(f["merge"], "never")
            tc.assertEqual(f["src"], f["dest"])
            tc.assertTrue((KIT / f["src"]).is_file(), f"missing kit file {f['src']}")
            kit_files.append(f["src"])
            continue
        tc.assertNotIn("from", f)
        tc.assertEqual(f["src"], f["dest"])
        tc.assertTrue((folder / f["src"]).is_file(), f"missing {f['src']}")
        srcs.append(f["src"])
        # a JSON settings file the user may already own must be merged, never replaced
        if f["src"].endswith(("settings.json", "hooks.json", "hooks.v1.json", "cli.json", "config.json")) and "hullproof-audit" not in f["src"] \
                and not f["src"].startswith(".github/hooks/"):
            tc.assertEqual(f["merge"], "json", f["src"])
    tc.assertEqual(len(srcs), len(set(srcs)))
    on_disk = {str(p.relative_to(folder)) for p in files_under(folder) if p.name not in SKIP_NAMES}
    tc.assertEqual(set(srcs), on_disk if expect_files is None else set(expect_files))
    tc.assertEqual(len(kit_files), len(set(kit_files)))
    if kit_files:
        tc.assertIn(".claude/hooks/hullproof-readonly-bash.mjs", kit_files)
        tc.assertTrue(any(k.startswith("tools/hullproof/hooks/") and k.endswith("-adapter.mjs") for k in kit_files))
    return data


def check_text(tc, folder):
    """Writing rules for every shipped text file: no em or en dashes, no spaced hyphen, no hedging labels."""
    for p in files_under(folder):
        if p.suffix not in (".md", ".mdc", ".json"):
            continue
        text = p.read_text(encoding="utf8")
        rel = p.relative_to(folder)
        for d in BAD_DASHES:
            tc.assertNotIn(d, text, f"{rel} has a dash")
        tc.assertNotRegex(text, r"(?<=\w) - (?=\w)", f"{rel} has a spaced hyphen")
        tc.assertIsNone(BANNED_WORDS.search(text), f"{rel} hedges a claim")


def frontmatter(path):
    text = pathlib.Path(path).read_text(encoding="utf8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path} has no frontmatter"
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        if v.strip() or not line.startswith(" "):
            out[k.strip()] = v.strip()
    return out


def sec_ids_exist(tc, paths):
    """Every requirement ID cited in the rule files exists in docs/hullproof."""
    docs = "\n".join(p.read_text(encoding="utf8") for p in (KIT / "docs" / "hullproof").glob("*.md"))
    for p in paths:
        for rid in set(re.findall(r"SEC-[A-Z]+-\d+", pathlib.Path(p).read_text(encoding="utf8"))):
            tc.assertIn(rid, docs, f"{rid} cited in {p} is not in docs/hullproof")
