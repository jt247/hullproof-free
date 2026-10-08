# Hullproof

A software security standard for teams that build with AI coding agents. It covers SaaS, AI applications, web apps, APIs, backend services, mobile apps, PostgreSQL databases, serverless functions, and cloud deployments.

Version 0.3.0. The free edition contains 110 requirements: every BLOCKER (44 of them) and every CRITICAL requirement. It also holds the Production Security Gate and a release checklist of 110 items. See [CHANGELOG.md](CHANGELOG.md).

## What Hullproof is

Hullproof is a kit you copy into your own project. It does two jobs.

1. It tells your AI coding agent what the security rules are, so the agent follows them whenever it touches security sensitive code.
2. It gives you a checklist and an auditor agent that test a release against those rules and write a report with evidence, so a person can decide whether to ship.

Every requirement has an ID such as `SEC-AUTH-002`, a severity, a way to check it, and the evidence to keep. Cited sources are listed in `kit/docs/hullproof/REFERENCES.md` (154 in this edition).

## What the free edition contains

| Part | Path | What it does |
|------|------|--------------|
| Agent instructions | `kit/docs/hullproof/HULLPROOF.md` | Security operating rules and the required development process |
| Master standard | `kit/docs/hullproof/STANDARD.md` | Severity rules, stages, risk acceptance and the Production Security Gate |
| Domain standards | `kit/docs/hullproof/*.md` | 110 requirements across the security domains, each with Verify steps and an Evidence line |
| Release checklist | `kit/docs/hullproof/PRE-LAUNCH-AUDIT.md` | 110 items to check before you ship |
| Short checklist | `kit/docs/hullproof/LITE-CHECKLIST.md` | The checks a solo builder can run alone, each linked to its full requirement |
| Skill | `kit/.claude/skills/hullproof-prelaunch/` | The `/hullproof-prelaunch` command, which runs the checklist and writes a results file |
| Agent | `kit/.claude/agents/hullproof-pre-launch-auditor.md` | Checks the items in parallel, read only |
| Hook | `kit/.claude/hooks/hullproof-readonly-bash.mjs` | Blocks shell commands outside a short read only list while the agent runs |
| Scoped rules | `kit/.claude/rules/hullproof/` | Short rules that load only when the agent edits matching files, such as auth, API, database, or AI code |
| Scanner rules | `kit/tools/hullproof/` | Semgrep rules with fixtures, a SQL policy helper and a Gitleaks configuration |
| AI tool files | `kit/editors/` | One folder for each of fifteen AI tools: rules, skills, agents, enforcement settings where the tool allows them, a tool page and a `TOOL.json` |
| Prompts | `kit/prompts/` | The single pass audit prompt (full and short) and the install by chat prompt, written for the free scope |
| Installer | `kit/tools/hullproof/install.mjs` | One command per tool, dry run by default |
| Templates | `kit/docs/hullproof/templates/` | Audit report, stage record, accepted risk, threat model, breach runbook, provider export and staging test templates |

## What Pro adds

Hullproof Pro is the paid edition. It holds 655 requirements and uses the same requirement IDs as this edition. The free edition already holds every BLOCKER and every CRITICAL requirement. The Pro requirements are not listed here. Each domain document in this edition says how many more requirements Pro holds for that domain and describes them in one sentence.

| Area | Free edition | Hullproof Pro |
|------|--------------|---------------|
| Requirements | Every BLOCKER and every CRITICAL requirement (110 in all, 44 of them BLOCKER) | All 655 requirements: the free set plus every HIGH, MEDIUM and LOW requirement |
| Release audit | `/hullproof-prelaunch` runs the release checklist and writes a results file | A full security audit that writes the audit report with evidence, and a verdict that includes HIGH findings |
| API review | The API requirements that are BLOCKER or CRITICAL | A review of your endpoints against the whole API standard |
| Threat model | A threat model template you fill in yourself | A threat model built with you from your repository |
| Reviewer agents | A read only pre launch auditor | The auditor plus further agents that review, hunt, check coverage and try to disprove findings |
| Machine readable requirements | None | A file of every requirement for your own tooling |
| CI gate | None | A CI gate example that reads the results table and blocks a release on open items |
| AI tools | Rules, skills, prompts and the installer for fifteen AI tools, scoped to the free requirements | The same tools with the full requirement set, the full audit prompt with the independent verifier flow and hunt cards, and an AI agent security prompt |
| Templates and checklists | Audit report, stage record, accepted risk, threat models, breach runbook, provider exports and staging test window | The same, plus further templates for incident response, ownership, inventories and policies, and the SaaS, API and AI checklists |

