# Hullproof: Security Operating Rules

These rules apply to every change in this project. Load them by adding `@docs/hullproof/HULLPROOF.md` to the project's root `CLAUDE.md`. This file is the only one loaded every session. Scoped rules in `.claude/rules/hullproof/` load automatically when you touch matching files. The standards below are large: read the one you need when you need it, starting with its Coverage map, and never import them with `@`.

## Standards

Read the applicable document before changing the matching area. All paths are in `docs/hullproof/`.

| Area | Document |
|------|----------|
| Master standard, severity, stages, release gate | `STANDARD.md` |
| Authentication, sessions, authorization | `AUTH.md` |
| APIs, webhooks, rate limiting, payments | `API-SECURITY.md` |
| Server side code: injection, internal routes, jobs, SSRF, file uploads | `BACKEND-SECURITY.md` |
| Databases, migrations, row level security | `DATABASE-SECURITY.md` |
| AI features, prompts, model output, tools | `AI-SECURITY.md` |
| Secrets and keys | `SECRETS.md` |
| Release readiness | `PRE-LAUNCH-AUDIT.md` |
| Quick start: the most common failures, each with a five minute check | `LITE-CHECKLIST.md` (read it first if you are new) |
| Governance, threat modeling | `GOVERNANCE.md` (read when designing or before release) |

**Read order.** On a new project, read `LITE-CHECKLIST.md` first, then `STANDARD.md` for the stages, severity and release gate, then the one domain document that matches your change.


**Read one requirement, not a whole document.** Open the document's Coverage map and find the rows for your change. Run `grep -n '^### SEC-' docs/hullproof/AUTH.md` (use the document you need) to list every requirement heading with its line number. Then read only that block: the Read tool with an offset and a limit of about 60 lines, or `sed -n '120,185p' docs/hullproof/AUTH.md`. The Verify, Evidence and Exceptions fields are the ones you need.

Other domains (frontend, data protection, privacy, dependencies, infrastructure, observability, incident response, mobile, agentic development) are indexed in `STANDARD.md`. A domain document missing from your edition is not part of it.

## Hard rules

1. Security is a design input. Decide controls before writing code, not after.
2. Read the applicable standard before modifying authentication, authorization, APIs, backend services, databases, file storage, infrastructure, payments, or AI functionality.
3. Frontend controls are never security controls. Hiding a button or validating a form in the browser protects nothing.
4. Never expose credentials, tokens, private keys, service role keys, database credentials, or privileged secrets to client code, client bundles, public environment variables, logs, or error messages.
5. Authorization is deny by default and enforced server side on every request, for every resource, including ownership and tenant checks.
6. Apply least privilege to users, service accounts, database roles, API keys, and AI tools.
7. Treat all input as untrusted: request bodies, headers, query strings, files, webhooks, third party API responses, and model output. Validate it against a schema and constrain size, type, and range on the server.
8. Never invent cryptography, token formats, or password hashing. Use established libraries and platform controls.
9. Never weaken an existing security control to make an implementation easier. This includes disabling row level security, widening CORS, skipping signature checks, and broadening roles. If a control blocks you, stop and report it.
10. Preserve auditability. Do not remove audit logs, security events, or the history needed to reconstruct who did what.

## How to report

1. **Flag assumptions.** Start any security relevant claim you have not verified with `ASSUMPTION:`.
2. **Separate findings.** Label each one `VERIFIED` (reproduced, or proven from code) or `SUSPECTED` (pattern match, not confirmed). Never present a suspected finding as verified. Say what evidence backs each finding: a traced path to harm, a required control or record that is absent, or another layer that prevents the harm, shown as code. The last kind is a HARDENING NOTE, and it never lowers a BLOCKER requirement (see Finding classes in `STANDARD.md`).
3. **Rate severity** with the scale and the ordered rating rules in the Severity section of `docs/hullproof/STANDARD.md`: BLOCKER, CRITICAL, HIGH, MEDIUM, LOW. A finding under a named BLOCKER requirement is never rated below CRITICAL. Rating it CRITICAL instead of BLOCKER is a lowering, and it stands only with code evidence in the finding and a reviewer who did not write the code or the rating. A finding rated below its BLOCKER requirement goes in the Lowered BLOCKER requirements table.
4. **List what you could not assess** and why, under UNVERIFIED CONTROLS, with one routed state per item: NEEDS DASHBOARD, NEEDS BUILD, NEEDS DYNAMIC TEST, ASK OWNER, ATTESTATION or UNKNOWN, and the owner action that closes it. A code trace that proves a control is `PASS (static)`. An unchecked control counts as unknown, never as passing, and a run that only reads code cannot end READY while any BLOCKER or CRITICAL item is NOT ASSESSED. Audit reports follow `docs/hullproof/templates/AUDIT-REPORT.md`.
5. **Document architecture changes.** Any change that alters a trust boundary, auth flow, data access path, or secret handling gets a short note in the project's security decisions log, saying what changed, why, and what risk it accepts.
6. **Never mark a production readiness task complete** while any BLOCKER or CRITICAL finding is unresolved or unsettled. An item left NOT ASSESSED counts as open. BLOCKER findings cannot be accepted as exceptions, and neither can CRITICAL findings in credentials and secrets exposure, authentication, tenant isolation or payments (acceptance, not rating; see the Severity rules). A CRITICAL finding can be accepted only in writing, with a named owner, an approver, a compensating control, an expiry date and the term limits in `STANDARD.md`.

## Process

DESIGN → THREAT MODEL → IMPLEMENT → STATIC REVIEW → SECURITY REVIEW → TEST → PRE-LAUNCH AUDIT → RELEASE

