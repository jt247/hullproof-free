# Incident Response

| Field | Value |
|-------|-------|
| Domain codes | SEC-LOG |
| Topics covered | Incident Response |
| Part of | Hullproof Security Standard, see STANDARD.md |

Preparing for, handling, and learning from security incidents, including breach notification per market. Requirement IDs keep the SEC-LOG code. Detection signals come from OBSERVABILITY.md; secret rotation from SECRETS.md.

> Research based engineering guidance, not legal advice.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 1 of the 16 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-LOG-024](#sec-log-024-a-breach-runbook-meets-each-served-markets-deadline) | A breach runbook meets each served market's deadline | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Mobile, AI features |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Incident response plan and named roles (solo builder friendly) | GOVERNANCE.md | None | SEC-LOG-022 |
| Severity classification of incidents | None | None | SEC-LOG-060 |
| Containment: leaked secret | SECRETS.md, AGENTIC-DEV-SECURITY.md | None | SEC-LOG-061 |
| Leaked provider credential reported or revoked through the provider's route | SECRETS.md, AGENTIC-DEV-SECURITY.md | None | SEC-LOG-066 |
| Evidence preservation and timeline | OBSERVABILITY.md, INFRASTRUCTURE-SECURITY.md | None | SEC-LOG-023, SEC-LOG-062 |
| Eradication | None | None | SEC-LOG-063 |
| Recovery, restore from backup | DATABASE-SECURITY.md, INFRASTRUCTURE-SECURITY.md | None | SEC-LOG-028 |
| Breach notification to regulators per market (deadlines and content) | None | None | SEC-LOG-026 |
| Notification to affected users | None | None | SEC-LOG-024 |
| Customer and vendor communication | None | None | SEC-LOG-025, SEC-LOG-064, SEC-LOG-065 |
| Out of band incident communication | None | None | SEC-LOG-067 |
| Post incident review and lessons learned | GOVERNANCE.md | None | SEC-LOG-029 |
| Live exposure triage and exposure window record | None | Breach triage | SEC-LOG-076 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-MARKET-ZA | Does the product process personal data of people in South Africa? | STAGE.md Markets served and Markets excluded name the market, and a check of signup country, billing country or analytics geography shows no South African data subjects, or the owner's written answer says so. A market is excluded only by a technical control that blocks it (a country block at signup and billing) or by a recorded count of zero data subjects from the user table by country. Where the product collects no country, Global applies. | SEC-LOG-026 |
<!-- hullproof:gates:end -->

The security, abuse and leaked key routes for each default stack provider (checked 2026-10-02) are in the provider contacts template (`templates/PROVIDER-CONTACTS.md`). Routes change, so SEC-LOG-065 requires the team to confirm each one from the provider's own pages.

---

## Incident Response

### SEC-LOG-024: A breach runbook meets each served market's deadline

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile, AI features |
| Automation | MANUAL |
| Verification method | DOCUMENT REVIEW, MANUAL TEST |

**Requirement.** The team MUST keep a breach notification runbook with a decision tree and prepared notice templates for regulators and affected people in every served market, each set to meet the deadlines in the table above.

**Why.** Regulator deadlines of 72 hours in Nigeria, the EU, the United Kingdom and Kenya cannot be met by writing notices from scratch during an incident, and each law requires specific notice content. A leaked key that unlocks personal data starts the same clock, so the runbook must be usable before the facts are complete. This applies per served market.

**Implementation.**
- Record which markets the product serves and include only those laws in the runbook.
- Prepare templates with each law's required content from the notice content table above, kept as a per market checklist with one line per content item (for example GDPR Art 33(3)(a) to (d) and the same items in UK GDPR, Kenya s43(5)(a) to (e) and reg 38(1)(a) to (i), GAID Art 33(5) for the NDPC, POPIA s22(5) for South African data subjects, and Canada reg 2(1)(a) to (g) for the Privacy Commissioner and reg 3(a) to (f) for people). For a product with United States users, keep a short list of the states where users live with each state's deadline, thresholds and regulator route taken from the state's own statute.
- Include phased notice where the law allows it (Nigeria, EU, Kenya) so a first notice can go out before the investigation ends, and a field for the reasons for delay where the 72 hour mark is passed (EU, Kenya).
- For Kenyan users, put the reg 37 categories (credentials with an account identifier, Second Schedule data such as card or bank account numbers) in the decision tree as automatic notify triggers.
- Treat a leaked key that unlocks personal data as a possible breach and run the risk test (leaked secret procedure in SECRETS.md).
- Name the privacy owner from SEC-LOG-022 as the person who decides and sends.

**Verify.**
1. Review the runbook for each served market's deadlines, recipients and template content.
2. Tick each regulator and people template against its market checklist and confirm every content item in the notice content table has a field (for an EU template: nature, numbers, contact point, consequences, measures; for a Kenya regulator template also the awareness date, chronology, cause and grounds for not telling people).
3. During the yearly tabletop, time the path from declaration to a ready to send regulator notice.

**Evidence.** The runbook, templates and the tabletop timing record.

**Exceptions.** Rule 8 of STANDARD.md Severity applies: when this runbook is missing and the practice it covers is also absent (for example the product holds no personal data), rate the finding MEDIUM. When personal data is held and the runbook is missing, the CRITICAL label stands. CRITICAL exception only: in writing, with a named owner, a compensating control and an expiry date. Products that hold no personal data are exempt; record that decision.

**References.** Nigeria Data Protection Act 2023 s40(2), (3), (4), (9) [SRC-100]; NDP Act GAID 2025 Art 33 [SRC-101]; GDPR Art 33(1), (3), (4), Art 34(1), (2), (3) [SRC-103]; UK GDPR Art 33, Art 34 [SRC-323]; PIPEDA s10.1 [SRC-325]; Breach of Security Safeguards Regulations reg 2, 3 [SRC-326]; US state statutes (California [SRC-327], Florida [SRC-328], Texas [SRC-329], Colorado [SRC-330]); Kenya Data Protection Act 2019 s43(1), (2), (4), (5), (7) [SRC-106]; Kenya Data Protection (General) Regulations 2021 reg 37, reg 38, Second Schedule [SRC-107]; POPIA s22 [SRC-104]; Information Regulator eServices guide [SRC-105]; Ghana Data Protection Act 2012 (Act 843) s31 [SRC-109]; NIST SP 800-61 Rev. 3 GV.OC-03.R1, RS.CO-02.R3, RC.CO-04.R1 [SRC-054] (ADVISORY).

**AI Agent Instruction.** Never send, draft for sending, or publish a breach notice on your own. If you find a possible breach, record the time you found it, report it, and point to the runbook. Never state whether a breach is reportable as fact; mark it as ASSUMPTION for the privacy owner to decide.
