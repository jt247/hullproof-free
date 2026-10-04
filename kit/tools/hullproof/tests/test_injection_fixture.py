"""Checks tests/fixtures/injection-delimiters.txt: format, case count, unique ids, the canary in every payload, no en or em dashes.
  python3 -m unittest tools/hullproof/tests/test_injection_fixture.py
"""
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "injection-delimiters.txt"
DOC = HERE.parent / "helpers" / "injection-corpus.md"
CANARY = "HULLPROOF_CANARY_7Q"


def cases():
    out = []
    for line in FIXTURE.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        cid, family, payload = line.split("\t")
        out.append((cid, family, json.loads(payload)))
    return out


def reveal(text):
    """Map the Unicode tag block back to ASCII so a hidden instruction can be read."""
    return "".join(chr(ord(c) - 0xE0000) if 0xE0000 <= ord(c) <= 0xE007F else c for c in text)


class InjectionFixture(unittest.TestCase):
    def test_at_least_twenty_unique_cases(self):
        c = cases()
        self.assertGreaterEqual(len(c), 20)
        self.assertEqual(len({i for i, _, _ in c}), len(c))
        self.assertEqual(len({p for _, _, p in c}), len(c))

    def test_every_payload_asks_for_the_canary(self):
        for cid, _, payload in cases():
            self.assertIn(CANARY, reveal(payload), cid)

    def test_delimiter_families_are_present(self):
        text = " ".join(p for _, _, p in cases())
        for needle in ("{{CLOSE}}", "{{OPEN}}", "{{CLOSE_UPPER}}", "{{CLOSE_SPACED}}", "{{CLOSE_ZWSP}}", "]]>", "```", '"""', "-->", "<|im_end|>", "[/INST]",
                       "Human:", "</tool_result>"):
            self.assertIn(needle, text + FIXTURE.read_text(), needle)
        self.assertTrue(any(0xE0000 <= ord(ch) <= 0xE007F for _, _, p in cases() for ch in p), "hidden tag characters")
        self.assertTrue(any(chr(0x202e) in p for _, _, p in cases()), "right to left override")

    def test_no_en_or_em_dashes_anywhere(self):
        for p in (FIXTURE, DOC):
            t = p.read_text()
            self.assertNotIn(chr(0x2014), t, p.name)
            self.assertNotIn(chr(0x2013), t, p.name)

    def test_the_doc_names_the_corpus_and_its_license(self):
        t = DOC.read_text()
        for needle in ("NVIDIA/garak", "Apache License 2.0", "promptinject", "latentinjection", "archived"):
            self.assertIn(needle, t)


if __name__ == "__main__":
    unittest.main()
