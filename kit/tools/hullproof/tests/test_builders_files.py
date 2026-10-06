"""Structure and wording tests for the builder and chat editor targets (W4).

  python3 -m unittest kit/tools/hullproof/tests/test_builders_files.py
"""
import json
import pathlib
import re
import unittest

HERE = pathlib.Path(__file__).resolve().parent
EDITORS = HERE.parents[2] / "editors"
TOOLS = ["lovable", "replit", "bolt", "emergent", "v0", "chatgpt", "claude-ai", "gemini-app"]
KEYS = {"tool", "displayName", "surfaces", "files", "enforcement", "enforcementNote", "trustNote", "firstRun", "ways"}
WAYS = {"agent", "rules", "prompt", "install-by-chat"}
FORBIDDEN_WORDS = ["unverified", "unconfirmed"]
PRO_ID = re.compile(r"\bSEC-[A-Z]+-\d+")
CAPS = {
    "lovable/KNOWLEDGE.txt": 10000,
    "chatgpt/PROJECT-INSTRUCTIONS.txt": 1500,
    "replit/replit.md": 16000,
    "lovable/AGENTS.md": 12000,
}


def shipped(tool):
    return sorted(p for p in (EDITORS / tool).rglob("*") if p.is_file())


class Builders(unittest.TestCase):
    def test_tool_json_and_files(self):
        for t in TOOLS:
            with self.subTest(tool=t):
                d = json.loads((EDITORS / t / "TOOL.json").read_text())
                self.assertEqual(set(d), KEYS)
                self.assertEqual(d["tool"], t)
                self.assertEqual(d["enforcement"], "advisory")
                self.assertTrue(d["enforcementNote"] and d["firstRun"])
                self.assertTrue(d["ways"] and set(d["ways"]) <= WAYS)
                self.assertTrue(d["surfaces"] and d["files"])
                self.assertTrue((EDITORS / t / "README.md").is_file())
                for e in d["files"]:
                    self.assertIn(e["merge"], {"never", "append", "json"})
                    self.assertTrue((EDITORS / t / e["src"]).is_file(), e["src"])
                    self.assertFalse(e["dest"].startswith("/"))

    def test_size_caps(self):
        for rel, cap in CAPS.items():
            n = len((EDITORS / rel).read_text())
            self.assertLessEqual(n, cap, rel)

    def test_skill_descriptions(self):
        for rel in ["claude-ai/hullproof/skill.md", "gemini-app/skills/hullproof/SKILL.md", "replit/.agents/skills/hullproof/SKILL.md"]:
            text = (EDITORS / rel).read_text()
            m = re.search(r"^description: (.+)$", text, re.M)
            self.assertTrue(m, rel)
            self.assertLessEqual(len(m.group(1)), 200, rel)
            self.assertRegex(text, r"^---\nname: hullproof\n")

    def test_wording(self):
        for t in TOOLS:
            for p in shipped(t):
                text = p.read_text()
                low = text.lower()
                name = str(p.relative_to(EDITORS))
                self.assertNotIn("—", text, name)
                self.assertNotIn("–", text, name)
                self.assertIsNone(re.search(r"\S - \S", text), name)
                self.assertIsNone(PRO_ID.search(text), name)
                for w in FORBIDDEN_WORDS:
                    self.assertNotIn(w, low, name)

    def test_emergent_wording(self):
        text = "".join(p.read_text().lower() for p in shipped("emergent"))
        self.assertIn("own project", text)
        for w in ["penetration test", "security assessment"]:
            self.assertNotIn(w, text)

    def test_read_only_and_pointer(self):
        for rel in ["lovable/AGENTS.md", "lovable/KNOWLEDGE.txt", "replit/replit.md", "bolt/agents.md",
                    "emergent/PROJECT-INSTRUCTION.txt", "v0/INSTRUCTION.txt", "chatgpt/HULLPROOF-RULES.md",
                    "claude-ai/PROJECT-INSTRUCTIONS.txt", "gemini-app/INSTRUCTIONS.txt"]:
            text = (EDITORS / rel).read_text()
            self.assertIn("HULLPROOF-AUDIT-PROMPT", text, rel)
            self.assertRegex(text, r"read only", rel)
            self.assertRegex(text, r"do not edit project files", rel)

    def test_readme_plain_about_advisory(self):
        for t in TOOLS:
            text = (EDITORS / t / "README.md").read_text()
            self.assertIn("Advisory only", text, t)
            self.assertIn("The limit that matters", text, t)
            self.assertIn("What this does not do", text, t)


if __name__ == "__main__":
    unittest.main()