[Get Hullproof Pro](https://buy.polar.sh/polar_cl_QBorXMBiEvjQ9H6PFb0LDoD371YBsL83gYWrS4dOGuh) for 16.50 USD, taxes included. The first 500 buyers pay 13.25 USD with the code FIRST500. It is a one time purchase delivered as a zip, and updates replace the file in your customer portal. Purchase terms, licensing and support for Pro are in the Pro package.

## Works with your AI tool

Hullproof runs in the AI tool you already use: in its desktop app, in its command line tool or in VS Code, as an agent, as a rules file, as a pasted prompt, or installed by chat. One command puts the files for your tool in place: `node tools/hullproof/install.mjs --tool <name>` shows what it would do, and adding `--write` does it. It never overwrites a file of yours. The free audit prompt covers the free scope and ends every report with a short note on what the Pro edition adds.

| Tool | How to run | Enforcement |
|------|-----------|-------------|
| Claude Code | `/hullproof-prelaunch` | partial |
| Codex | `$hullproof-audit` | partial |
| Antigravity | `/hullproof-audit` | partial |
| Gemini CLI | Ask it to use the `hullproof-audit` skill | partial |
| Cursor | `/hullproof-audit` | partial |
| Windsurf and Devin | Ask the agent to run the `hullproof-audit` skill | partial |
| GitHub Copilot | `/hullproof-audit` | partial |
| Lovable | Install by chat, or paste the short prompt | advisory |
| Replit | Install by chat, or paste the short prompt | advisory |
| Bolt | Paste the short prompt in Plan mode | advisory |
| Emergent | Paste the short prompt in Plan mode | advisory |
| v0 | Paste the short prompt with Plan Mode ticked | advisory |
| ChatGPT | Run the audit prompt from a Project | advisory |
| Claude.ai | Run the audit prompt from a Project or skill | advisory |
| Gemini app | Paste the short prompt in a Gem or skill chat | advisory |

Only the labels in this table are enforced limits, and partial means some actions are blocked under stated conditions, such as a trusted folder and audit mode on. Advisory means nothing blocks anything. Everything else in the tool files is advice. Each tool has a page in `kit/editors/<tool>/README.md`, and `kit/editors/README.md` explains the labels, audit mode and install by chat.

## How Hullproof relates to bug hunting tools

Hullproof is a standard, a workflow and a release gate. It tells your coding agent what to build, checks what was built against written requirements, and records the evidence a person needs to decide whether to ship. Tools that hunt for vulnerabilities by scanning or probing a running system do a different job. They are complementary: their output can be evidence for a Hullproof requirement, and Hullproof tells you which checks you still owe before a release.

## Sample audit

[docs/SAMPLE-AUDIT-REPORT.md](docs/SAMPLE-AUDIT-REPORT.md) is the output of the free audit on the hullproof-demo app, a small app built with deliberate flaws for this purpose. The demo app is public at [github.com/jt247/hullproof-demo](https://github.com/jt247/hullproof-demo). Run your own audit on it first, then compare your results with its answer key. It is intentionally vulnerable, so never deploy it and never use real data in it.

## What READY (FREE SCOPE) means

The free scope is the BLOCKER and CRITICAL requirements. The Production Security Gate has eight conditions, G-1 to G-8. In the free scope they mean this:

| Condition | In the free scope |
|-----------|-------------------|
| G-1 | The stage is declared and recorded in `docs/security/STAGE.md` with the file and its date. |
| G-2 | An audit report in the `docs/hullproof/templates/AUDIT-REPORT.md` format that covers every BLOCKER and CRITICAL requirement. You can write it by hand or have a reviewer (a person, or an agent session independent of the code author) write it. `/hullproof-prelaunch` does not write this report. You fill in the template from its results table, and the two together satisfy G-2. The Pro edition has an audit skill that can also write the report, and it is optional. |
| G-3, G-4, G-5 | No BLOCKER is open. Every BLOCKER is PASS or NOT APPLICABLE. Every CRITICAL is settled, or accepted in writing where the standard allows it. |
| G-6 | Outside the free scope. |
| G-7 | Secret, static and dependency scans ran on this commit. `/hullproof-prelaunch` runs gitleaks with the kit configuration. You run Semgrep with the kit rules and OSV Scanner in your own terminal and attach the output files. |
| G-8 | A rollback path for this release is known. |

A verdict of READY (FREE SCOPE) says nothing about HIGH, MEDIUM or LOW requirements or findings. The label states that, because those requirements are outside the free scope and are not evaluated.

## What READY needs from you

A coding agent that reads your repository cannot reach READY (FREE SCOPE) alone. Most BLOCKER and CRITICAL requirements are settled by evidence that lives outside the code: an export from a provider dashboard, a test against a running or staging copy of the product, or the output of a build or scan. Expect to supply that evidence yourself, dated and recent, for most of the requirements before the first READY. The templates `PROVIDER-EXPORTS.md` and `STAGING-TEST-WINDOW.md` show how to record it. Until then those items stay NOT ASSESSED and the verdict stays NOT READY.

## Install

Requirements:

1. Claude Code. Use a current release. The skill and the agent attach the hook through their own settings, and an older release may not load them. If you see `HOOK: INACTIVE` after you accept the trust prompt, update Claude Code first.
2. Node, to run the hook. The hook and its self test were run on Node 22. Use a current long term support release.
3. Git. The audit reads your history with read only git commands.
4. Python 3, for the helper scripts in `tools/hullproof/helpers/`. They use the standard library only. They were run on Python 3.14, and any current Python 3 should work.
5. Optional scanners that the checklist uses when they are present: gitleaks, semgrep and osv-scanner. Without them the related items stay NOT ASSESSED and the report says so.
6. macOS or Linux. The commands below use `cp -R` and `shasum`. On Windows, use WSL, or Git Bash with `sha256sum -c` in place of `shasum -a 256 -c`.

Steps:

1. Get the kit. Clone this repository, or unzip `hullproof-free-0.3.0.zip` in an empty folder, not inside your project. The zip holds one folder, `hullproof-free-0.3.0/`. If you were given a `.sha256` file or a SHA256SUMS file with the download, check the zip first, in the folder that holds it: `shasum -a 256 -c hullproof-free-0.3.0.zip.sha256`. A SHA256SUMS file lists every release zip, so with only this zip in the folder use `shasum -a 256 -c --ignore-missing SHA256SUMS`.
2. From the root of your project, copy the kit in. This command is for a project that has no Hullproof files yet. If you installed Hullproof before, follow Update below instead. Every kit file lives under a `hullproof` name. The `-n` flag skips a file that already exists, so nothing of yours is overwritten.

   ```bash
   cp -Rn path/to/hullproof-free-0.3.0/kit/. .
   ```

   Then copy the license files in. This step is required, because the license texts must travel with the files you copied:

   ```bash
   mkdir -p docs/hullproof/licence
   cp path/to/hullproof-free-0.3.0/{LICENSE,LICENSE-DOCS.md,LICENSE-DOCS-CC-BY-SA-4.0.txt,LICENSING.md,NOTICE.md} docs/hullproof/licence/
   ```

3. Add this line to your project's root `CLAUDE.md`. Create the file if you do not have one.

   ```
   @docs/hullproof/HULLPROOF.md
   ```

4. Start Claude Code and run `/memory` to confirm Hullproof is loaded.
5. Accept Claude Code's workspace trust prompt for the project. The hook runs only after you accept it. Without it the auditor is not limited, so see the safety model below.
6. Run through `docs/hullproof/LITE-CHECKLIST.md`. It holds the checks a solo builder can run alone in a few minutes, each linked to its full requirement.
7. Run `/hullproof-prelaunch`. It asks for the stage, the markets you serve and what it may run, then writes `docs/security/reports/PRE-LAUNCH-RESULTS-<date>.md`. Keep that folder out of any public repository, because the report lists exploitable failures.
8. Fill in `docs/hullproof/templates/AUDIT-REPORT.md` from the results table. Without that report gate condition G-2 is not met and the verdict stays NOT READY.

To run Hullproof in another AI tool, see Works with your AI tool above and `editors/README.md` (after the copy in step 2 it sits in your project root). Leave `editors/` and `prompts/` where they land, because the kit manifest lists them.

## Update

Use this to move to a newer release of the free edition. Do not use `cp -Rn` for it, because `-n` keeps every file that already exists and your old files would win silently.

1. Unzip the new release in an empty folder, outside your project. The zip holds one folder, `hullproof-free-0.3.0/` for this release.
2. From the root of your project, save a copy of the current Hullproof files, outside the project:

   ```bash
   mkdir -p ../hullproof-old/skills ../hullproof-old/agents ../hullproof-old/hooks ../hullproof-old/rules
   cp -R docs/hullproof tools/hullproof ../hullproof-old/
   cp -R .claude/skills/hullproof-* ../hullproof-old/skills/
   cp -R .claude/agents/hullproof-* ../hullproof-old/agents/
   cp -R .claude/hooks/hullproof-* ../hullproof-old/hooks/
   cp -R .claude/rules/hullproof ../hullproof-old/rules/
   ```

3. Copy the new files over them. These are the only paths this command touches. Any local edit to a file in them is replaced, so merge your edits from the saved copy afterwards.

   ```bash
   KIT=path/to/hullproof-free-0.3.0/kit
   mkdir -p docs tools .claude/skills .claude/agents .claude/hooks .claude/rules
   cp -R "$KIT/docs/hullproof" docs/
   cp -R "$KIT/tools/hullproof" tools/
   cp -R "$KIT"/.claude/skills/hullproof-* .claude/skills/
   cp -R "$KIT"/.claude/agents/hullproof-* .claude/agents/
   cp -R "$KIT"/.claude/hooks/hullproof-* .claude/hooks/
   cp -R "$KIT/.claude/rules/hullproof" .claude/rules/
   cp -R "$KIT/editors" "$KIT/prompts" .
   ```

4. Check the result with `shasum -a 256 -c docs/hullproof/.kit-manifest`. Every line must say OK. Files that a newer release no longer ships are not deleted. They stay in your folders and are not in the manifest. Then copy the license files again as in Install step 2. Nothing else is touched.

## What to keep

When you copy kit files into your own repository, keep `LICENSE`, `LICENSE-DOCS.md`, `LICENSE-DOCS-CC-BY-SA-4.0.txt`, `LICENSING.md` and `NOTICE.md` in it. They sit outside `kit/`, so the install command does not copy them. Install step 2 puts them in `docs/hullproof/licence/`. CC BY-SA 4.0 applies to the documentation you copy and adapt, and Apache-2.0 applies to the code. [LICENSING.md](LICENSING.md) says which license covers which path.

## How to read the results

Each checklist item gets one result.

| Result | Meaning | What you do |
|--------|---------|-------------|
| PASS | The Verify steps were run on this commit and the evidence is attached. PASS (static) means it was proven by reading the code. | Keep the evidence. |
| FAIL | The requirement is not met. | Fix it. Findings are labelled VERIFIED (proven) or SUSPECTED (pattern seen, not proven). |
| NOT APPLICABLE | The system type does not exist in your project, with the reason and evidence recorded. | Check that the reason is true. |
| NOT ASSESSED | The agent could not settle the item. It always names a route. | Do the owner action in the next table. |

| Route for NOT ASSESSED | Owner action |
|------------------------|--------------|
| NEEDS DASHBOARD | Open the provider dashboard and record the setting with a screenshot or export. |
| NEEDS BUILD | Run a production build or CI job and attach the output. |
| NEEDS DYNAMIC TEST | Test the running app or a staging copy and record the request and response. |
| ASK OWNER | Answer the question the code and dashboards cannot answer. |
| ATTESTATION | Get a dated written statement from the owner or the provider. |
| UNKNOWN | Choose one of the routes above before sign off. |

How the results become a verdict:

1. NOT READY: any BLOCKER or CRITICAL item is FAIL or NOT ASSESSED, or another gate condition is not met. An unsettled BLOCKER or CRITICAL counts as open. BLOCKER findings cannot be waived.
2. READY WITH ACCEPTED RISK (FREE SCOPE): every failed CRITICAL item outside the protected classes has a written acceptance that names an owner, a compensating control and an expiry date, and all other conditions are met.
3. READY (FREE SCOPE): all gate conditions of the free scope are met and no BLOCKER or CRITICAL item is open. It says nothing about HIGH, MEDIUM or LOW findings.

A static run, which only reads code and configuration, cannot end READY while any BLOCKER needs a dashboard, a build or a running system. Expect the first run on a real project to end NOT READY. That is the checklist working.

## Safety model

The auditor agent reads your repository. The skill writes one results file. Neither changes your code, your data or your infrastructure unless you ask.

What the hook does. The hook checks every shell command the agent tries to run. It allows a short list of read only commands (git history commands, `ls`, `wc`, `grep`, `find` without `-exec` or `-delete`, `sed -n`, `awk` without `system()` or redirection, `jq`, redacted `gitleaks`, and read only `curl` for the auditor). It blocks command chaining, redirection, command substitution, interpreters, package installs and anything else off the list. If the hook cannot read its input or fails, it blocks the command. It is attached to the skill and to the agent, and the skill's `allowed-tools` line pre approves only the exact forms it lists, so other allowed forms may ask you for permission.

What the hook does not do. It limits writes made through the shell and the path of each Write call the skill makes. The skill's `allowed-tools` line pre approves Write only for Markdown files in `docs/security/reports/`, and the hook refuses a write to the hook, the agent, the skill, the standards, the settings or source files. It scans the text for secret shaped values and does not judge the rest of it, so an instruction planted in your code could still make the skill write misleading text into a report. The agent has no Write tool.

Before its first real command the auditor runs a probe that a working hook blocks. It prints `HOOK: ACTIVE` or `HOOK: INACTIVE` as the first line of its output, and makes no shell call after `INACTIVE`. Treat `HOOK: INACTIVE` as a stop. The auditor then checks the kit files against the manifest in `docs/hullproof/.kit-manifest` and prints `KIT: verified`, `KIT: MISMATCH` or `KIT: NOT VERIFIED`. The manifest detects accidental or hostile edits to the kit. It cannot protect against someone who edits both a file and its manifest line.

## Limits

1. The hook is the only enforced control. The rules written in the agent and skill files are instructions that a model can ignore. The hook controls which commands run, blocks reads of secret file names and limits the path of the skill's Write call, but it does not control the rest of what the agent reads or what a report says, so review each report before you share it and run the agents only on repositories you trust.
2. READY (FREE SCOPE) covers the BLOCKER and CRITICAL requirements at the declared stage and nothing else. It is evidence that a defined set of checks was done on one commit. It is not a certification and not proof that a product is secure.
3. Static analysis and scans cannot settle items that live in a provider dashboard, a build or a running system, and scans find only what their rules know. Those items stay NOT ASSESSED until the owner supplies evidence.
4. The requirements were validated on products built on the default stack: Next.js, TypeScript, Supabase and Vercel. Other stacks have not been validated.
5. Vendor behaviour changes between releases, so check the current vendor documents against the date each citation shows.

## How the standard is organized

Every requirement has an ID in the format `SEC-[DOMAIN]-[NUMBER]` and the same fields: requirement, rationale, severity, applicable systems, implementation guidance, verification method, automation potential, references, and exceptions.

| Document | Purpose |
|----------|---------|
| [conventions/requirement-ids.md](conventions/requirement-ids.md) | ID format and domain codes |
| [conventions/requirement-template.md](conventions/requirement-template.md) | The structure every requirement follows |
| [conventions/severity.md](conventions/severity.md) | BLOCKER, CRITICAL, HIGH, MEDIUM, LOW |
| [conventions/sources.md](conventions/sources.md) | How every claim is traced to a source |

## Support

Ask questions and report problems with the kit as GitHub issues on this repository, https://github.com/jt247/hullproof-free/issues. Issues are public, so do not paste secrets or private project details.

## Reporting a vulnerability in Hullproof

If you find a way around the hook, a gap in a requirement, or a flaw in the agent instructions, see [SECURITY.md](SECURITY.md) for how to report it. Do not use a public issue for that.

## Licensing, notices and security

Code is licensed under Apache License 2.0 ([LICENSE](LICENSE)). Documentation is licensed under CC BY-SA 4.0 ([LICENSE-DOCS.md](LICENSE-DOCS.md)). [LICENSING.md](LICENSING.md) says which license covers which path.

[NOTICE.md](NOTICE.md) credits the sources whose licenses ask for attribution, and states that Hullproof is not affiliated with or endorsed by the organisations it cites. [SECURITY.md](SECURITY.md) explains how to report a vulnerability in Hullproof, by email, or through GitHub private vulnerability reporting where the repository offers it. Hullproof and the READY labels describe the result of a defined set of checks on one commit. They are not a certification, and the names of other organisations and products belong to their owners.
