# Observability

| Field | Value |
|-------|-------|
| Domain codes | SEC-LOG |
| Topics covered | Logging, Monitoring, Alerting, Error Handling |
| Part of | Hullproof Security Standard, see STANDARD.md |

Security logging, monitoring, alerting, and error handling. Requirement IDs keep the SEC-LOG code. Incident response and breach notification are in INCIDENT-RESPONSE.md.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 3 of the 29 requirements in this domain: every BLOCKER and every CRITICAL requirement in it. Hullproof Pro holds the other 26. Pro covers what you log, who can read it, how long you keep it and which events wake someone up.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-LOG-001](#sec-log-001-no-credentials-or-payment-data-in-logs) | No credentials or payment data in logs | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Serverless, Mobile, AI features |
| [SEC-LOG-003](#sec-log-003-authentication-and-authorization-events-are-logged) | Authentication and authorization events are logged | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Serverless |
| [SEC-LOG-019](#sec-log-019-authentication-validation-and-signature-checks-fail-closed) | Authentication, validation and signature checks fail closed | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Serverless, AI features |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Authentication and authorization events logged | AUTH.md | Security event logging | SEC-LOG-003 |
| No secrets or payment data in logs | MOBILE-SECURITY.md, AI-SECURITY.md | None | SEC-LOG-001 |
| Encoding of logged data (log injection) | FRONTEND-SECURITY.md | None | None in this document |
| Error handling and fail closed behaviour | AUTH.md, AI-SECURITY.md | None | SEC-LOG-019 (more in Pro edition) |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
<!-- hullproof:gates:end -->

---

## Logging

### SEC-LOG-001: No credentials or payment data in logs

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless, Mobile, AI features |
| Automation | PARTIAL |
| Verification method | SECRET SCAN, STATIC ANALYSIS, CONFIG REVIEW |

**Requirement.** Application logs, build logs, error responses, error tracker events and breadcrumbs, and analytics payloads MUST NOT contain passwords, session tokens, refresh tokens, JWT access tokens, API keys, signing secrets, connection strings, password reset tokens, magic link tokens, invitation tokens, one time codes, OAuth authorization codes, signed or presigned storage URLs, full payment card or bank account numbers, or full webhook payloads. Payment and webhook code MAY log only event IDs, order references, status and amounts. Errors MUST be logged by a fixed allowlist of fields (name, message, status, code), never as the whole error object, because the error of a failed provider call carries the request headers or query parameters that were sent.

**Why.** Anyone with access to a log sink, a shared error tracker project or an analytics dashboard can lift a credential from a log line and use it, and vendor retention keeps the value long after the code is fixed. Tokens in request logs and error tracker breadcrumbs are a common leak in AI built apps. Stage note: v5.0.0-16.2.5 is one of the Level 2 items promoted to LAUNCH.

**Implementation.**
- Log through one shared logger that redacts keys such as `password`, `token`, `secret`, `authorization`, `cookie`, `apiKey` and `card` before output.
- Never log raw request bodies, full header sets, session objects or whole provider responses. Log the fields you need by name.
- Keep credentials out of URLs and query strings so access logs and proxies never capture them. Tokens that must travel in a link (reset, verification, magic link, invitation, OAuth code) are allowed in the URL only under the conditions in a Pro edition requirement (SECRETS.md), and the request path and query string of those routes are removed from every log, tracker event and breadcrumb.
- Set the log, CDN and error tracker settings to drop query strings by default, and log the route pattern instead of the full URL. A signed or presigned storage URL is a credential until it expires, so log the object key and not the URL.
- Keep the error tracker's server side scrubbing on and strip headers in the SDK hook that runs before an event is sent.
- On payment and webhook routes, log a fixed allowlist of fields per event and scrub request bodies in the error tracker.
- Never echo environment variables in build scripts, and never return a key or connection string in an error message.
- Default stack: in the Sentry SDK keep `sendDefaultPii` off, remove `Authorization` and `Cookie` in `beforeSend`, and strip the query string from the request URL and from navigation and fetch breadcrumbs in `beforeSend` and `beforeBreadcrumb`; in Next.js route handlers, Server Actions and Supabase Edge Functions never pass the request object to `console.log`.
- The MAY log only list for payment and webhook code is an allowlist: on those routes, any field outside the list is not logged.

**Verify.**
1. In staging, exercise sign in, password reset, magic link or email code sign in, invitation, OAuth sign in, signed file download, payment, webhook and API key flows. Capture the value of each token the flows produce (the reset token, the magic link token, the invitation token, the one time code, the OAuth `code`, a signed storage URL and a JWT access token) and then export the platform logs, CDN or proxy access logs and a sample of error tracker events and breadcrumbs. Search the export for each captured value and for the URL query string of each link, and any hit fails. For each outbound provider call, force a failure (a stubbed 500 and a timeout) with a test credential, export the resulting logs and error tracker events, and search the export for the test credential value the call carried.
2. Run Gitleaks or TruffleHog over the export. Expect zero findings. The scanner has no rule for a reset token or a one time code, so step 1 is the test for those and this step is an extra check.
3. Run Semgrep rules that flag logger or console calls receiving `req.body`, `req.headers`, `request`, a session object, an error identifier or an object that holds one, or identifiers named like token, secret, password or key. A single line search misses calls that span lines; search the source for every `catch` block and every logger call that receives an error.
4. Review the logger redaction list and the error tracker scrubbing settings.

**Evidence.** Secret scan report over exported logs with zero findings, Semgrep run output, logger configuration file, and an export or screenshot of the error tracker scrubbing settings.

**Exceptions.** Masked payment details (card brand and last four digits) are allowed and need no exception. Any other deviation is a CRITICAL exception: in writing, with a named owner, a compensating control and an expiry date.

**References.** OWASP ASVS 5.0.0 v5.0.0-16.2.5 [SRC-010]; OWASP ASVS 5.0.0 v5.0.0-14.2.1 [SRC-010]; OWASP MASWE 1.0.0 MASWE-0005 [SRC-014]; OWASP Logging Cheat Sheet (Data to exclude) [SRC-044]; OWASP Top 10:2025 A09:2025 [SRC-020]; Sentry Server-Side Data Scrubbing [SRC-165]; Vercel Sensitive environment variables, build log redaction [SRC-082].

**AI Agent Instruction.** When you add or change any logger, console, error tracker or analytics call, pass only named fields, never a request, header set, session, provider response or webhook payload object. Route output through the project logger. If you find a credential already being logged, stop, report it as a finding, and treat the credential as exposed under SECRETS.md. Never turn off scrubbing or redaction to debug.

---

### SEC-LOG-003: Authentication and authorization events are logged

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CONFIG REVIEW |

**Requirement.** The server MUST write a log record for every sign in success and failure, sign out, password or MFA change, account recovery request, and authorization denial, including denied attempts to read or change another user's or tenant's data. Every route and server action MUST be covered: the denial path of each calls the shared enforcement helper that logs, or the route is listed as public. This requirement is CRITICAL wherever the product holds personal data or has accounts.

**Why.** Credential stuffing, account takeover and object level authorization probing can only be detected or investigated if these events exist. The breach notification clocks in Nigeria, the EU and Kenya run from awareness, so missing records make the deadline unreachable. Stage note: promoted to LAUNCH, because data protection law in served markets requires security of processing that Hullproof reads as logging authentication and access events from the first real user.

**Implementation.**
- Hosted auth providers record some of these events. Confirm which ones in the provider's logs and add application records for the rest.
- Log authorization denials at the server side check that refuses the request, with actor ID, resource type, resource ID and reason.
- Log account recovery requests whether or not the account exists, without revealing the result to the caller.
- Use the record format in a Pro edition requirement once at GROWTH; at LAUNCH a timestamp, actor ID, event type and outcome are the minimum.
- Default stack: Supabase RLS filters rows silently, so authorization denials must be logged where server code checks ownership or tenancy and returns 403 or 404.

**Verify.**
1. Write an automated test against staging that performs a failed sign in, a successful sign in, a password reset request and a request for another user's object, then queries the log store.
2. Assert that one record exists per action with actor or anonymous marker, event type, outcome and time.
3. Review the auth provider's log settings to confirm which events it records and for how long.
4. Enumerate every route and server action from the framework route list. For each, confirm the denial path calls the shared enforcement helper that logs, or that the route is listed as public. Run a rule that flags route handlers returning 401, 403 or 404 without the helper.

**Evidence.** Passing test run with its test file, and the provider log configuration export.

**Exceptions.** Events fully recorded by the hosted auth provider need no duplicate application record if the provider keeps them for at least the minimum in a Pro edition requirement (30 days at LAUNCH, Hullproof policy). Record the provider and period. Any other gap needs a recorded owner and fix date.

**References.** OWASP ASVS 5.0.0 v5.0.0-16.3.1, v5.0.0-16.3.2 (L2, promoted to LAUNCH) [SRC-010]; GDPR Art 32(1)(b), (d), Art 33(1) [SRC-103]; Nigeria Data Protection Act 2023 s39(2)(c), s40(2) [SRC-100]; Kenya Data Protection Act 2019 s43(1) [SRC-106] (Derived); OWASP Logging Cheat Sheet (Which events to log) [SRC-044]; NIST SP 800-53 Rev. 5 AU-2 [SRC-062] (ADVISORY); OWASP Top 10:2025 A09:2025 [SRC-020].

**AI Agent Instruction.** When you write or change sign in, sign out, recovery, MFA or authorization code, add the matching log call in the same change and a test that asserts it. Never remove or silence an existing security event log (HULLPROOF.md hard rule 10). If the auth provider already records an event, say so in the change description instead of assuming.

---

## Error Handling

### SEC-LOG-019: Authentication, validation and signature checks fail closed

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless, AI features |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, STATIC ANALYSIS |

**Requirement.** Any error raised while performing an authentication, input validation or signature check MUST result in the request being denied. Errors in authorization checks are owned by SEC-AUTHZ-006 in AUTH.md.

**Why.** A check that throws and is caught by a broad handler can let the request continue, which grants access exactly when something unusual is happening. Stage note: promoted to LAUNCH, because the same checks guard webhook signatures and agent tool actions. Payment handlers have their own fail closed requirement in API-SECURITY.md.

**Implementation.**
- Structure checks as "allow only on explicit success"; the default path returns 401, 403 or 400.
- Never wrap an auth or signature check in a `try` block whose `catch` continues to the protected action.
- When the auth provider or key service is unreachable, deny and log the failure (a Pro edition requirement).

**Verify.**
1. Write automated tests that force the auth client, the input validator and the signature verifier to throw, then assert each protected route returns a denial and performs no write.
2. Run Semgrep rules for empty catch blocks and catch blocks that continue after auth, validation or verification calls.

**Evidence.** Passing test run with its test file, and Semgrep output.

**Exceptions.** CRITICAL exception only: in writing, with a named owner, a compensating control and an expiry date. A deliberate fail open on an optional hardening check whose outage removes no access control, such as the breached password lookup owned by a Pro edition requirement, is allowed when the choice is recorded in the security decisions log and every skipped check is logged (a Pro edition requirement). Authentication, signature and validation checks themselves never fail open.

**References.** OWASP ASVS 5.0.0 v5.0.0-16.5.3 (L2, promoted to LAUNCH) [SRC-010]; OWASP Top 10:2025 A10:2025 [SRC-020]. See also SEC-AUTHZ-006 for authorization errors.

**AI Agent Instruction.** Write every security check so failure, exceptions and unexpected values deny the request. Never catch and ignore an error from an authentication, validation or signature check to make code run; apply SEC-AUTHZ-006 to authorization checks. If a check keeps failing, stop and report it (AUTH.md hard rule 9).
