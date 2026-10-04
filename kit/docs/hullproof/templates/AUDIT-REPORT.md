# Security Audit Report Template

Every Hullproof audit, whether run by an agent or a person, produces a report in this format. In the free edition you can fill it in by hand, or have a reviewer fill it in, from the `/hullproof-prelaunch` results table; that report satisfies G-2 when it covers every BLOCKER and CRITICAL requirement. The `/hullproof-security-audit` skill writes it to `docs/security/reports/SECURITY-AUDIT-REPORT.md` unless the user names another path. A report lists exploitable findings, so keep its folder out of any public repo (add it to `.gitignore`); the skill warns when the path is not ignored. Keep earlier reports: a re run after fixes is a new report for the new commit, never an edit of the old one. A report is never overwritten. Before a new report replaces an existing one, the old one is copied unchanged to `docs/security/reports/<name>-<sha7>-<date>.md` (a name that already exists gets a counter, and an old report that holds a secret value is not copied: stop and ask the owner to scrub it). The report text is checked for secret values before it is written, and it quotes no commit message (give the commit hash only).

The findings sections are fixed and always appear in this order, even when empty (write "None."): BLOCKERS, CRITICAL, HIGH, MEDIUM, LOW, PASSED CONTROLS, UNVERIFIED CONTROLS, RECOMMENDED NEXT ACTIONS. Sections marked optional appear only when they apply. A large audit (more than about 30 findings) should use them, because a flat list cannot be planned from.

