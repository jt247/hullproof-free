"""Tests for helpers/ledger.py (coverage ledger). Standard library only.

  python3 -m unittest tools/hullproof/tests/test_ledger.py
"""
import importlib.util
import io
import pathlib
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE.parent / "helpers" / "ledger.py"
spec = importlib.util.spec_from_file_location("ledger", SCRIPT)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)

PRELAUNCH = """# Pre Launch Audit

## Part 1: BLOCKER requirements

- [ ] **SEC-AUTH-002** Tokens | BLOCKER | PARTIAL | CODE REVIEW | Authority: runtime
- [ ] **SEC-API-001** Auth on routes | BLOCKER | PARTIAL | CODE REVIEW | Authority: runtime

## Part 2: CRITICAL requirements at LAUNCH

- [ ] **SEC-DB-002** Policies | CRITICAL | PARTIAL | CONFIG REVIEW | Authority: runtime

## Part 3: CRITICAL requirements at GROWTH

- [ ] **SEC-FIX-404** Alerts | CRITICAL | PARTIAL | CONFIG REVIEW | Authority: dashboard

## Results

| ID | Result | Severity |
|----|--------|----------|
| SEC-AUTH-002 | PASS | BLOCKER |
| SEC-API-001 | FAIL | BLOCKER |
| SEC-DB-002 | PASS | CRITICAL |
"""


def results(rows, heading="Results"):
    body = "\n".join(f"| {i} | PASS | x |" for i in rows)
    return f"## {heading}\n\n| ID | Result | Notes |\n|----|--------|-------|\n{body}\n"


