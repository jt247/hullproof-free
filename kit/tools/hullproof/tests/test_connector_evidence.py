"""Runs the comparison block of helpers/connector-evidence.md on sample export files.
  python3 -m unittest tools/hullproof/tests/test_connector_evidence.py
"""
import pathlib
import re
import subprocess
import tempfile
import unittest

DOC = pathlib.Path(__file__).resolve().parent.parent / "helpers" / "connector-evidence.md"


class ConnectorCompare(unittest.TestCase):
    def test_counts(self):
        block = re.search(r"## 3\. Compare with counts\n\n```bash\n(.*?)\n```", DOC.read_text(), re.S).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            ev = pathlib.Path(tmp, "docs/security/evidence/2026-01-31")
            ev.mkdir(parents=True)
            (ev / "connectors-agent.txt").write_text("github\torg1\tdeploy-helper\nvercel\tteam1\tdocs-bot\nsupabase\tacct\tmcp\n")
            (ev / "connectors-provider.txt").write_text(
                "github\torg1\tdeploy-helper\tcontents: write\nvercel\tteam1\tdocs-bot\tread\nstripe\tacct\told-bot\tadmin\nslack\tws\tnotes\tread\n")
            p = subprocess.run(["bash", "-c", block], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout.splitlines(), [
                "agent side: 3", "provider side: 4",
                "authorized at a provider, not in the agent inventory: 2",
                "in the agent inventory, not authorized at a provider: 1",
                "grants with write or admin scope: 2",
            ])

    def test_no_dashes(self):
        t = DOC.read_text()
        self.assertNotIn(chr(0x2014), t)
        self.assertNotIn(chr(0x2013), t)


if __name__ == "__main__":
    unittest.main()