```markdown
# Security Audit: [Product name]

| Field | Value |
|-------|-------|
| Audit date | YYYY-MM-DD |
| Commit audited | Full commit SHA |
| Branch | |
| Working tree | Clean, or dirty (the results do not describe the commit) |
| Scope | Paths or "full" |
| Live target tested | URL, or "none (static only)" |
| Audit type | CODE ONLY, or CODE AND LIVE |
| Release scope | Which of web, mobile and API ship. Requirements for targets that do not ship are NOT APPLICABLE, out of release scope. |
| Live in production | Yes or no. Yes starts breach triage if a personal data exposure is verified. |
| Report folder ignored by git | Yes or no (`git check-ignore`) |
| Project stage | The declared stage (LAUNCH, GROWTH or SCALE) and the derived stage. Only requirements at or below the stage in force are scored, and the declared stage is never lower than the derived one. |
| Stage triggers found | Each trigger with file and line (payments, roles besides the owner, shared workspaces, business customer data, enterprise or regulation markers), or "none found" |
| Markets served | Countries or regions, from `docs/security/STAGE.md` or the user |
| Hullproof version | From the Version line in `docs/hullproof/STANDARD.md` |
| Edition and scope | Hullproof Pro (full standard), or Hullproof Free (free scope: the BLOCKER and CRITICAL requirements only; HIGH, MEDIUM and LOW requirements are NOT EVALUATED and G-6 is outside the scope) |
| Author | The tool and run id, or the person who wrote this report. A report with no author field is not reused. |
| Evidence folder | The named folder that holds the scan output, exports and test records for this commit |
| Hook and kit check | HOOK: ACTIVE or INACTIVE (probe result), and KIT: verified, MISMATCH or NOT VERIFIED (manifest check) |

## Verdict

**[NOT READY | READY WITH ACCEPTED RISK | READY]**: one sentence on why. In the free edition write READY (FREE SCOPE) or READY WITH ACCEPTED RISK (FREE SCOPE); it means the gate was met for the free edition's requirement set only, and it says nothing about HIGH, MEDIUM or LOW findings.

The verdict is the Production Security Gate outcome from `docs/hullproof/STANDARD.md`.

| Gate | Condition (short form, see STANDARD.md) | Met? | Note |
|------|------------------------------------------|------|------|
| G-1 | Stage declared and recorded with file and date, not lower than the derived stage | YES or NO | |
| G-2 | Audit report written by the auditor for this commit and release (one still in progress does not count) | YES or NO | |
| G-3 | No open BLOCKER finding, verified or suspected; a lowered FAIL under a BLOCKER requirement still counts; Lowered BLOCKER requirements table reviewed | YES or NO | |
| G-4 | Every BLOCKER requirement is PASS or NOT APPLICABLE: none FAIL (at any rating) or in UNVERIFIED CONTROLS (any state); worse status wins if a pre launch checklist differs | YES or NO | |
| G-5 | Every CRITICAL requirement PASS or NOT APPLICABLE, or (FAIL or unsettled) resolved or, outside credentials and secrets, authentication, tenant isolation and payments, under a current written acceptance within the limits | YES or NO | |
| G-6 | Every HIGH resolved or accepted with owner and fix date within 180 days | YES or NO (free edition: outside the scope) | |
| G-7 | Secret, static and dependency scans ran on this commit with the kit's own configuration and their output files name the commit; requirements whose static check did not run are listed | YES or NO | |
| G-8 | Rollback path known, secrets re checked after rollback | YES or NO | |

| Severity | Open | Verified | Suspected |
|----------|------|----------|-----------|
| BLOCKER | | | |
| CRITICAL | | | |
| HIGH | | | |
| MEDIUM | | | |
| LOW | | | |

## Breach triage (optional, only when a verified personal data exposure is live)

Placed ahead of BLOCKERS. This is triage, not a legal determination. Notification clocks run from when the owner became aware.

| Field | Value |
|-------|-------|
| Finding | F-NN and a one line description |
| Data exposed | Types of personal data, and how many people can be named (number or "unknown") |
| Exposure window start | The commit that introduced it (`git log`), and the date it reached production (from the owner) |
| Exposure window end | The date the exposure was closed, or "still open" |
| Evidence of access | Logs or exports checked for use of the exposure, or "none checked" |
| Owner became aware | Date and time |
| Markets and clocks | For example NG and EU, 72 hours from awareness; see `docs/hullproof/INCIDENT-RESPONSE.md` |
| First steps taken | Contain, preserve evidence, assess, notify (see `templates/BREACH-RUNBOOK.md`) |
| Decision owner | Name |

## System profile

| Item | What was found | Where |
|------|----------------|-------|
| Architecture | Monolith, monorepo, services, serverless, and how they connect | file paths |
| Languages and frameworks | | |
| Trust boundaries | Browser to server, server to database, webhooks in, third party calls out, admin surfaces | |
| Authentication | Provider, session type, MFA, OAuth | |
| Authorization | Where access checks run: middleware, route handlers, row level security, roles | |
| External services | Payments, email, analytics, AI providers, webhooks | |
| Secrets handling | Where secrets load, which reach client code, env files present | |
| Database | Engine, provider, how the app connects | |
| Storage | Buckets, file uploads, public or private | |
| AI capabilities | Models called, retrieval, tools the model can trigger, or "none" | |

Applicable standards read: list each `docs/hullproof/*.md` used and why it applied.

## Gates

Copy the gate answers from the Gates section of `docs/security/STAGE.md`, or record the answers given in this run. A gate answered No marks its IDs NOT APPLICABLE, and each such result names the gate. A BLOCKER is NOT APPLICABLE through a gate only when the owner's search is recorded (commit, exact patterns, result counts) and the auditor re ran it in this session over every tracked file except dependency folders and found nothing. The owner's statement alone never clears a BLOCKER.

| Gate | Answer (Yes, No or not answered) | Owner's evidence (commit, exact patterns, result counts) | Auditor re run (command, files searched, count) | IDs marked NOT APPLICABLE |
|------|----------------------------------|----------------------------------------------------------|--------------------------------------------------|---------------------------|
| GATE-TOOLS | | | | |

## Strengths

Controls that are present and working, with file locations. Credit them so they are not removed later.

## Domain scorecard

| Domain | Status | Note |
|--------|--------|------|
| AUTH | PASS, WARN, FAIL, or N/A | |
| AUTHZ | | |
| API | | |
| WEB | | |
| DB | | |
| DATA | | |
| SECRETS | | |
| AI | | |
| AGENT | | |
| SUPPLY | | |
| CLOUD | | |
| MOBILE | | |
| LOG | | |
| GOV | | |

## Merge record (optional)

How findings were combined, so a reader can trace a finding back to its sources.

| Finding | Merged from | Raised by | Note |
|---------|-------------|-----------|------|
| F-NN | Reviewer or tool item ids | Reviewers and tools that reported it | For example "same root cause, severity taken from the highest assessed" |

## Reviewer disagreements (optional)

| Finding or item | Assessor A and rating | Assessor B and rating | Rating that stands, and why |
|-----------------|-----------------------|-----------------------|-----------------------------|
| F-NN | | | The higher rating stands unless the lower assessor shows its premise is wrong |

## Lowered BLOCKER requirements (mandatory when any finding is rated below a BLOCKER requirement it breaks)

"Cannot be waived" governs acceptance, not rating (Severity rule 6 in `docs/hullproof/STANDARD.md`). A finding under a BLOCKER requirement is never rated below CRITICAL. Every finding rated CRITICAL instead of BLOCKER is listed here so the gate (G-3) can review it, with an independent reviewer: a person or an agent session that did not write the code and did not write the rating. A row with no reviewer, or with evidence that does not hold, counts as a BLOCKER. A lowered finding never satisfies G-3 or G-4 and is never accepted. "None." if there are none.

| Finding | Requirement | Requirement severity | Rating given (CRITICAL at the lowest) | Code evidence for the lower rating | Independent reviewer (name or session, and date; PENDING if none) |
|---------|-------------|----------------------|----------------------------------------|-------------------------------------|---------------------------------------------------------------------|
| F-NN | SEC-[DOMAIN]-[NUMBER] | BLOCKER | | file:line and the reach or impact limit it shows. An identifier precondition alone is never enough. | |

## BLOCKER coverage (optional)

One row for every BLOCKER requirement in scope, so gate G-4 can be read at a glance.

| Requirement | State | Finding or evidence | Owner action to close |
|-------------|-------|---------------------|-----------------------|
| SEC-[DOMAIN]-[NUMBER] | PASS (static), FAIL, NEEDS DASHBOARD, NEEDS BUILD, NEEDS DYNAMIC TEST, ASK OWNER, ATTESTATION, UNKNOWN or NOT APPLICABLE | F-NN, file:line, or for NOT APPLICABLE the gate name and the evidence of absence | |

## Discovery cross check (optional)

Every claim from the discovery profile is a hypothesis. Record what the reviewers found.

| Discovery claim | Result (CONFIRMED, REJECTED, PARTLY) | Evidence | Correction made to the profile |
|-----------------|---------------------------------------|----------|--------------------------------|

## Owner questions (optional)

Grouped by the owner action that answers them, so one export or one test session closes many.

| # | Question | Requirements it settles | Evidence to attach |
|---|----------|--------------------------|--------------------|

## BLOCKERS

Each finding uses the block below. Order within a section by how easily it can be exploited.

### F-01: [Short title]

| Field | Value |
|-------|-------|
| Requirement | SEC-[DOMAIN]-[NUMBER], plus any others the same root cause breaks. Use the tag `gap in standard` if no requirement fits. |
| Root cause | Short label. Findings with one cause share it, so the number of fixes is visible. |
| Raised by | Reviewers and tools that reported it (optional) |
| Severity | BLOCKER, CRITICAL, HIGH, MEDIUM or LOW, from the ordered rules in the Severity section of `docs/hullproof/STANDARD.md`. If it differs from the requirement's own severity, say why. Below a BLOCKER requirement: also list it in Lowered BLOCKER requirements. |
| Confidence | VERIFIED (reproduced, or proven from code) or SUSPECTED (pattern match, not confirmed) |
| Location | file:line, endpoint, or setting |
| Exploitability | Who can trigger it, what they need, and what they gain. Say "demonstrated" only if it was actually reproduced in this audit. |
| Remediation | The change needed, specific to this codebase, and how to confirm the fix |
| Evidence | Code excerpt, tool output, or probe result. Never include secret values: give location and type only. |

## CRITICAL

## HIGH

## MEDIUM

## LOW

## PASSED CONTROLS

| Requirement | Evidence seen |
|-------------|---------------|
| SEC-[DOMAIN]-[NUMBER] | file:line, config, or tool result that shows the control works |

## UNVERIFIED CONTROLS

Every requirement in scope that could not be settled, and why. This is what `docs/hullproof/STANDARD.md` gate G-4 calls NOT ASSESSED, and the states below are the NOT ASSESSED sub states defined in its Result states section. Each item stays unknown until someone confirms it and is never counted as passing. Mark BLOCKER and CRITICAL requirements clearly, because an unsettled BLOCKER or CRITICAL requirement counts as open and holds the gate (G-4, G-5). Unsettled HIGH requirements stay here with their owner action. Every row carries one routed state and the owner action that closes it.

| Requirement | Severity | State | Why it could not be settled | Owner action |
|-------------|----------|-------|-----------------------------|--------------|
| SEC-[DOMAIN]-[NUMBER] | | NEEDS DASHBOARD, NEEDS BUILD, NEEDS DYNAMIC TEST, ASK OWNER, ATTESTATION or UNKNOWN | For example: provider setting, no build from this commit, two user test not permitted, tool not installed | For example: export per `templates/PROVIDER-EXPORTS.md`, or a session per `templates/STAGING-TEST-WINDOW.md` |

## RECOMMENDED NEXT ACTIONS

Numbered, in the order they should be done. Severity order is the default: fix BLOCKERS first, then close UNVERIFIED BLOCKER requirements, then CRITICAL and HIGH. Dependency order is allowed and preferred where it matters, for example containing exposed secrets before anything else, or locking down the data API before fixing individual routes; say when an action sits above its severity for that reason. Name the finding or requirement each action closes.

### Remediation groups (optional)

The same actions grouped by root cause and phase, so the number of fixes is clear.

| Group | Root cause | Findings closed | Phase (contain, fix, verify, harden) | Depends on |
|-------|------------|-----------------|---------------------------------------|------------|

## Tool output

| Tool | Version | Config used | Commit named in the output | Result |
|------|---------|-------------|----------------------------|--------|
| Secret scan (Gitleaks) | or "not run: reason" | The kit config `tools/hullproof/gitleaks.toml`, with inline allow tags ignored | | |
| Static analysis (Semgrep) | | The kit rules `tools/hullproof/rules` | | |
| Dependency scan (OSV Scanner) | Hits classed as direct runtime, transitive runtime, or dev and build only | | | |
| Outdated packages | | | | |
| Working tree secret scan (`gitleaks dir . --redact`) | or "not run: reason" | | | |
| Build output secret scan (`gitleaks dir <build> --redact`) | or "not run: reason". Build commit must equal the audited commit. | | | |
| Header probe (curl) | | | | |
| Repository owned scanner config found (`.gitleaks.toml`, `.gitleaksignore`, `.semgrepignore`, `osv-scanner.toml`, inline `gitleaks:allow` or `nosemgrep`) | | Reported as findings, not honoured as BLOCKER evidence | | List each file and what it excludes, or "None." |

Files scanned against files tracked, and whether the clone is shallow: state both. Requirements whose static check did not run (for gate G-7): list each, or "None."

## Limits

This report reflects the commit and date above. It is based on code review, tool output, and live testing where stated, not on production traffic or runtime monitoring. No exploitation is claimed unless a finding says it was demonstrated. A READY verdict means the known risks covered by Hullproof at the declared stage were checked and resolved, not that the application is secure. READY (FREE SCOPE) covers only the BLOCKER and CRITICAL requirements and says nothing about HIGH, MEDIUM or LOW findings.
```

For a code change audit or an API review, keep the header, the severity count table, and the eight findings sections, and skip the system profile, strengths and domain scorecard. Any audit report states the gate outcome its evidence can support and names the G conditions it could not evaluate. A partial review can support NOT READY, never READY or READY WITH ACCEPTED RISK.
