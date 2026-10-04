"""Catch rate of the rule pack on known bad code variants.

Each file in tests/variants holds blocks marked with a comment line `// variant: <family>-<n>`.
A variant counts as caught when at least one rule reports a finding on a line of its block.
A variant marked `// variant: <id> expect-miss` is a documented gap: the test fails if it starts to
be caught, so the README stays honest.

Usage:
  python3 tools/hullproof/tests/test_variant_catch.py [--rules DIR]   (project root) print the table for a rule directory
  python3 -m unittest tools/hullproof/tests/test_variant_catch.py   regression check against the shipped rules
"""
import argparse
import collections
import json
import pathlib
import re
import shutil
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
RULES = HERE.parent / "rules"
VARIANTS = HERE / "variants"
TAG = re.compile(r"^\s*//\s*variant:\s*(\S+)(?:\s+(expect-miss))?\s*$")


def parse_blocks(path):
    """Return [(variant_id, expect_miss, first_line, last_line)] for one file."""
    lines = path.read_text().splitlines()
    tags = [(i + 1, TAG.match(l)) for i, l in enumerate(lines) if TAG.match(l)]
    blocks = []
    for n, (line_no, m) in enumerate(tags):
        end = tags[n + 1][0] - 1 if n + 1 < len(tags) else len(lines)
        blocks.append((m.group(1), m.group(2) == "expect-miss", line_no + 1, end))
    return blocks


def run_semgrep(rules, target):
    if not shutil.which("semgrep"):
        raise unittest.SkipTest("semgrep not installed")
    # Copy so that semgrep's default ignores (tests folders) do not hide the fixtures.
    proc = subprocess.run(
        ["semgrep", "scan", "--config", str(rules), "--metrics=off", "--disable-version-check",
         "--quiet", "--json", "--no-git-ignore", str(target)],
        capture_output=True, text=True)
    return json.loads(proc.stdout)


def measure(rules, files=None):
    """Return {variant_id: (caught, expect_miss, [rule ids])}."""
    result = {}
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for f in sorted(files or VARIANTS.glob("*.ts")):
            shutil.copy(f, tmp)
        data = run_semgrep(rules, tmp)
        for f in sorted(files or VARIANTS.glob("*.ts")):
            hits = [r for r in data["results"] if pathlib.Path(r["path"]).name == f.name]
            for vid, expect_miss, first, last in parse_blocks(f):
                rules_hit = sorted({h["check_id"].split(".")[-1] for h in hits
                                    if first <= h["start"]["line"] <= last})
                result[vid] = (bool(rules_hit), expect_miss, rules_hit)
    return result


def summarize(result):
    fam = collections.OrderedDict()
    for vid, (caught, _, _) in result.items():
        f = vid.rsplit("-", 1)[0]
        c, t = fam.get(f, (0, 0))
        fam[f] = (c + int(caught), t + 1)
    return fam


class VariantCatch(unittest.TestCase):
    def test_shipped_rules_catch_every_variant_except_documented_gaps(self):
        result = measure(RULES)
        wrong = []
        for vid, (caught, expect_miss, rules_hit) in result.items():
            if expect_miss and caught:
                wrong.append(f"{vid} is marked expect-miss but is now caught by {rules_hit}")
            if not expect_miss and not caught:
                wrong.append(f"{vid} is not caught")
        self.assertEqual(wrong, [])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", default=str(RULES))
    ap.add_argument("--files", nargs="*")
    a = ap.parse_args()
    res = measure(pathlib.Path(a.rules), [pathlib.Path(x) for x in a.files] if a.files else None)
    for vid, (caught, expect_miss, rules_hit) in res.items():
        print(f"{vid:16} {'CAUGHT' if caught else 'missed':7} {','.join(rules_hit)}")
    total = sum(1 for c, _, _ in res.values() if c)
    print("--")
    for f, (c, t) in summarize(res).items():
        print(f"{f:12} {c}/{t}")
    print(f"{'TOTAL':12} {total}/{len(res)}")
