# Changelog

All notable changes to Hullproof are recorded here. Versions follow semantic versioning: a major version changes or removes requirements, a minor version adds requirements or a new audit capability (such as running the audit in another AI tool), and a patch fixes wording.

## [Unreleased]

Nothing yet.

## [0.4.0] 2026-10-11

The free edition holds 110 requirements (every BLOCKER and every CRITICAL), 154 cited sources and a 110 item pre launch checklist. Why this is a minor release: the standard gained new requirements in the Pro edition, and the free kit gains the release gate and the record validators. None of the new requirements is a BLOCKER or a CRITICAL, so the free requirements are the same as in 0.3.1.

### Added

- The release gate (`tools/hullproof/ci/hullproof-gate.mjs`), the two record validators (`validate-findings.mjs` and `validate-surface-ledger.mjs`), their shared module (`hullproof-records-common.mjs`) and the CI README, now in the free kit under the Apache License 2.0.
- The two record schemas, `docs/hullproof/findings.schema.json` and `docs/hullproof/surface-ledger.schema.json`, under the Apache License 2.0.
- A free controls file, `docs/hullproof/security-controls.json`, that holds the 110 free requirements as data for the gate, the validators and other tools. It is under CC BY-SA 4.0, the same licence as the documentation it repeats.
- Findings schema 1.1.0. A fail record may carry a `machine_evidence` block that names the tool, the rule id, the tool version and the hash of the configuration used. A SUSPECTED finding with machine evidence may leave out `boundary` and `trace`, and a VERIFIED finding still needs both. Version 1.0.0 files stay valid.
- The `deterministic_only` reason for an incomplete findings record. It marks a run in which no model ran, so no verifier ran, by design.
- The Hullproof Engine, a separate public repository at https://github.com/jt247/hullproof-engine. It discovers any stack and cloud, runs the scanners you have installed, runs executable checks, and writes a deterministic report and gate result. It runs on this free kit alone. See the README.
- The engine is now inside the release zip, in `engine/`, and the upload pack is inside it too, in `pack/`. The zip is the one file to download for this edition. The pack was a separate download (`hullproof-free-pack-0.4.0.zip`) in the first 0.4.0 build; the same file now sits in `pack/` and is no longer released on its own.
- The engine's code map (Phase 2) is part of 0.4.0 as an addition. It was finished after the first 0.4.0 upload of the engine, and the engine version stays 0.4.0, so an engine zip downloaded earlier on 2026-10-11 does not have it. The code map lists every entry point it can find with what protects it, for Node and TypeScript, Python, Go, Ruby on Rails, PHP and Laravel, and Expo, and it adds checks that read the map. Those checks are leads until they are measured. Names of sign in helpers the engine does not know can be listed in `.hullproof/kit.local.json`.

### Changed

- The authority line in `STANDARD.md`. A repository check may record FAIL on a dashboard or runtime requirement for the part a file settles, for example no header configuration anywhere in the repository. It never records PASS for such a requirement. After the fix the requirement returns to its NOT ASSESSED sub state until the live evidence is supplied.
- SEC-SUPPLY-002 now says that a dependency with a known advisory fails the requirement, rated by the advisory level and reachability under Dependency advisories, and not at the severity of the requirement.
- `LICENSING.md` lists the gate, the validators and the schemas as code under the Apache License 2.0, and the free controls file as documentation under CC BY-SA 4.0.
- The README has a section on the Hullproof Engine and lists the gate and the controls file among the contents of the free edition.

### Not changed

- No free requirement was added, removed or re rated, and no stage or severity changed.
- The gate arithmetic, the finding classes and the enforcement labels are the same. Every tool is partial or advisory, and none is labelled enforced.
- The audit runs no code from the audited repository.

### Limits of this release

- The engine's coverage is partial, its taint rules are leads until they are measured, OSV Scanner runs only when you allow network access, and some scanners must be installed by you.
- Claude Code unattended runs can be stopped by the model provider's safeguards partway through. Nothing in your project changes when that happens. Run the same command again on the same commit.

## [0.3.1] 2026-10-10

The free edition holds 110 requirements (every BLOCKER and every CRITICAL), 154 cited sources and a 110 item pre launch checklist. This release is a patch. No requirement was added, removed or re rated, and no stage or severity changed. The new scripts and scanner rules serve checks the standard already asks for, such as the scanner output that gate condition G-7 needs.

### Added

- Scan wrapper, `tools/hullproof/scan.sh`. It runs Gitleaks, Semgrep and OSV Scanner, each only when installed, with the kit's own configuration, and writes each output with a JSON file beside it that records the commit, the tree, the tool and its version, the hash of the configuration used, the files scanned and the files tracked. OSV Scanner runs only with `--allow-network`. It refuses to run when `.git/config` holds a setting that could run code from the folder, and it writes only to the folder you name.
- Nine Semgrep rules, each with a fixture: a signature check whose result is never read, a `NEXT_PUBLIC_` variable named like a secret, a route handler that reads data and never touches a session, a log call that receives a token or a whole session, a read by id with no owner filter, `permissions: write-all` in a workflow, event text expanded in a workflow `run` step, a long literal assigned to a secret name, and a zod schema that accepts a privilege field. The route handler rule and the read by id rule are confidence LOW and report leads only.
- `tools/hullproof/helpers/peek.sh FILE:LINE` prints one line of a file with secret shaped values masked.
- `tools/hullproof/helpers/owner_packet.py` reads the items a report could not settle and writes a filled `PROVIDER-EXPORTS.md`, grouped by provider, and a `STAGING-TEST-WINDOW.md`.
- The read only hook refuses `sed -n` on a file whose content holds a secret shaped value (Stripe, GitHub, Slack and AWS key shapes, a JWT, a private key header, a password inside a URL), and `cat` gets a clear message. Nothing the hook refused before is allowed now.
- `ledger.py` fails a `PASS (static)` row whose authority is not repo.
- `helpers/agent-rules.md` has a fixed list of root cause labels and a section on provider side objects.

### Changed

- The stage record asks three questions where it asked one: business customer data (GROWTH), questionnaires or audits as a standing condition of selling or an enterprise channel (SCALE), and sector regulation (SCALE). `/hullproof-prelaunch` and the audit prompts ask the same three. No stage moved.
- Scope notes in `AUTH.md`: SEC-AUTHZ-003 covers a missing owner check where the only boundary is a single owner, SEC-AUTHZ-013 covers reads and changes across tenants, and SEC-AUTH-002 covers signed tokens only.
- The pre launch auditor returns record lines only, with fixed codes for NOT APPLICABLE and NOT ASSESSED rows, and no exploit steps. It rates from the files first: when the repository files answer an item, the item is decided from the files, and NEEDS DYNAMIC TEST or UNKNOWN is kept for items a file cannot settle. `/hullproof-prelaunch` follows the same rule.
- The audit prompts ask for record fields only.
- The `server-action-no-auth` rule searches the whole function body, so an auth call inside a nested block counts.
- The calibration examples in `STANDARD.md` now say they apply to severity rules 1 to 4.
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