class Ledger(unittest.TestCase):
    def run_cli(self, checklist, res, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            c, r = pathlib.Path(tmp, "c.md"), pathlib.Path(tmp, "r.md")
            c.write_text(checklist)
            r.write_text(res)
            p = subprocess.run([sys.executable, str(SCRIPT), str(c), "--results", str(r), *extra], capture_output=True, text=True)
            return p.returncode, p.stdout

    def test_checklist_ids_follow_the_declared_stage(self):
        self.assertEqual(ledger.checklist_ids(PRELAUNCH, "LAUNCH"), ["SEC-AUTH-002", "SEC-API-001", "SEC-DB-002"])
        self.assertEqual(ledger.checklist_ids(PRELAUNCH, "GROWTH")[-1], "SEC-FIX-404")
        self.assertEqual(len(ledger.checklist_ids(PRELAUNCH)), 4)

    def test_checklist_item_stage_field_is_used_without_parts(self):
        text = "- [ ] **SEC-WEB-026** CSRF | HIGH | GROWTH | Authority: runtime | [r](x)\n- [ ] **SEC-FIX-510** Enc | HIGH | LAUNCH | Authority: repo | [r](x)\n"
        self.assertEqual(ledger.checklist_ids(text, "LAUNCH"), ["SEC-FIX-510"])

    def test_clean_run_exits_zero_and_prints_the_count_line(self):
        code, out = self.run_cli(PRELAUNCH, PRELAUNCH, "--stage", "LAUNCH")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip(), "Ledger: in scope 3, rows 3, missing 0, duplicate 0, extra 0")

    def test_missing_duplicate_and_extra_ids_are_named(self):
        res = results(["SEC-AUTH-002", "SEC-AUTH-002", "SEC-FIX-510"])
        code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH")
        self.assertEqual(code, 1)
        self.assertIn("Ledger: in scope 3, rows 3, missing 2, duplicate 1, extra 1", out)
        self.assertIn("missing (2): SEC-API-001, SEC-DB-002", out)
        self.assertIn("duplicate (1): SEC-AUTH-002", out)
        self.assertIn("extra (1): SEC-FIX-510", out)

    def test_section_limits_the_tables(self):
        res = results(["SEC-AUTH-002"], "Other table") + results(["SEC-AUTH-002", "SEC-API-001", "SEC-DB-002"], "Coverage ledger")
        code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH", "--section", "Coverage ledger")
        self.assertEqual(code, 0, out)

    def test_tables_without_a_result_column_are_ignored(self):
        res = "## Findings\n\n| ID | Title |\n|----|-------|\n| SEC-FIX-510 | x |\n\n" + results(["SEC-AUTH-002", "SEC-API-001", "SEC-DB-002"])
        code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH")
        self.assertEqual(code, 0, out)

    def test_ids_file_replaces_the_checklist(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids, r = pathlib.Path(tmp, "ids.txt"), pathlib.Path(tmp, "r.md")
            ids.write_text("SEC-AUTH-002, SEC-API-001\nSEC-DB-002")
            r.write_text(results(["SEC-AUTH-002", "SEC-API-001"]))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ledger.main(["--ids", str(ids), "--results", str(r), "--line"])
            self.assertEqual(code, 1)
            self.assertEqual(buf.getvalue().strip(), "Ledger: in scope 3, rows 2, missing 1, duplicate 0, extra 0")

    def test_pass_static_on_a_non_repo_requirement_fails_the_run(self):
        # SEC-DB-002 has Authority: runtime in the checklist, so PASS (static) is not allowed for it.
        res = PRELAUNCH.replace("| SEC-DB-002 | PASS |", "| SEC-DB-002 | PASS (static) |")
        code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH")
        self.assertEqual(code, 1)
        self.assertIn("static_not_repo (1): SEC-DB-002", out)
        code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH", "--line")
        self.assertEqual(out.strip(), "Ledger: in scope 3, rows 3, missing 0, duplicate 0, extra 0, static_not_repo 1")

    def test_pass_static_on_a_repo_requirement_is_allowed(self):
        chk = PRELAUNCH.replace("| CONFIG REVIEW | Authority: runtime", "| CONFIG REVIEW | Authority: repo")
        res = PRELAUNCH.replace("| SEC-DB-002 | PASS |", "| SEC-DB-002 | PASS (static) |")
        code, out = self.run_cli(chk, res, "--stage", "LAUNCH")
        self.assertEqual(code, 0, out)

    def test_controls_file_supplies_the_authority_and_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctl = pathlib.Path(tmp, "controls.json")
            ctl.write_text('{"controls": [{"id": "SEC-AUTH-002", "authority": "dashboard"}]}')
            res = PRELAUNCH.replace("| SEC-AUTH-002 | PASS |", "| SEC-AUTH-002 | PASS (static) |")
            code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH", "--controls", str(ctl))
        self.assertEqual(code, 1)
        self.assertIn("static_not_repo (1): SEC-AUTH-002", out)

    def test_rule_8_findings_are_counted_and_do_not_fail_the_run(self):
        res = PRELAUNCH + (
            "\n### F-01: No breach runbook\n\n| Field | Value |\n|---|---|\n| Severity | MEDIUM |\n| Class | MISSING CONTROL RECORD |\n"
            "\n### F-02: Open route\n\n| Field | Value |\n|---|---|\n| Severity | HIGH |\n| Class | FINDING |\n"
            "\n### F-03: Access matrix\n\n| Severity | MEDIUM |\nRated MEDIUM by rule 8.\n"
            "\n### F-04: Record missing, practice present\n\n| Severity | HIGH |\n| Class | MISSING CONTROL RECORD |\n")
        code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH")
        self.assertEqual(code, 0, out)
        self.assertIn("rule_8 (2): F-01, F-03", out)
        code, out = self.run_cli(PRELAUNCH, res, "--stage", "LAUNCH", "--line")
        self.assertEqual(out.strip(), "Ledger: in scope 3, rows 3, missing 0, duplicate 0, extra 0, rule_8 2")

    def test_bad_input_exits_two(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "nope.md", "--results", "nope2.md"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_standard_library_only_and_no_network(self):
        src = SCRIPT.read_text()
        for bad in ("socket", "urllib", "http.client", "requests", "subprocess"):
            self.assertNotIn(f"import {bad}", src)


if __name__ == "__main__":
    unittest.main()
