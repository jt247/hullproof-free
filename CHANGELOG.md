# Changelog

All notable changes to Hullproof are recorded here. Versions follow semantic versioning: a major version changes or removes requirements, a minor version adds requirements or a new audit capability (such as running the audit in another AI tool), and a patch fixes wording.

## [Unreleased]

### Changed

- The README links the Hullproof Pro checkout in place of the waitlist, and every free audit report note now ends with the same link.

## [0.3.0] 2026-10-06

The free edition holds 110 requirements (every BLOCKER and every CRITICAL), 154 cited sources and a 110 item pre launch checklist. This release adds tool coverage and an installer. It adds no requirements.

### Added

- Tool coverage. The kit now has a folder in `kit/editors/` for fifteen AI tools: Claude Code, Codex, Antigravity, Gemini CLI, Cursor, Windsurf and Devin, GitHub Copilot, Lovable, Replit, Bolt, Emergent, v0, ChatGPT, Claude.ai and the Gemini app. Each folder holds the files the tool reads, a tool page with the install, first run, limits and enforcement line, and a `TOOL.json`.
- Installer, `tools/hullproof/install.mjs`. `node tools/hullproof/install.mjs --tool <name> --write` copies the files for one tool and prints the trust note, the enforcement label and the first thing to run. It does a dry run unless you add `--write`, never overwrites a file of yours, and writes only inside the project folder.
- Audit prompts written for the free scope, in a full and a short version, and an install by chat prompt, in `kit/prompts/`. They run the audit in a tool with no helper agents and no hook.
- Hook adapters in `tools/hullproof/hooks/` and an audit mode switch for Codex, Antigravity, Gemini CLI, Cursor, Windsurf and Copilot. Their hooks enforce only while `docs/security/.audit-mode` exists or `HULLPROOF_AUDIT=1` is set.
- Every free audit report now ends with a short note on what this run covered and what the Pro edition adds. The counts come from the build.

### Changed

- The README has a Works with your AI tool section, and the Update steps copy `editors/` and `prompts/` too.

## [0.2.0] 2026-10-06

The free edition holds 110 requirements (every BLOCKER and every CRITICAL), 154 cited sources and a 110 item pre launch checklist. No requirement was added or changed.

### Added

- Finding classes in `STANDARD.md`. A failed requirement can now say what evidence backs it: a traced path to harm (FINDING), a required control or record that is absent (MISSING CONTROL RECORD), or another layer that prevents the harm, shown as code (HARDENING NOTE). A class never changes the result of a requirement or the gate, and a HARDENING NOTE is never allowed under a BLOCKER requirement.
- A Class row in each finding of the audit report template, and an optional HARDENING NOTES section.
- An Update section in the README, with the commands to move to a newer release without keeping old files by mistake.

### Changed

- Gate condition G-2 says that a report that is incomplete, or that covers only part of the scope, can support NOT READY only.
- The absence searches in `STANDARD.md` leave out the kit's own folders, which name every term and so could never return a count of zero.
- The README describes what Hullproof Pro is and links the waitlist. It no longer carries purchase terms, which are in the Pro package. LICENSING.md has the same change.
- The package check fails the build if any file of this edition names a Pro only skill, agent or file.

## [0.1.3] 2026-10-05

The free edition holds 110 requirements (every BLOCKER and every CRITICAL), 154 cited sources and a 110 item pre launch checklist.

### Added

- A "What Pro adds" table in the README that shows, area by area, what the free edition covers and what Hullproof Pro adds. It does not list Pro requirements.
- A "Get notified when Pro launches" section, a short note on how Hullproof relates to tools that hunt for vulnerabilities, and a "Sample audit" section.
- A closing line on the audit report template and in the results step of `/hullproof-prelaunch` that says the report covers the free requirements and how many further requirements the Pro edition checks in the same run.

### Changed

- Terms for Hullproof Pro are described in the README and in LICENSING.md: delivery as a download from the checkout provider, access to the latest version through the provider's customer portal, update announcements on the Releases page of this repository, no refunds once delivered, and support through issues on this repository.

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
