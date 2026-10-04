# Breach Runbook Template

Covers SEC-LOG-024 (CRITICAL) and the register in SEC-LOG-023, plus SEC-LOG-025, 026 and 064, in `docs/hullproof/INCIDENT-RESPONSE.md`. Save as `docs/security/BREACH-RUNBOOK.md` (or the private location in `STAGE.md`). Read the deadline table and notice content tables in `INCIDENT-RESPONSE.md` for each law; do not rely on this sheet for legal content. This is a working aid, not legal advice. Delete this note.

Requirement IDs in this template that have no entry in your `docs/hullproof` folder (SEC-LOG-023 for example) are Hullproof Pro requirements; cite them by ID as written.

## First hour

1. Write down the time the owner became aware: [date and time]. The clock starts there.
2. Declare the incident (your incident response plan names who does this). Open a register entry.
3. Contain: stop the exposure first, but copy evidence before cleanup.
4. Write the exposure window: the commit that introduced the weakness (from `git log`) and the date it reached production, until the date it was closed.
5. Check logs for use of the exposure. Record what you checked and what you could not.
6. A leaked key that unlocks personal data starts the same clock. Run this runbook before the facts are complete.

## Decision tree

1. Is personal data involved (including credentials with an account identifier, card or bank numbers)? If no, handle as a normal incident. If unsure, treat as yes.
2. Were the people or the data exposed to someone who should not have it, lost or altered? If no, record the reasoning and stop.
3. Is there a risk to the people? Record the reasoning either way.
4. For each served market in the table below, notify within its deadline. Phased notice is allowed where the law allows it: send a first notice, then follow up.
5. If you process this data for a business customer, tell that customer without undue delay (they run their own clock).
6. Record every decision, including a decision not to notify, in the register.

## Markets

Fill one row per market named in `STAGE.md`. Take the regulator, deadline and required content from the tables in `INCIDENT-RESPONSE.md`.

| Market | Regulator and route | Deadline from awareness | Notice content checklist | Who files | Notice template path |
|--------|---------------------|-------------------------|--------------------------|-----------|----------------------|
| NG | | | | | |
| EU | | | | | |
| | | | | | |

Reasons for delay if a deadline is passed: [field to fill]. South Africa: the organisation and Information Officer are registered on the regulator portal before any incident: yes or no, date.

## Notices

| Audience | Template | Sent on | Sent by |
|----------|----------|---------|---------|
| Regulator, first notice | | | |
| Regulator, follow up | | | |
| Affected people | | | |
| Business customers (controller) | | | |

Processors: each contract requires the processor to tell you of a breach without undue delay, within 48 hours where Kenyan users are affected. Contracts checked: [list].

## Register entry (one per incident and per breach, including ones judged not reportable)

Keep the register in access restricted storage at [location]. It holds personal data itself.

| Field | Value |
|-------|-------|
| Entry id | |
| Declared at | |
| Aware at | |
| Facts and data types | |
| People affected | Number or "unknown" |
| Exposure window | Start, end |
| Effects | |
| Actions taken | |
| Notification decision per market and why | |
| Notices sent | |
| Root cause fix | Issue link and status |
| Closed on | |
