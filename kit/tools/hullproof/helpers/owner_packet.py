#!/usr/bin/env python3
"""Owner packet: turn the unsettled controls of an audit into a filled PROVIDER-EXPORTS.md and STAGING-TEST-WINDOW.md.

An audit ends with a list of requirements it could not settle (UNVERIFIED CONTROLS, each with one routed state). This script reads that
list and writes two checklists grouped by action, so one export session per provider and one staging session close many rows at once.

  python3 tools/hullproof/helpers/owner_packet.py --report docs/security/reports/SECURITY-AUDIT-REPORT.md
  python3 tools/hullproof/helpers/owner_packet.py --findings docs/security/reports/SECURITY-AUDIT-REPORT.findings.md --out ~/Desktop/owner-packet
  python3 tools/hullproof/helpers/owner_packet.py --report R.md --findings R.findings.md --controls docs/hullproof/security-controls.json

Inputs (give at least one):
  --report    the audit report. Rows of the UNVERIFIED CONTROLS table (requirement, severity, state, why, owner action).
  --findings  the findings record. Records of kind routed (one row per SEC ID). A row also in the report keeps the report's text.
  --controls  security-controls.json, only to fill in a severity the rows do not carry.
Output: PROVIDER-EXPORTS.md and STAGING-TEST-WINDOW.md in --out (default: the folder of the first input file). Nothing else is written, and
an existing file is never replaced unless you pass --force. The templates are read from docs/hullproof/templates next to the tools folder
(--templates to point elsewhere).
Where each state goes: NEEDS DASHBOARD to the provider exports, grouped by provider with the requirements each export closes. NEEDS DYNAMIC TEST
and NEEDS BUILD to the staging window (the prepared checks that name the requirement, then the rest). ASK OWNER, ATTESTATION and UNKNOWN to
the owner answers section of the provider exports.
Reads files only, makes no network call. Python 3 standard library only. Exit: 0 written, 1 no unsettled rows found, 2 usage or input error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"SEC-[A-Z]+-\d{3}")
STATES = ("NEEDS DASHBOARD", "NEEDS BUILD", "NEEDS DYNAMIC TEST", "ASK OWNER", "ATTESTATION", "UNKNOWN")
SEV_RANK = {"BLOCKER": 0, "CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
CELL_MAX = 300
DEFAULT_TEMPLATES = Path(__file__).resolve().parents[3] / "docs" / "hullproof" / "templates"


def clean(text, limit=CELL_MAX):
    """One line of plain text: no control characters, no table breaking pipes, capped."""
    text = re.sub(r"[\x00-\x1f\x7f​-‏‪-‮⁦-⁩]", " ", str(text or ""))
    text = re.sub(r"\s+", " ", text).replace("|", "/").strip()
    return text[:limit]


def state_of(text):
    up = (text or "").upper()
    return next((s for s in STATES if s in up), None)


def parse_report(text):
    """Rows of the UNVERIFIED CONTROLS table: {id, severity, state, why, action}."""
    rows, in_section, head = [], False, None
    for line in text.splitlines():
        h = re.match(r"^##\s+(.*)$", line)
        if h:
            in_section, head = h.group(1).strip().upper().startswith("UNVERIFIED CONTROLS"), None
            continue
        if not in_section or not line.lstrip().startswith("|"):
            continue
        cells = [c.strip().strip("*`") for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        low = [c.lower() for c in cells]
        if head is None:
            if low and low[0] in ("requirement", "id"):
                head = {name: next((i for i, c in enumerate(low) if c.startswith(name)), None) for name in ("severity", "state", "why", "owner")}
            continue
        found = ID_RE.search(cells[0])
        get = lambda k: cells[head[k]] if head[k] is not None and head[k] < len(cells) else ""  # noqa: E731
        st = state_of(get("state"))
        if found and st:
            sev = get("severity").upper()
            rows.append(dict(id=found.group(0), severity=sev if sev in SEV_RANK else "", state=st, why=clean(get("why")), action=clean(get("owner"))))
    return rows


def parse_findings(text):
    """One row per SEC ID of every routed record. Returns (rows, commit)."""
    m = re.search(r"(?ms)^```hullproof-findings[ \t]*\n(.*?)\n```[ \t]*$", text) or re.search(r'(?ms)^```json[ \t]*\n(\{.*?"records".*?\})\n```[ \t]*$', text)
    if not m:
        raise ValueError("no hullproof-findings block found")
    data = json.loads(m.group(1))
    rows = []
    for r in data.get("records", []):
        st = state_of(r.get("state")) if r.get("kind") == "routed" else None
        for sid in r.get("sec_ids", []) if st else []:
            rows.append(dict(id=sid, severity="", state=st, why=clean(r.get("reason")), action=clean(r.get("owner_action")), card=clean(r.get("check_card"), 40)))
    return rows, (data.get("report") or {}).get("commit", "")


def merge(report_rows, finding_rows, severities):
    """One row per ID. The report's row wins, the record fills what it lacks."""
    out = {}
    for r in finding_rows + report_rows:  # later wins, so the report overwrites
        old = out.get(r["id"], {})
        out[r["id"]] = {**old, **{k: v for k, v in r.items() if v}}
    for i, r in out.items():
        r.setdefault("severity", "")
        r["severity"] = r["severity"] or severities.get(i, "")
    return sorted(out.values(), key=lambda r: (SEV_RANK.get(r["severity"], 5), r["id"]))