| Stage | Exit condition |
|-------|----------------|
| DESIGN | Data flows, trust boundaries, and required controls are written down. |
| THREAT MODEL | Threats and mitigations are recorded. A change that meets a trigger in a Pro edition requirement (a new trust boundary or entry point, a new external service or model provider, a change to an auth, session or role flow, money, tenant isolation, an AI feature or tool, or agent access to secrets) needs a FULL model. Any other change in an area in hard rule 2 needs a DELTA note (a Pro edition requirement). Other changes need neither. See `GOVERNANCE.md`. |
| IMPLEMENT | Code follows the applicable standards. Security tests are written alongside the feature. |
| STATIC REVIEW | Linters, type checks, secret scanning (e.g. Gitleaks), static analysis (e.g. Semgrep), and dependency scanning (e.g. OSV Scanner) pass. |
| SECURITY REVIEW | The diff is reviewed against the standards. Findings are rated and labelled. |
| TEST | Authorization, validation, and abuse cases are tested, including negative cases. The tests for the BLOCKER areas that apply to the product exist and run (a Pro edition requirement). |
| PRE-LAUNCH AUDIT | `docs/hullproof/PRE-LAUNCH-AUDIT.md` passes with no open BLOCKER or CRITICAL findings. |
| RELEASE | Rollback path is known. Monitoring for security events is live. |

Do not skip a stage silently. If a stage is skipped, say which one and why.

## Skills

Run these by typing the command. Each reads the standard at run time and writes its report into the project.

**The hook.** The read only agents run under a hook in `.claude/hooks/` that blocks any shell command outside a short allowlist: git history commands, `ls`, `wc`, `grep`, `find` without `-exec` or `-delete`, `sed -n`, `awk` without `system()` or redirection, `jq`, the kit manifest check (`shasum -a 256 -c docs/hullproof/.kit-manifest`, exact form only), `gitleaks` with `--redact` and the kit configuration (`--config tools/hullproof/gitleaks.toml`, no other config path), and (for the pre launch auditor) read only `curl` to the Live target in `docs/security/STAGE.md`. It fails closed: input it cannot read, or an internal error, blocks the command. It needs Node and runs only after you accept Claude Code's workspace trust prompt for the project. The hook is attached to each skill with the profile `skill` and to each agent that has Bash with its own profile. The matcher is `Bash|Read|Grep|Glob`, so it also blocks reads, searches and listings of known secret file names such as `.env*` and key files. It judges the path, not the content of a file. It blocks every command outside the allowed forms, and a blocked command is not put to the user as a question. The `allowed-tools` line of a skill pre approves only the exact forms it lists, so an allowed form that is not pre approved may ask you for permission. The hook is the only enforced limit on what a run reads and executes. The agents have no Write tool. The skills write their own report with the Write tool. A skill's `allowed-tools` line pre approves the write only for Markdown files in `docs/security/reports/` (the threat model skill: `docs/security/threat-models/`), with an `Edit(docs/security/reports/*.md)` rule, because Claude Code checks file permissions against Edit rules only, an Edit rule also governs the Write tool, and a `Write(...)` path rule is never consulted. The report folder must exist before the run, and the skill creates no folder, and the hook decides each Write by path and never lets a run write the hook, the agents, the skills, the standards, the settings or source files. The Write limit is path based, with a scan for secret shaped values, and it does not judge the rest of the text, so the rule that a skill writes only its own report is partly an instruction. The hook also blocks reading `.git/config` and searching its contents in every profile, because a remote URL can hold a token. The written rules in the agent and skill files are instructions a model can ignore.



If the hook file is missing, switched off or a stub, Claude Code treats it as a non blocking error and nothing is limited. So each agent that has a shell tool (the pre launch auditor) starts with a probe: its first shell command is `hullproof-hook-probe`, which is not a real command, and a working hook blocks it with a message containing `HULLPROOF HOOK ACTIVE`. The agent then prints `HOOK: ACTIVE` or `HOOK: INACTIVE` as the first line of its output and makes no shell call after `INACTIVE`. Its second command checks the kit against `docs/hullproof/.kit-manifest` with `shasum -a 256 -c`, and prints `KIT: verified`, `KIT: MISMATCH` (it then stops) or `KIT: NOT VERIFIED` (no manifest). You can run the hook's own test with `node .claude/hooks/hullproof-readonly-bash.mjs --selftest`. Run the agents only on repositories you trust.

| Command | Use it | Output |
|---------|--------|--------|
| `/hullproof-prelaunch` | Before every production release | `docs/security/reports/PRE-LAUNCH-RESULTS-<date>.md` and the gate outcome |

The skills take their answers as arguments (`stage=GROWTH markets=NG,EU live=no`) or from `docs/security/STAGE.md`, and ask only for what is still missing. Reports list exploitable findings, so keep `docs/security/reports/` out of any public repo (the skills warn when it is not git ignored).


## Templates

Fill in the blank templates in `docs/hullproof/templates/` and keep the filled copies in `docs/security/` (private location if the repo is public).

| Template | Use it for |
|----------|-----------|
| `STAGE.md` | Stage, markets, release scope and where records live. Read first by every run. |
| `AUDIT-REPORT.md`, `THREAT-MODEL.md`, `AI-THREAT-MODEL.md` | Audit reports and threat models |
| `ACCEPTED-RISK.md` | Written acceptance of a CRITICAL or HIGH finding outside the protected classes (HIGH acceptances last at most 180 days) |
| `BREACH-RUNBOOK.md` | Breach decision tree, notices per market, and the breach register |
| `PROVIDER-EXPORTS.md`, `STAGING-TEST-WINDOW.md` | Closing items a static run cannot settle |
