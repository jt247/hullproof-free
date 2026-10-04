# Changelog

All notable changes to Hullproof are recorded here. Versions follow semantic versioning: a major version changes or removes requirements, a minor version adds requirements, and a patch fixes wording.

## [Unreleased]

Nothing yet.

## [0.1.2] 2026-10-04

The free edition holds 110 requirements (every BLOCKER and every CRITICAL), 154 cited sources and a 110 item pre launch checklist.

### Added

- A contact address in SECURITY.md for vulnerability reports. GitHub private vulnerability reporting is the second route, where the repository offers it.
- A statement in LICENSING.md of where the standard draws on OWASP and other share alike sources and that it restates them in its own words, a rule for files that exist in both editions, and a short statement on the use of the Hullproof name and the READY labels.
- Platform and version requirements, a Start here order, a step to fill in the audit report, and a section on the evidence a READY needs from the owner, in the README.
- A support route: GitHub issues on this repository.

### Changed

- The zip now holds one top level folder, `hullproof-free-0.1.2/`, so unzipping never spills files into the current folder. The install command uses the new path.
- The free edition no longer lists Pro requirement IDs or titles. Each domain document shows how many requirements Pro adds and a short description. Coverage map rows that hold only Pro requirements are gone, and other mentions read "a Pro edition requirement".
- Text derived from the CIS Docker Benchmark was removed or rewritten.
- Counts in the README and changelog are filled from the registry at build time.

## [0.1.1] 2026-10-04

### Added

- Three CRITICAL requirements: realtime channel authorization (SEC-AUTHZ-036), isolated frames for generated or supplied HTML (SEC-WEB-044) and no account wide credential in CI or an agent workspace (SEC-SUPPLY-035).
- An authority tag on every checklist item (repo, dashboard or runtime) that says what kind of evidence settles it.
- Kenya and Ghana market gates in the stage record, and a Policy values table in the standard that states the basis of every numeric value.
- A coverage ledger and provenance fields in the audit report template, route and handler enumeration recipes, an SSRF guard test harness, connector evidence recipes and an injection test corpus in the tools.

## [0.1.0] 2026-10-03

First release of the free edition. It holds every BLOCKER and every CRITICAL requirement.

### Added

- Security standard: a master standard, `docs/hullproof/STANDARD.md`, with severity rules, stages, risk acceptance and the Production Security Gate, plus domain standards for authentication and authorization, APIs, backend services, frontend, databases, secrets, data protection, privacy, AI features, agentic development, dependencies and CI, infrastructure, observability, incident response, governance and mobile apps.
- Requirements with a stable ID, a severity, a stage, verification steps, an evidence line and an instruction for AI agents. Cited sources are listed in `REFERENCES.md` with their licenses.
- The `/hullproof-prelaunch` skill and the `hullproof-pre-launch-auditor` agent, which check the release checklist in parallel, read only, and write a results file.
- A read only shell hook that fails closed, checks flags, schemes, hosts and paths, and ships with a self test and a kit manifest.
- Pre launch checklist results with routed NOT ASSESSED states (NEEDS DASHBOARD, NEEDS BUILD, NEEDS DYNAMIC TEST, ASK OWNER, ATTESTATION, UNKNOWN) and an owner action for each.
- The READY (FREE SCOPE) verdict. It means the free scope of the gate was met for the BLOCKER and CRITICAL requirements (G-1, G-2, G-3, G-4, G-5, G-7 and G-8). G-6 is outside the free scope, and the label says nothing about HIGH, MEDIUM or LOW findings.
- Twelve applicability gates with evidence of absence, a solo builder path and an ordered set of severity rules.
- Evidence freshness limits and limits on accepting a CRITICAL finding, labelled Hullproof policy.
- Findings under a named BLOCKER requirement are never rated below CRITICAL. A rating of CRITICAL instead of BLOCKER stands only with code evidence and a reviewer who is independent of the author.
- The auditor derives the stage from repository evidence and never lowers a declared stage. A market can be excluded only with a technical block or a zero count by country.
- Scanner rules: Semgrep rules with fixtures, a SQL policy helper and a Gitleaks configuration.
- Templates for the audit report, stage record, accepted risk, threat model, breach runbook, provider exports and staging test window.
- Scoped agent rules for authentication, API, database, AI, client code, infrastructure, payments and file storage.
- Licensing, notices and security: LICENSE (Apache License 2.0 for code), LICENSE-DOCS.md (CC BY-SA 4.0 for documentation), LICENSING.md, NOTICE.md with source credits and a not affiliated statement, SECURITY.md (GitHub private vulnerability reporting), and a License column in REFERENCES.md.
- All kit files sit under `docs/hullproof/`, `.claude/rules/hullproof/` and `hullproof-` names, so installing never overwrites your own files.
