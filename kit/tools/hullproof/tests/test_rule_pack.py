"""Checks on the rule pack itself: metadata, real SEC IDs, and the template file rules.

  python3 -m unittest tools/hullproof/tests/test_rule_pack.py
"""
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
RULES = HERE.parent / "rules"
DOCS = HERE.parents[2] / "docs" / "hullproof"
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


def rule_blocks():
    """Yield (file, rule id, text) for each rule in the pack. Plain text parse, no YAML library needed."""
    for f in sorted(RULES.glob("*.yaml")):
        text = f.read_text()
        parts = re.split(r"(?m)^  - id: ", text)[1:]
        for part in parts:
            yield f.name, part.splitlines()[0].strip(), part


class RuleMetadata(unittest.TestCase):
    def test_every_rule_has_sec_ids_severity_and_confidence(self):
        problems = []
        for fname, rid, block in rule_blocks():
            m = re.search(r"sec_ids:\s*\[([^\]]*)\]", block)
            ids = [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []
            if not ids:
                problems.append(f"{rid}: no sec_ids")
            sev = re.search(r"severity_hint:\s*(\w+)", block)
            if not sev or sev.group(1) not in SEVERITIES:
                problems.append(f"{rid}: bad severity_hint")
            conf = re.search(r"\n\s+confidence:\s*(\w+)", block)
            if not conf or conf.group(1) not in CONFIDENCE:
                problems.append(f"{rid}: bad confidence")
        self.assertEqual(problems, [])

    def test_rule_ids_are_unique_and_prefixed(self):
        ids = [rid for _, rid, _ in rule_blocks()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i.startswith("hullproof-") for i in ids))

    def test_sec_ids_exist_in_the_kit_docs(self):
        if not DOCS.is_dir():
            self.skipTest("kit docs not found next to the tools folder")
        known = set()
        for md in DOCS.glob("*.md"):
            text = md.read_text()
            if "**Free edition.**" in text:
                self.skipTest("free edition docs hold only part of the requirements, run this check in the full kit")
            known.update(re.findall(r"(?m)^### (SEC-[A-Z]+-\d+):", text))
        self.assertGreater(len(known), 100)
        missing = []
        for _, rid, block in rule_blocks():
            m = re.search(r"sec_ids:\s*\[([^\]]*)\]", block)
            for sid in [x.strip() for x in m.group(1).split(",") if x.strip()]:
                if sid not in known:
                    missing.append(f"{rid}: {sid}")
        self.assertEqual(missing, [])


TEMPLATE_CASES = {
    "page.hbs": ("<div>{{{body}}}</div>\n<p>{{name}}</p>\n", "hullproof-handlebars-unescaped", 1),
    "ok.hbs": ("<div>{{body}}</div>\n", "hullproof-handlebars-unescaped", 0),
    "page.j2": ("<p>{{ body | safe }}</p>\n{% autoescape false %}\n<p>{{ name }}</p>\n", "hullproof-jinja-unescaped", 2),
    "ok.j2": ("<p>{{ name }}</p>\n", "hullproof-jinja-unescaped", 0),
    "page.ejs": ("<p><%- body %></p>\n<p><%= name %></p>\n", "hullproof-ejs-pug-unescaped", 1),
    "ok.ejs": ("<p><%= name %></p>\n", "hullproof-ejs-pug-unescaped", 0),
    "page.pug": ("p\n  != body\ndiv !{raw}\n", "hullproof-ejs-pug-unescaped", 2),
    "ok.pug": ("p= body\n", "hullproof-ejs-pug-unescaped", 0),
}


class TemplateRules(unittest.TestCase):
    def test_template_engine_rules(self):
        if not shutil.which("semgrep"):
            self.skipTest("semgrep not installed")
        with tempfile.TemporaryDirectory() as tmp:
            for name, (content, _, _) in TEMPLATE_CASES.items():
                (pathlib.Path(tmp) / name).write_text(content)
            proc = subprocess.run(
                ["semgrep", "scan", "--config", str(RULES / "template-unescaped-output.yaml"),
                 "--metrics=off", "--disable-version-check", "--quiet", "--json", "--no-git-ignore", tmp],
                capture_output=True, text=True)
            results = json.loads(proc.stdout)["results"]
        for name, (_, rule, expected) in TEMPLATE_CASES.items():
            got = sum(1 for r in results
                      if pathlib.Path(r["path"]).name == name and r["check_id"].endswith(rule))
            self.assertEqual(got, expected, f"{name} {rule}")


if __name__ == "__main__":
    unittest.main()
