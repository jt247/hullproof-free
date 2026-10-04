# Secrets Management

| Field | Value |
|-------|-------|
| Domain codes | SEC-SECRETS |
| Topics covered | Secrets |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers API keys, database keys, signing secrets and service tokens used by the product and its pipeline: where they live, who can read them, how they leak, and how they are rotated. User passwords and session tokens are in AUTH.md, encryption key material in DATA-PROTECTION.md, CI deploy tokens and cloud identities in DEPENDENCIES.md and INFRASTRUCTURE-SECURITY.md, secrets in model prompts in AI-SECURITY.md, and secret exposure to AI coding agents in AGENTIC-DEV-SECURITY.md. Breach notification after a leak is in INCIDENT-RESPONSE.md.

> Research based engineering guidance, not legal advice. Requirements that name a market (NG, EU, ZA, KE, GH) apply only to products serving that market.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 4 of the 20 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-SECRETS-001](#sec-secrets-001-no-secret-in-client-bundles-or-public-environment-variables) | No secret in client bundles or public environment variables | BLOCKER | LAUNCH | Web, Mobile, SaaS, AI features |
| [SEC-SECRETS-003](#sec-secrets-003-keys-that-bypass-access-control-stay-in-trusted-server-code) | Keys that bypass access control stay in trusted server code | BLOCKER | LAUNCH | Database (Supabase), Backend, Serverless, Web, Mobile |
| [SEC-SECRETS-004](#sec-secrets-004-no-valid-secret-in-the-repository-or-its-history) | No valid secret in the repository or its history | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Mobile |
| [SEC-SECRETS-010](#sec-secrets-010-leaked-secrets-are-revoked-and-rotated-first) | Leaked secrets are revoked and rotated first | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Cloud, Mobile |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Secret storage (platform environment variables, secret managers) | DEPENDENCIES.md, INFRASTRUCTURE-SECURITY.md, DATABASE-SECURITY.md | None | SEC-SECRETS-007 |
| Secrets never in client code, bundles or public environment prefixes | MOBILE-SECURITY.md, AI-SECURITY.md | None | SEC-SECRETS-002, SEC-SECRETS-003 |
| Secret scanning in CI and push protection | None | None | SEC-SECRETS-005, SEC-SECRETS-006 |
| Secrets in git history | DEPENDENCIES.md | None | SEC-SECRETS-004 |
| Secrets in logs and error trackers | OBSERVABILITY.md, MOBILE-SECURITY.md, AI-SECURITY.md | None | SEC-SECRETS-015 |
| Secrets inventory and ownership | DATA-PROTECTION.md | None | SEC-SECRETS-012 |
| Rotation on exposure with a deadline | AGENTIC-DEV-SECURITY.md, INCIDENT-RESPONSE.md | None | SEC-SECRETS-010, SEC-SECRETS-016 |
| Separation per environment | INFRASTRUCTURE-SECURITY.md, AI-SECURITY.md | Environment credential separation | SEC-SECRETS-009 |
| Least privilege and scoped keys | API-SECURITY.md, AI-SECURITY.md, DATABASE-SECURITY.md, DATA-PROTECTION.md | None | SEC-SECRETS-008 |
| Short lived and dynamic credentials | INFRASTRUCTURE-SECURITY.md | None | SEC-SECRETS-013 |
| CI and deploy secrets | DEPENDENCIES.md, INFRASTRUCTURE-SECURITY.md, MOBILE-SECURITY.md | None | None in this document |
| Secrets exposed to AI coding agents | AGENTIC-DEV-SECURITY.md | None | None in this document |
| Local developer secrets and `.env` handling | AGENTIC-DEV-SECURITY.md | None | SEC-SECRETS-017 |
| Secrets in mobile apps | MOBILE-SECURITY.md | None | SEC-SECRETS-001 |
| Encryption key material and key management | DATA-PROTECTION.md, DATABASE-SECURITY.md | None | None in this document |
| Secret restoration after rollback | INFRASTRUCTURE-SECURITY.md | None | SEC-SECRETS-011 |
| Default credentials for service authentication (ASVS V13) | INFRASTRUCTURE-SECURITY.md | None | SEC-SECRETS-018 |
| Audit of who read or changed a secret | OBSERVABILITY.md, INFRASTRUCTURE-SECURITY.md, DEPENDENCIES.md | None | SEC-SECRETS-019, SEC-SECRETS-020 |
| CLI link files and project binding metadata | None | None | SEC-SECRETS-021 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-PAYMENTS | Does the product take payments or grant paid entitlements through a payment provider or an app store? | Search package.json and the source for paystack, paddle, stripe, flutterwave, revenuecat, apple or google billing, and for a checkout or entitlement route. Any handler that changes a plan, credit, role or entitlement is a payment path, whatever the payment provider is called. Record the commands, the number of files searched and that nothing was found, or record the owner's written answer that no money is taken through the product. | SEC-SECRETS-016 |
<!-- hullproof:gates:end -->

---

## Client exposure

### SEC-SECRETS-001: No secret in client bundles or public environment variables

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Web, Mobile, SaaS, AI features |
| Automation | FULL |
| Verification method | SECRET SCAN, STATIC ANALYSIS |

**Requirement.** A secret value MUST NOT reach a client by any channel (browser bundle, source map, mobile app package, rendered HTML, server component payload, API response, error body or redirect), and variables with a public prefix (`NEXT_PUBLIC_`, `EXPO_PUBLIC_`, or the framework's equivalent) MUST hold only values that are safe to publish. Compliance MUST be verified by scanning the built output, not only the source. A scan counts as evidence only after it has found a planted synthetic value of each secret format the project holds (Verify 1).

**Why.** Public prefixed variables are inlined into the JavaScript sent to every visitor and into the compiled mobile app in plain text. Escape found over 400 leaked secrets in AI built apps, including OpenAI keys, GitHub tokens and payment admin keys, and flagged Supabase service role keys in the browser as critical.

**Implementation.**
- Treat every value in the client bundle, `app.json` or `app.config.js` `extra`, and the mobile JS bundle as public. Obfuscation and Hermes bytecode do not change that.
- Only publishable identifiers may use a public prefix: for example the Supabase project URL and publishable or anon key, or a payment provider's publishable key.
- Calls that need a paid or privileged key (AI providers, email, payment secret keys) go through a server route or Edge Function.
- Disable or protect production source maps if they would reveal server code paths.

**Verify.**
1. Build the list of secret formats the project holds from the platform variable list and the secrets inventory (SEC-SECRETS-012). For each format, plant one synthetic value in a scratch file in the folder to be scanned and confirm the scan reports it; a scan that cannot find a planted value is not evidence, and a custom rule is added for every format the planted value test misses. Then, after `next build`, scan `.next/static` (and for Expo, the exported JS bundle from `npx expo export`) with Gitleaks or TruffleHog plus those custom patterns, including `sb_secret_`, JWTs whose payload has `"role":"service_role"`, `sk_live_`, `sk_test_`, AI provider key formats, and `scheme://user:password@host` connection strings. The evidence scan runs with the scanner's default rules plus the custom patterns, with no path or line allowlist, and the evidence states the configuration file used. A noise triage configuration is never evidence.
2. Flag every `NEXT_PUBLIC_` or `EXPO_PUBLIC_` variable whose name contains SECRET, PRIVATE, SERVICE, TOKEN or KEY (other than a known publishable key) and confirm its value is public by design.
3. On the deployed site, review every served JavaScript file and any exposed source map for keys, and test whether each key found is restricted. Fetch the rendered HTML, the server component payload and the JSON of every route in a full staging user journey, scan the captured responses with the evidence scan, and check that no build configuration `env` entry takes its value from a non public variable.

**Evidence.** Build output scan report with zero secret findings, the public variable review, and the deployed site review, each dated for the release.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-13.3.1 (L2, Promoted) [SRC-010]; OWASP MASVS 2.1.0 MASVS-STORAGE-1 [SRC-011]; OWASP MASWE 1.0.0 MASWE-0004 [SRC-014]; OWASP WSTG 4.2 WSTG-v42-INFO-05 [SRC-186]; NIST SP 800-53 Rev. 5 IA-5(7) (ADVISORY) [SRC-062]; Next.js Environment Variables [SRC-079]; Expo environment variables [SRC-084]; Supabase API keys [SRC-071]; Escape State of Vibe Coded Apps [SRC-007] (evidence).

**AI Agent Instruction.** Never put a secret in a variable with a public prefix, in client components, in mobile app config, or in any file the client bundle imports. When a feature needs a secret key, create a server route or Edge Function and call it from the client. If you find a secret in client code or public variables, stop, report it as BLOCKER, and do not deploy.

---

### SEC-SECRETS-003: Keys that bypass access control stay in trusted server code

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Database (Supabase), Backend, Serverless, Web, Mobile |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, SECRET SCAN, DYNAMIC TEST |

**Requirement.** Database keys and credentials that bypass row level security (the Supabase secret key or legacy `service_role` key, the `postgres` password, and any role with `BYPASSRLS`) MUST be used only in trusted server code, and MUST NOT be sent to a client by any channel, accepted from a client in a request, or returned in any API response, rendered page or error body.

**Why.** These keys skip every RLS policy. Whoever holds one can read and change every table, so one leak undoes all database access control.

**Implementation.**
- Create the privileged client only in server modules covered by SEC-SECRETS-002.
- Never pass a key to the client through props, API responses, error messages or config endpoints, and never read a key from a request header or body.
- Default stack: move from legacy `anon` and `service_role` keys to publishable (`sb_publishable_`) and secret (`sb_secret_`) keys, which Supabase states it is deprecating by the end of 2026, and use one secret key per backend component.
- Supabase rejects secret keys sent from a browser user agent with HTTP 401. Treat that as defense in depth only.

**Verify.**
1. Grep the codebase for every place the secret or service role key is read and confirm each is server only.
2. Scan API responses, rendered HTML, server component payloads and error bodies in staging (for example with a proxy capture of a full user journey) with the evidence scan of SEC-SECRETS-001, which must first have found a planted value, for key patterns.
3. Confirm no route reads an API key or database credential from request headers or body.

**Evidence.** Code review notes listing each use, and the response scan result.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-13.3.1 (L2, Promoted) [SRC-010]; NIST SP 800-53 Rev. 5 AC-6 (ADVISORY) [SRC-062]; Supabase API keys [SRC-071]; Supabase Securing your data [SRC-073]; PostgreSQL 18 Row Security Policies, BYPASSRLS [SRC-077]; Escape State of Vibe Coded Apps [SRC-007] (evidence).

**AI Agent Instruction.** Use the Supabase secret or service role key only in server code, and only for jobs listed as needing it (see SEC-DB-012 in DATABASE-SECURITY.md). Never return it, log it, or accept it from a request. If a client feature fails under RLS, fix the policy; never hand the client a privileged key.

---

## Source control and scanning

### SEC-SECRETS-004: No valid secret in the repository or its history

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile |
| Automation | FULL |
| Verification method | SECRET SCAN |

**Requirement.** An unrevoked secret MUST NOT exist in any tracked file or in any commit reachable on any ref the host serves, including pull request and fork refs and commits that a force push or a deleted branch left reachable by hash. An inline scanner allow tag or an ignore file entry MUST carry a reason and an owner in the security decisions log. A secret found in history MUST be revoked and rotated; rewriting history alone does not meet this requirement.

**Why.** Repositories get cloned, forked, shared with tools and occasionally made public. A key committed once stays in history even after the file is fixed.

**Implementation.**
- Add `.env`, `.env*.local` and similar files to `.gitignore` and keep a `.env.example` with placeholders only.
- Load secrets from the platform secret store or a local untracked file, never from committed config.
- When a scan finds a secret, rotate it first (SEC-SECRETS-010), then decide whether to clean history.

**Verify.**
1. Run `gitleaks git` (or `trufflehog git`) over the full history of all branches, with the evidence configuration of SEC-SECRETS-001 and the pull request refs fetched into the clone, and confirm zero findings, or that every finding maps to a key recorded as revoked. Search the repository for the scanner's inline allow tag and for ignore files; each hit must have a decisions log entry with a reason and an owner.
2. Commit a fake key, remove it in the next commit and push the branch; confirm CI fails on the first commit. Confirm `.gitignore` covers environment files and that `git ls-files` lists no `.env` file other than `.env.example`.
3. List tracked files that carry CLI link metadata or project references written by the tools in use (for example the `.vercel` folder) and confirm they are ignored or hold only non secret identifiers. Report counts and line numbers, never printed lines.

**Evidence.** Full history scan report and the revocation record for any historical finding.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-13.3.1 (L2, Promoted) [SRC-010]; NIST SSDF 1.1 PS.1.1 [SRC-050]; NIST SP 800-53 Rev. 5 IA-5(7) (ADVISORY) [SRC-062]; OWASP Secrets Management Cheat Sheet, 8 Detection [SRC-043]; GitHub secret scanning [SRC-093]; Next.js Environment Variables [SRC-079].

**AI Agent Instruction.** Never write a real secret into any tracked file, commit message, test fixture or example. Use placeholders in `.env.example`. If you see a secret in the repository, stop, report it as BLOCKER, and say it must be rotated; do not just delete the line.

---

## Rotation and response

### SEC-SECRETS-010: Leaked secrets are revoked and rotated first

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Cloud, Mobile |
| Automation | MANUAL |
| Verification method | DOCUMENT REVIEW, MANUAL TEST |

**Requirement.** The team MUST keep a written procedure that, for every production secret, names how to revoke it, issue a replacement and redeploy, and requires checking provider and application logs for misuse after any suspected exposure. A secret MUST be revoked and replaced in every environment that used it within one working day of the earliest of a scanner or push protection alert, a provider notice, a report, or the first log line that shows use from an unknown source; a secret not yet confirmed as leaked is treated as exposed when any of these exists. The clock does not start when the team records its confirmation. A leaked key that can reach personal data MUST be handed to the breach process in INCIDENT-RESPONSE.md.

**Why.** A leaked payment or service role key keeps working until someone revokes it. Teams without a written path lose hours working out how to rotate under pressure.

**Implementation.**
- For each secret in the inventory (SEC-SECRETS-012), record the provider page or CLI command to revoke and reissue it and every place the new value must be set.
- Rotate first, then fix the root cause and clean history if needed.
- Default stack: Supabase lets you create a new secret key and delete the leaked one immediately.
- After rotation, confirm the old value fails against the provider.

**Verify.**
1. Read the procedure and confirm each production secret has a revoke, reissue and redeploy entry and a log check step.
2. Run one real rotation of the payment or service role key on staging copies, time it, confirm the old value is refused by the provider, and record the result.
3. For each past exposure in the incident log, take the earliest timestamp from the source system (alert created time, provider email header, scanner report time) and compare it with the revocation time on the provider's key page. Any gap over one working day is a finding.

**Evidence.** The dated procedure and the rotation drill record. Incident records showing confirmation and revocation times.

**Exceptions.** None at LAUNCH. Missing entries for low impact secrets may be accepted in writing with an owner, a compensating control and an expiry date.

**References.** OWASP Secrets Management Cheat Sheet, 9 Incident Response [SRC-043]; NIST SP 800-53 Rev. 5 IA-5 (ADVISORY) [SRC-062]; GitHub secret scanning, rotate first [SRC-093]; Supabase API keys, leaked key procedure [SRC-071]; law driven and Derived (EU GDPR Art 32(1) [SRC-103]; NG NDPA 2023 s39(1) [SRC-100]; ZA POPIA s19 [SRC-104]; KE DPA 2019 s41 [SRC-106]; GH Act 843 s28 [SRC-109]).

**AI Agent Instruction.** If you find or cause a secret exposure, stop work, report it with where it appeared, and point to the rotation procedure. Never decide on your own that a leak is harmless. Never rotate production keys yourself unless the human asks and you have the access. Treat a provider email saying it found or revoked one of the keys as an exposure, and handle provider reporting through SEC-LOG-066 in INCIDENT-RESPONSE.md.
