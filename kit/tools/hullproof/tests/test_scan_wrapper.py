"""Tests for scan.sh (scanner wrapper). Uses stub scanners on PATH, so no real scanner or network is needed.

  python3 -m unittest tools/hullproof/tests/test_scan_wrapper.py
"""
import hashlib
import json
import os
import pathlib
import shutil
import stat
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent
SCAN = TOOLS / "scan.sh"
GIT = ["git", "-c", "user.email=t@example.test", "-c", "user.name=t"]

STUBS = {
    "gitleaks": 'case "$1" in version) echo 8.99.0;; *) echo "INF no leaks found";; esac',
    "semgrep": 'case "$1" in --version) echo 1.99.0;; *) echo "Ran 7 rules on 2 files: 0 findings.";; esac',
    "osv-scanner": 'case "$1" in --version) echo "osv-scanner version: 2.99.0";; *) echo "Scanned /r/package-lock.json file and found 3 packages";; esac',
}


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


class ScanWrapper(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        kit = self.repo / "tools" / "hullproof"
        (kit / "rules").mkdir(parents=True)
        shutil.copy(SCAN, kit / "scan.sh")
        (kit / "gitleaks.toml").write_text("title = \"x\"\n")
        (kit / "rules" / "a.yaml").write_text("rules: []\n")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "a.ts").write_text("export const a = 1;\n")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "add", "-A"], check=True)
        subprocess.run(GIT + ["-C", str(self.repo), "commit", "-qm", "x"], check=True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.log = self.tmp / "calls.log"

    def stub(self, name):
        p = self.bin / name
        p.write_text(f'#!/bin/sh\necho "{name} $*" >> "{self.log}"\n{STUBS[name]}\n')
        p.chmod(p.stat().st_mode | stat.S_IXUSR)

    def run_scan(self, *args, tools=("gitleaks", "semgrep", "osv-scanner")):
        for t in tools:
            self.stub(t)
        out = self.tmp / "out"
        env = dict(os.environ, PATH=f"{self.bin}:/usr/bin:/bin")
        p = subprocess.run(["sh", str(self.repo / "tools/hullproof/scan.sh"), "--out", str(out), *args, str(self.repo)],
                           capture_output=True, text=True, env=env)
        return p, out

    def calls(self):
        return self.log.read_text().splitlines() if self.log.exists() else []

    def test_runs_the_exact_tool_chain_forms(self):
        p, out = self.run_scan("--allow-network")
        self.assertEqual(p.returncode, 0, p.stderr)
        scans = [c for c in self.calls() if not c.endswith("version") and "--version" not in c]
        self.assertEqual(scans, [
            "gitleaks git . --redact --no-banner --config tools/hullproof/gitleaks.toml --ignore-gitleaks-allow",
            "gitleaks dir . --redact --no-banner --config tools/hullproof/gitleaks.toml --ignore-gitleaks-allow",
            "semgrep scan --config tools/hullproof/rules --metrics=off",
            "osv-scanner scan source -r .",
        ])

    def test_each_output_has_a_meta_json_with_the_provenance_fields(self):
        p, out = self.run_scan("--allow-network")
        head = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD", "HEAD^{tree}"], capture_output=True, text=True).stdout.split()
        tracked = len(subprocess.run(["git", "-C", str(self.repo), "ls-files"], capture_output=True, text=True).stdout.split())
        for name in ("gitleaks-git", "gitleaks-dir", "semgrep", "osv-scanner"):
            self.assertTrue((out / f"{name}.txt").is_file(), name)
            meta = json.loads((out / f"{name}.meta.json").read_text())
            for key in ("commit", "tree", "tool", "version", "config_sha", "files_scanned", "files_tracked"):
                self.assertIn(key, meta, f"{name} {key}")
            self.assertEqual((meta["commit"], meta["tree"]), tuple(head))
            self.assertEqual(meta["files_tracked"], tracked)
            self.assertEqual(meta["exit_code"], 0)
        gl = json.loads((out / "gitleaks-dir.meta.json").read_text())
        self.assertEqual(gl["version"], "8.99.0")
        self.assertEqual(gl["config_sha"], sha256(self.repo / "tools/hullproof/gitleaks.toml"))
        self.assertIsNone(gl["files_scanned"])
        sg = json.loads((out / "semgrep.meta.json").read_text())
        self.assertEqual((sg["version"], sg["files_scanned"]), ("1.99.0", 2))
        self.assertEqual(len(sg["config_sha"]), 64)
        osv = json.loads((out / "osv-scanner.meta.json").read_text())
        self.assertEqual((osv["files_scanned"], osv["config_sha"]), (1, None))

    def test_a_tool_that_is_not_installed_is_skipped_and_nothing_is_installed(self):
        p, out = self.run_scan(tools=("semgrep",))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("skipped gitleaks: not installed", p.stdout)
        self.assertIn("skipped osv-scanner: not installed", p.stdout)
        self.assertEqual(sorted(x.name for x in out.glob("*.txt")), ["semgrep.txt"])
        text = SCAN.read_text()
        for bad in ("brew ", "pip ", "pip3 ", "npm ", "apt", "curl ", "wget ", "go install"):
            self.assertNotIn(bad, text)

    def test_osv_needs_the_network_flag(self):
        p, out = self.run_scan()
        self.assertIn("skipped osv-scanner: it sends package names to osv.dev", p.stdout)
        self.assertFalse((out / "osv-scanner.txt").exists())
        self.assertFalse(any(c.startswith("osv-scanner scan") for c in self.calls()))

    def refused(self, config_text, expect):
        with open(self.repo / ".git" / "config", "a") as f:
            f.write(config_text)
        p, out = self.run_scan()
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("refused", p.stderr)
        self.assertIn(expect, p.stdout)
        self.assertFalse(out.exists(), "nothing may be written when the run is refused")
        self.assertEqual(self.calls(), [], "no scanner may start")

    def test_refuses_a_git_config_key_that_runs_code(self):
        for key in ("fsMonitor = touch x", "sshCommand = ssh -v", "hooksPath = hooks", "pager = less", "editor = vi", "textconv = cat"):
            with self.subTest(key=key):
                self.setUp()
                self.refused(f"[core]\n\t{key}\n", "code running keys 1")

    def test_refuses_a_diff_filter_or_credential_section(self):
        for section in ('[diff "x"]', '[filter "lfs"]', '[credential]'):
            with self.subTest(section=section):
                self.setUp()
                self.refused(f"{section}\n\tfoo = bar\n", "driver and credential sections 1")

    def test_a_remote_url_with_credentials_is_counted_never_printed(self):
        with open(self.repo / ".git" / "config", "a") as f:
            f.write('[remote "origin"]\n\turl = https://bob:hunter22@example.test/r.git\n')
        p, out = self.run_scan()
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("remote URLs with credentials 1", p.stdout)
        self.assertIn("ROTATION REQUIRED", p.stdout)
        self.assertNotIn("hunter22", p.stdout + p.stderr)

    def test_a_folder_that_is_not_a_git_repository_is_refused(self):
        plain = self.tmp / "plain"
        plain.mkdir()
        shutil.copytree(self.repo / "tools", plain / "tools")
        p = subprocess.run(["sh", str(plain / "tools/hullproof/scan.sh"), "--out", str(self.tmp / "o"), str(plain)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_usage_errors_exit_two(self):
        for args in ([], ["--bogus"], ["--out"]):
            p = subprocess.run(["sh", str(SCAN), *args], capture_output=True, text=True)
            self.assertEqual(p.returncode, 2, args)


if __name__ == "__main__":
    unittest.main()
