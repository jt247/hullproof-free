"""Tests for helpers/peek.sh (one line of a file with secret shaped values masked).

  python3 -m unittest tools/hullproof/tests/test_peek_script.py
"""
import pathlib
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
PEEK = HERE.parent / "helpers" / "peek.sh"

# Fake values, joined at run time so that no scanner finds a literal in this file.
STRIPE = "sk_" + "live_" + "51HxAbCdEfGh1234567890"
GITHUB = "gh" + "p_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4"
AWS = "AKIA" + "ABCDEFGHIJKLMNOP"
JWT = "eyJ" + "hbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTYifQ.abcDEF123_-xyz"
URLPASS = "hunter22"
LINES = [
    "plain line with nothing secret",
    f"STRIPE_KEY={STRIPE}",
    f'const t = "{GITHUB}"; // note',
    "db: postgres://app" + ":" + f"{URLPASS}@db.example.com/x",
    f"aws {AWS} region",
    f'{{"token": "{JWT}"}}',
    "Authorization: Bearer abcDEF123456xyz",
    '{"password": "p@ss w0rd", "name": "ok"}',
    "export API_TOKEN='abc def ghi'",
    "-----BEGIN RSA PRIVATE KEY-----MIIEowIBAAKCAQEA",
    "x" * 40 + " long run of key characters",
    "short line",
]
SECRET_PARTS = [STRIPE[8:], GITHUB[4:], AWS[4:], JWT[3:20], URLPASS, "w0rd", "abc def ghi", "abcDEF123456xyz", "MIIEowIBAAKCAQEA", "x" * 33]


class Peek(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = pathlib.Path(self.tmp.name, "f.txt")
        self.file.write_text("\n".join(LINES) + "\n")

    def peek(self, spec):
        return subprocess.run(["sh", str(PEEK), spec], capture_output=True, text=True)

    def test_a_plain_line_is_printed_with_its_place(self):
        p = self.peek(f"{self.file}:1")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(p.stdout, f"{self.file}:1: {LINES[0]}\n")

    def test_every_secret_shape_is_masked_and_the_value_never_appears(self):
        for n in range(2, 12):
            p = self.peek(f"{self.file}:{n}")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(len(p.stdout.splitlines()), 1)
            self.assertIn("[MASKED]", p.stdout, f"line {n}")
            for part in SECRET_PARTS:
                self.assertNotIn(part, p.stdout, f"line {n}")
                self.assertNotIn(part, p.stderr)

    def test_the_surrounding_text_is_kept(self):
        self.assertIn('// note', self.peek(f"{self.file}:3").stdout)
        self.assertIn("@db.example.com/x", self.peek(f"{self.file}:4").stdout)
        self.assertIn('"name": "ok"', self.peek(f"{self.file}:8").stdout)
        self.assertIn("region", self.peek(f"{self.file}:5").stdout)

    def test_a_long_line_is_cut_at_300_characters(self):
        self.file.write_text("a b " * 200 + "\n")
        out = self.peek(f"{self.file}:1").stdout
        self.assertLessEqual(len(out.split(": ", 1)[1].rstrip("\n")), 300)

    def test_line_past_the_end_exits_one(self):
        p = self.peek(f"{self.file}:99")
        self.assertEqual(p.returncode, 1)
        self.assertEqual(p.stdout, "")

    def test_usage_errors_exit_two_and_print_nothing_to_stdout(self):
        for spec in ("", "nofile", f"{self.file}", f"{self.file}:0", f"{self.file}:x", f"{self.file}:-1", "missing.txt:3", f"{self.tmp.name}:1"):
            p = self.peek(spec)
            self.assertEqual(p.returncode, 2, spec)
            self.assertEqual(p.stdout, "", spec)
        p = subprocess.run(["sh", str(PEEK)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)

    def test_it_writes_nothing(self):
        before = sorted(x.name for x in pathlib.Path(self.tmp.name).iterdir())
        self.peek(f"{self.file}:2")
        self.assertEqual(sorted(x.name for x in pathlib.Path(self.tmp.name).iterdir()), before)
        text = PEEK.read_text()
        for bad in (">>", "tee ", "curl", "wget", "nc "):
            self.assertNotIn(bad, text.replace("2>&1", ""))


if __name__ == "__main__":
    unittest.main()
