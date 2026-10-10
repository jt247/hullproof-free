"""Every rule added in 0.3.1 has a positive and a negative fixture, and the whole pack passes the Semgrep rule tests.

  python3 -m unittest tools/hullproof/tests/test_rules_new_pack.py
"""
import pathlib
import re
import shutil
import subprocess
import unittest

HERE = pathlib.Path(__file__).resolve().parent
RULES = HERE.parent / "rules"

# rule file -> (fixture file, rule ids)
NEW = {
    "verify-result-unused.yaml": ("verify-result-unused.ts", ["hullproof-verify-result-unused"]),
    "next-public-secret-name.yaml": ("next-public-secret-name.ts", ["hullproof-next-public-secret-name"]),
    "api-route-no-auth.yaml": ("api-route-no-auth.ts", ["hullproof-api-route-no-auth"]),
    "log-session-token.yaml": ("log-session-token.ts", ["hullproof-log-session-token"]),
    "read-by-id-no-owner.yaml": ("read-by-id-no-owner.ts", ["hullproof-read-by-id-no-owner"]),
    "github-workflow-unsafe.yaml": ("github-workflow-unsafe.test.yaml", ["hullproof-workflow-write-all", "hullproof-workflow-untrusted-in-run"]),
    "hardcoded-signing-secret.yaml": ("hardcoded-signing-secret.ts", ["hullproof-hardcoded-signing-secret"]),
    "zod-privileged-fields.yaml": ("zod-privileged-fields.ts", ["hullproof-zod-privileged-field"]),
    "server-action-no-auth.yaml": ("server-action-no-auth.ts", ["hullproof-server-action-no-auth"]),
}


class NewRules(unittest.TestCase):
    def test_every_new_rule_has_a_positive_and_a_negative_fixture(self):
        for rule_file, (fixture, ids) in NEW.items():
            text = (HERE / fixture).read_text()
            declared = re.findall(r"(?m)^  - id: (\S+)", (RULES / rule_file).read_text())
            self.assertEqual(sorted(declared), sorted(ids), rule_file)
            for rid in ids:
                self.assertRegex(text, rf"(?m)^\s*(//|#)\s*ruleid: {re.escape(rid)}\s*$", f"{rid} has no positive case")
                self.assertRegex(text, rf"(?m)^\s*(//|#)\s*ok: {re.escape(rid)}\s*$", f"{rid} has no negative case")

    def test_the_server_action_rule_has_the_no_directive_negative_file(self):
        self.assertIn("ok: hullproof-server-action-no-auth", (HERE / "server-action-no-auth-negative.ts").read_text())

    def test_the_rule_pack_passes_semgrep_test(self):
        if not shutil.which("semgrep"):
            self.skipTest("semgrep not installed")
        p = subprocess.run(["semgrep", "--test", "--config", str(RULES), str(HERE)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout[-1500:] + p.stderr[-500:])
        self.assertIn("All tests passed", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