def section(text, name, nxt):
    """The text of a template section from '## name' up to '## nxt' (or the end)."""
    m = re.search(rf"(?ms)^## {re.escape(name)}\n(.*?)(?=^## {re.escape(nxt)}|\Z)", text)
    return m.group(1).strip() if m else ""


def provider_table(template):
    """Template exports table -> [{provider, what, how, ids, evidence_only}]."""
    out = []
    for line in template.splitlines():
        if not line.startswith("| ") or line.startswith("| Provider") or set(line) <= set("|- "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        settles, _, only = cells[3].partition("Owner evidence only:")
        out.append(dict(provider=cells[0], what=cells[1], how=cells[2], ids=ID_RE.findall(settles), evidence_only=ID_RE.findall(only)))
    return out


def check_lines(template):
    """Template staging checks -> [(part, subheading, line, ids)]."""
    out, part, sub = [], "", ""
    for line in template.splitlines():
        h = re.match(r"^## (Part \d+.*)$", line)
        if h:
            part, sub = h.group(1), ""
            continue
        if re.match(r"^## ", line):
            part, sub = "", ""
            continue
        if part and line.strip() and not line.startswith("- [ ]") and not line.startswith(("Each line", "Use the")):
            sub = line.strip()
        if part and line.startswith("- [ ]"):
            out.append((part, sub, line, ID_RE.findall(line)))
    return out


def row_line(r):
    sev = r["severity"] or "severity not given"
    why = f" Why: {r['why']}." if r.get("why") else ""
    act = f" Action: {r['action']}." if r.get("action") else ""
    return f"- [ ] {r['id']} ({sev}).{why}{act}"


def build_exports(rows, template, source):
    mine = [r for r in rows if r["state"] == "NEEDS DASHBOARD"]
    by_id = {r["id"]: r for r in mine}
    out = ["# Provider Exports", "",
           f"Filled from {source}. {len(mine)} requirements are waiting on a provider export. Save each export in the evidence folder named in `docs/security/STAGE.md`, "
           "dated, with the commit or environment it describes. Delete this note when you hand it over.", ""]
    for name, nxt in (("Redaction rules (apply to every export)", "Freshness"), ("Freshness (Hullproof policy)", "What an export can and cannot close"),
                      ("What an export can and cannot close", "Exports")):
        body = section(template, name, nxt)
        if body:
            out += [f"## {name}", "", body, ""]
    groups, used = [], set()
    for p in provider_table(template):
        hit = [by_id[i] for i in p["ids"] if i in by_id]
        ev = [by_id[i] for i in p["evidence_only"] if i in by_id]
        if hit or ev:
            groups.append((p, hit, ev))
            used.update(r["id"] for r in hit + ev)
    groups.sort(key=lambda g: (-len(g[1]), min([SEV_RANK.get(r["severity"], 5) for r in g[1] + g[2]]), g[0]["provider"]))
    out += ["## Exports to take, one session per provider", ""]
    if not groups:
        out += ["None of the open requirements maps to a provider in the template.", ""]
    for p, hit, ev in groups:
        out += [f"### {p['provider']}: closes {len(hit)} requirement{'s' if len(hit) != 1 else ''}", "", f"Export: {p['what']}", "", f"How: {p['how']}", ""]
        out += [row_line(r) for r in hit]
        out += [row_line(r) + " Owner evidence only: this export does not close the row." for r in ev]
        out += ["", "Exported by: ______  Date: ______  Commit or environment: ______", ""]
    rest = [r for r in mine if r["id"] not in used]
    if rest:
        out += ["## No prepared export, name the provider", "", "The template has no row for these. Say which provider holds the setting, export it the same way, and record the provider name.", ""]
        out += [row_line(r) for r in rest] + [""]
    owner = [r for r in rows if r["state"] in ("ASK OWNER", "ATTESTATION", "UNKNOWN")]
    out += ["## Owner answers and statements", ""]
    if not owner:
        out += ["None.", ""]
    for st in ("ASK OWNER", "ATTESTATION", "UNKNOWN"):
        sub = [r for r in owner if r["state"] == st]
        if sub:
            out += [f"### {st}", ""] + [row_line(r) for r in sub] + [""]
    return "\n".join(out).rstrip() + "\n"


def build_staging(rows, template, source):
    dyn = {r["id"]: r for r in rows if r["state"] == "NEEDS DYNAMIC TEST"}
    build = [r for r in rows if r["state"] == "NEEDS BUILD"]
    out = ["# Staging Test Window Checklist", "",
           f"Filled from {source}. {len(dyn)} requirements wait on a running app and {len(build)} on a build. Run this against a staging copy of the audited commit, "
           "never against production data. Save the filled copy in the evidence folder named in `docs/security/STAGE.md`. Delete this note when you hand it over.", ""]
    for name, nxt in (("Before you start", "Record format"), ("Record format", "Part 1")):
        out += [f"## {name}", "", section(template, name, nxt), ""]
    placed, last = set(), (None, None)
    for part, sub, line, ids in check_lines(template):
        if not any(i in dyn for i in ids):
            continue
        if part != last[0]:
            out += [f"## {part}", ""]
        if sub and (part, sub) != last:
            out += [sub, ""]
        out.append(line)
        placed.update(i for i in ids if i in dyn)
        last = (part, sub)
        out.append("")
    rest = [dyn[i] for i in dyn if i not in placed]
    if rest:
        out += ["## No prepared check", "", "Use the Verify steps of each requirement and record the result in the format above.", ""]
        out += [row_line(r) for r in rest] + [""]
    out += ["## Build checks", ""]
    out += ([row_line(r) for r in build] if build else ["None."]) + [""]
    sign = section(template, "Sign off", "Not run here").split("\n\nNot run here")[0].strip()
    out += ["## Sign off", "", sign or "| Field | Value |\n|---|---|", ""]
    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--report", help="audit report markdown (UNVERIFIED CONTROLS table)")
    ap.add_argument("--findings", help="findings record markdown (routed records)")
    ap.add_argument("--controls", help="security-controls.json, to fill in missing severities")
    ap.add_argument("--out", help="folder for the two files (default: the folder of the first input file)")
    ap.add_argument("--templates", help="folder with PROVIDER-EXPORTS.md and STAGING-TEST-WINDOW.md")
    ap.add_argument("--force", action="store_true", help="replace the two output files if they exist")
    a = ap.parse_args(argv)
    if not (a.report or a.findings):
        ap.error("give --report, --findings or both")
    try:
        rep = parse_report(Path(a.report).read_text(encoding="utf-8")) if a.report else []
        fin, commit = parse_findings(Path(a.findings).read_text(encoding="utf-8")) if a.findings else ([], "")
        sev = {}
        if a.controls:
            sev = {c["id"]: c["severity"] for c in json.loads(Path(a.controls).read_text(encoding="utf-8"))["controls"]}
        tdir = Path(a.templates) if a.templates else DEFAULT_TEMPLATES
        t_exp = (tdir / "PROVIDER-EXPORTS.md").read_text(encoding="utf-8")
        t_stg = (tdir / "STAGING-TEST-WINDOW.md").read_text(encoding="utf-8")
    except (OSError, ValueError, KeyError) as e:
        print(f"owner_packet: {e}", file=sys.stderr)
        return 2
    rows = merge(rep, fin, sev)
    if not rows:
        print("owner_packet: no unsettled rows found (UNVERIFIED CONTROLS or routed records)", file=sys.stderr)
        return 1
    first = Path(a.report or a.findings)
    out_dir = Path(a.out) if a.out else first.resolve().parent
    source = ", ".join(Path(p).name for p in (a.report, a.findings) if p) + (f", commit {commit[:12]}" if commit else "")
    targets = {out_dir / "PROVIDER-EXPORTS.md": build_exports(rows, t_exp, source), out_dir / "STAGING-TEST-WINDOW.md": build_staging(rows, t_stg, source)}
    existing = [p.name for p in targets if p.exists()]
    if existing and not a.force:
        print(f"owner_packet: {', '.join(existing)} already exists in {out_dir}, pass --force to replace it", file=sys.stderr)
        return 2
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        for p, text in targets.items():
            p.write_text(text, encoding="utf-8")
    except OSError as e:
        print(f"owner_packet: {e}", file=sys.stderr)
        return 2
    counts = {s: sum(r["state"] == s for r in rows) for s in STATES}
    print("owner_packet: " + ", ".join(f"{n} {s}" for s, n in counts.items() if n) + f". Written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
