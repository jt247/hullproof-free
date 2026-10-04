#!/usr/bin/env python3
"""Coverage ledger: compare the in scope requirement IDs with the rows of a results table.

Every in scope ID must appear in exactly one row. The script prints the counts and then the missing, duplicate and extra IDs.
It reads files only, makes no network call and writes nothing. Python 3 standard library only.

  python3 tools/hullproof/helpers/ledger.py docs/hullproof/PRE-LAUNCH-AUDIT.md --results docs/security/reports/PRE-LAUNCH-RESULTS-2026-01-31.md --stage GROWTH
  python3 tools/hullproof/helpers/ledger.py docs/hullproof/checklists/SAAS-CHECKLIST.md --results SECURITY-AUDIT-REPORT.md --section "Coverage ledger"
  python3 tools/hullproof/helpers/ledger.py --ids in-scope.txt --results SECURITY-AUDIT-REPORT.md

In scope IDs come from the checklist files (lines that start with `- [ ] **SEC-XXX-000**`), cut to the declared stage with --stage,
or from --ids (a text file with IDs separated by spaces, commas or lines; use it after gate answers and release scope have removed items).
A results table is a markdown table whose header has an ID column and a Result (or State) column. Rows with no ID in the first
cell are ignored. --section limits the tables to those under a heading that contains the given text.
Exit status: 0 when nothing is missing, duplicate or extra, 1 when something is, 2 on a usage or input error.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ID_RE = re.compile(r"SEC-[A-Z]+-\d{3}")
ITEM_RE = re.compile(r"^- \[[ xX]\] \*\*(SEC-[A-Z]+-\d{3})\*\*(.*)$")
PART_STAGE = {"1": "LAUNCH", "2": "LAUNCH", "3": "GROWTH", "4": "SCALE"}
RANK = {"LAUNCH": 0, "GROWTH": 1, "SCALE": 2}


def checklist_ids(text, stage=None):
    """IDs of the checklist items, in order. With a stage, items whose own stage is above it are dropped."""
    ids, part = [], None
    for line in text.splitlines():
        m = re.match(r"^## Part (\d)\b", line)
        if m:
            part = PART_STAGE.get(m.group(1))
        item = ITEM_RE.match(line)
        if not item:
            continue
        own = part
        if own is None:
            s = re.search(r"\|\s*(LAUNCH|GROWTH|SCALE)\b", item.group(2))
            own = s.group(1) if s else None
        if stage and own and RANK[own] > RANK[stage]:
            continue
        ids.append(item.group(1))
    return ids


def result_rows(text, section=None):
    """IDs found in the first cell of the rows of every results table (header has an ID and a Result or State column)."""
    rows, heading, in_table = [], "", False
    for line in text.splitlines():
        h = re.match(r"^#{1,6}\s+(.*)$", line)
        if h:
            heading, in_table = h.group(1), False
            continue
        if not line.lstrip().startswith("|"):
            in_table = False
            continue
        cells = [c.strip().strip("*`").lower() for c in line.strip().strip("|").split("|")]
        if not in_table:
            if cells and cells[0] in ("id", "requirement") and any(c in ("result", "state") for c in cells[1:]):
                in_table = (section is None) or (section.lower() in heading.lower())
            continue
        if set("".join(cells)) <= set("-: "):
            continue  # separator row
        found = ID_RE.search(line.strip().strip("|").split("|")[0])
        if found:
            rows.append(found.group(0))
    return rows


def compare(in_scope, rows):
    want, got = Counter(in_scope), Counter(rows)
    return {
        "in_scope": len(want),
        "rows": len(rows),
        "missing": sorted(i for i in want if not got[i]),
        "duplicate": sorted(i for i, n in got.items() if n > 1),
        "extra": sorted(i for i in got if i not in want),
    }


def count_line(r):
    return (f"Ledger: in scope {r['in_scope']}, rows {r['rows']}, missing {len(r['missing'])}, "
            f"duplicate {len(r['duplicate'])}, extra {len(r['extra'])}")


def report(r):
    out = [count_line(r)]
    for kind in ("missing", "duplicate", "extra"):
        if r[kind]:
            out.append(f"{kind} ({len(r[kind])}): " + ", ".join(r[kind]))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("checklists", nargs="*", help="checklist markdown files (PRE-LAUNCH-AUDIT.md or checklists/*.md)")
    ap.add_argument("--results", required=True, help="markdown file with the results table")
    ap.add_argument("--stage", choices=list(RANK), help="declared stage; items above it are not in scope")
    ap.add_argument("--ids", help="text file with the in scope IDs (replaces the checklist files)")
    ap.add_argument("--section", help="only tables under a heading that contains this text")
    ap.add_argument("--line", action="store_true", help="print only the count line")
    a = ap.parse_args(argv)
    try:
        if a.ids:
            scope = ID_RE.findall(Path(a.ids).read_text())
        elif a.checklists:
            scope = [i for f in a.checklists for i in checklist_ids(Path(f).read_text(), a.stage)]
        else:
            ap.error("give checklist files or --ids")
        text = Path(a.results).read_text()
    except OSError as e:
        print(f"ledger: {e}", file=sys.stderr)
        return 2
    if not scope:
        print("ledger: no in scope IDs found", file=sys.stderr)
        return 2
    result = compare(scope, result_rows(text, a.section))
    print(count_line(result) if a.line else report(result))
    return 0 if not (result["missing"] or result["duplicate"] or result["extra"]) else 1


if __name__ == "__main__":
    sys.exit(main())
