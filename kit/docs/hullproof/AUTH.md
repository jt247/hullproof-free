# Authentication and Authorization

| Field | Value |
|-------|-------|
| Domain codes | SEC-AUTH, SEC-AUTHZ |
| Topics covered | Authentication, session management, OAuth and OpenID Connect; authorization, per user data isolation, multi-tenancy, admin systems and support tools (appended below) |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers how users prove who they are (login, passwords, MFA, recovery, identity tokens), how sessions are created, stored, cached, timed out and ended, how the product uses OAuth and OpenID Connect as a client, the rules for a product that issues OAuth or OpenID Connect tokens itself, and how business customers sign in through enterprise single sign on. Authorization requirements (SEC-AUTHZ) follow the authentication requirements in this same file. General cookie rules, CSP and XSS live in FRONTEND-SECURITY.md; per source rate limits live in API-SECURITY.md; token storage on the device lives in MOBILE-SECURITY.md; password hashing parameters and random value generation live in DATA-PROTECTION.md; admin and staff MFA lives in the authorization part of this file.

NIST SP 800-63B-4 is the normative baseline for authentication. Where it is stricter than OWASP ASVS 5.0.0, Hullproof follows it and says so in the References field.

The requirements in this file paraphrase and cite OWASP ASVS, OWASP cheat sheets and OWASP Top 10 lists by identifier and link. They do not copy the text of those sources.

On the default stack the identity provider's endpoints (Supabase Auth) and the Data API are public and answer to the publishable key. A control that runs only in the product's own server code does not stop a caller who goes straight to those endpoints. Where a requirement below says it must hold at the provider boundary, its Verify steps send the attack straight to the provider endpoint or the Data API, without passing through the product's server code. Where the provider or plan cannot enforce the rule, the requirement says what to record.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 22 of the 88 requirements in this domain: every BLOCKER and every CRITICAL requirement in it. Hullproof Pro holds the other 66. Pro covers the parts around sign in that attackers go for next, including sessions, account recovery, OAuth settings, tenant switching and admin and support tools.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-AUTH-001](#sec-auth-001-no-custom-password-storage-or-token-generation) | No custom password storage or token generation | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Mobile |
| [SEC-AUTH-002](#sec-auth-002-server-verifies-identity-tokens-before-trusting-them) | Server verifies identity tokens before trusting them | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Serverless |
| [SEC-AUTH-008](#sec-auth-008-no-default-shared-or-seeded-accounts-in-production) | No default, shared or seeded accounts in production | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Database |
| [SEC-AUTH-010](#sec-auth-010-no-authentication-bypass-paths-in-production) | No authentication bypass paths in production | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Serverless, Mobile |
| [SEC-AUTH-017](#sec-auth-017-logout-ends-the-session-on-the-server) | Logout ends the session on the server | CRITICAL | LAUNCH | SaaS, Web, API, Mobile |
| [SEC-AUTH-030](#sec-auth-030-exact-redirect-url-allowlist-in-production) | Exact redirect URL allowlist in production | CRITICAL | LAUNCH | SaaS, Web, Mobile |
| [SEC-AUTH-034](#sec-auth-034-external-identities-map-to-accounts-by-issuer-and-subject) | External identities map to accounts by issuer and subject | CRITICAL | LAUNCH | SaaS, Web, API, Mobile |
| [SEC-AUTHZ-002](#sec-authz-002-server-side-permission-check-in-every-handler-deny-by-default) | Server side permission check in every handler, deny by default | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Serverless, Mobile |
| [SEC-AUTHZ-003](#sec-authz-003-object-level-check-for-every-record-identified-by-request-input) | Object level check for every record identified by request input | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Serverless, Mobile, Database |
| [SEC-AUTHZ-004](#sec-authz-004-writable-field-allowlist-no-privilege-fields-from-the-client) | Writable field allowlist, no privilege fields from the client | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Serverless, Mobile, Database |
| [SEC-AUTHZ-005](#sec-authz-005-authorization-attributes-come-only-from-server-controlled-data) | Authorization attributes come only from server controlled data | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Database, Mobile |
| [SEC-AUTHZ-006](#sec-authz-006-authorization-errors-result-in-denial) | Authorization errors result in denial | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Serverless |
| [SEC-AUTHZ-007](#sec-authz-007-privileged-clients-never-act-for-a-user-without-that-users-permissions) | Privileged clients never act for a user without that user's permissions | CRITICAL | LAUNCH | SaaS, API, Backend, Serverless, Database |
| [SEC-AUTHZ-010](#sec-authz-010-ownership-policies-on-user-owned-tables) | Ownership policies on user owned tables | BLOCKER | LAUNCH | Database (Supabase) |
| [SEC-AUTHZ-012](#sec-authz-012-server-side-caches-keyed-by-user-and-tenant) | Server side caches keyed by user and tenant | CRITICAL | LAUNCH | SaaS, Web, Backend, Serverless |
| [SEC-AUTHZ-013](#sec-authz-013-no-operation-crosses-a-tenant-boundary) | No operation crosses a tenant boundary | BLOCKER | LAUNCH | SaaS, API, Backend, Database, AI features |
| [SEC-AUTHZ-014](#sec-authz-014-tenant-column-and-membership-based-rls-on-tenant-tables) | Tenant column and membership based RLS on tenant tables | BLOCKER | LAUNCH | Database (Supabase) |
| [SEC-AUTHZ-015](#sec-authz-015-active-tenant-resolved-on-the-server-from-verified-membership) | Active tenant resolved on the server from verified membership | CRITICAL | LAUNCH | SaaS, API, Backend, Serverless |
| [SEC-AUTHZ-020](#sec-authz-020-admin-functions-guarded-by-a-server-side-admin-role-check) | Admin functions guarded by a server side admin role check | BLOCKER | LAUNCH | SaaS, Web, API, Backend, Serverless |
| [SEC-AUTHZ-021](#sec-authz-021-mfa-required-for-in-product-admin-accounts) | MFA required for in product admin accounts | CRITICAL | LAUNCH | SaaS, Web, API |
| [SEC-AUTHZ-031](#sec-authz-031-support-tools-never-hold-an-all-tenant-rls-bypass-key) | Support tools never hold an all tenant RLS bypass key | CRITICAL | LAUNCH | SaaS, Backend, Database (Supabase) |
| [SEC-AUTHZ-036](#sec-authz-036-realtime-channels-authorize-every-join-broadcast-and-presence-update-per-user-and-tenant) | Realtime channels authorize every join, broadcast and presence update per user and tenant | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Mobile, Database (Supabase) |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Password authentication | FRONTEND-SECURITY.md | None | SEC-AUTH-008 (more in Pro edition) |
| Password storage | DATA-PROTECTION.md | None | SEC-AUTH-001 |
| MFA | INFRASTRUCTURE-SECURITY.md, MOBILE-SECURITY.md | None | SEC-AUTHZ-021 (more in Pro edition) |
| OAuth | PRIVACY.md | Redirect sinks | SEC-AUTH-030 (more in Pro edition) |
| OIDC | None | None | SEC-AUTH-034 |
| Session creation | DATA-PROTECTION.md, FRONTEND-SECURITY.md | None | SEC-AUTH-010 (more in Pro edition) |
| JWT validation | None | None | SEC-AUTH-002 (more in Pro edition) |
| Refresh tokens | MOBILE-SECURITY.md | Account suspension | SEC-AUTH-017 (more in Pro edition) |
| Privileged actions | OBSERVABILITY.md | None | SEC-AUTHZ-007, SEC-AUTHZ-020 (more in Pro edition) |
| Role and permission model | None | None | SEC-AUTHZ-002, SEC-AUTHZ-005, SEC-AUTHZ-006 (more in Pro edition) |
| Object and field level authorization | None | Object lookup before model call | SEC-AUTHZ-003, SEC-AUTHZ-004, SEC-AUTHZ-010 (more in Pro edition) |
| Tenancy and tenant isolation | None | Tenant membership insert | SEC-AUTHZ-012, SEC-AUTHZ-013, SEC-AUTHZ-014, SEC-AUTHZ-015 (more in Pro edition) |
| Support access and impersonation | None | None | SEC-AUTHZ-031 (more in Pro edition) |
| Realtime channel authorization | None | Realtime channel authorization | SEC-AUTHZ-036 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-TENANTS | Can one deployment hold data for more than one tenant, organisation, workspace, team or other group of customers? | Answer from the data model, not from a word list. A sharing boundary is a table that groups users or customers (an organisation, team, workspace or account) and that other tables reference to decide who may see their rows. Look for such a table in the schema. A foreign key from one ordinary table to another (orders to products, comments to posts) is not a sharing boundary on its own. A table with a membership style name (memberships, members, team_members, org_users or similar) points to one. A query that lists foreign keys to tables other than the users table is a helper for finding candidates, not the test. Then search the schema, migrations and source for tenant_id, org_id, organization_id, workspace_id, team_id and the product's own name for the unit that groups customers; these terms are hints. Record the commands, the number of files searched and that nothing was found, or record the owner's written answer that every customer has a separate deployment, cross checked against the schema. | SEC-AUTHZ-013, SEC-AUTHZ-014, SEC-AUTHZ-015 (more in Pro edition) |
| GATE-STAFF | Does anyone besides the owner hold an admin, staff or support role, or can staff act inside customer accounts? | Check the role column, role table or admin list and confirm only the owner's account holds a role above user, and that no support or impersonation feature exists. Record the query or search, or record the owner's written answer. This gate does not cover the admin route guard or admin MFA, which apply whenever an admin surface exists. | SEC-AUTHZ-031 (more in Pro edition) |
<!-- hullproof:gates:end -->

---

## Authentication

### SEC-AUTH-001: No custom password storage or token generation

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW |

**Requirement.** User authentication MUST be provided by a managed identity provider or an established, maintained authentication library, and application code MUST NOT contain its own password hashing, password comparison, or session or reset token generation logic.

**Why.** Hand written auth code is where weak hashing, timing leaks and predictable tokens (for example `Math.random`) appear. A managed provider removes that whole class of defects from the codebase.

**Implementation.**
- Use the provider's sign up, sign in, reset and session APIs. Do not reimplement any of them in application code.
- If the product must store passwords itself, record the reason in the security decisions log and follow the password hashing requirement in DATA-PROTECTION.md.
- Any value that must be unguessable and is not issued by the provider follows the CSPRNG requirement in DATA-PROTECTION.md.
- Default stack: Supabase Auth owns password storage, sessions and reset tokens. Record that ownership in the security decisions log.

**Verify.**
1. Run Semgrep over the repository for `bcrypt`, `argon2`, `scrypt`, `pbkdf2`, `crypto.createHash`, `createHmac` and `Math.random` inside auth, session, reset and invite code paths.
2. Review each hit and confirm it is either absent from auth logic or covered by a recorded decision.
3. Confirm the security decisions log names the identity provider that owns password storage and session issuance.

**Evidence.** Semgrep report with no unexplained hits in auth paths, and the security decisions log entry naming the identity provider.

**Exceptions.** A product that must run its own authentication records the reason, the library used, and the password hashing parameters. The exception needs a named owner, a compensating control and an expiry date. Failure modes for custom tokens: algorithm confusion, no expiry, timing leaks in comparison and no audience. A custom signed token built on a maintained library that pins the algorithm, sets expiry and audience, and compares in constant time is a hygiene finding rated LOW. Custom token logic with any failure mode keeps the CRITICAL rating.

**References.** NIST SP 800-218 SSDF 1.1 PW.1.3 [SRC-050]; OWASP ASVS 5.0.0 v5.0.0-11.4.2 (L2, promoted to LAUNCH), v5.0.0-11.5.1 (L2, promoted to LAUNCH) [SRC-010]; NIST SP 800-63B-4 §3.1.1.2 (storage), §3.2.12 [SRC-060]; OWASP Password Storage Cheat Sheet [SRC-032]; Next.js Authentication guide [SRC-080]; OWASP Top 10:2025 A07:2025 [SRC-020].

**AI Agent Instruction.** Use the project's identity provider for every sign up, sign in, reset and session operation. Never write password hashing, password comparison, or token generation code. If a feature seems to need custom auth logic, stop and report the need instead of writing it.

---

### SEC-AUTH-002: Server verifies identity tokens before trusting them

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, STATIC ANALYSIS |

**Requirement.** Server code MUST verify an identity or access token's signature with an allowlisted algorithm, a key from a preconfigured trusted source for that issuer, its `exp` and `nbf` validity window, its issuer (`iss`), its audience (`aud`) for this service, and its token type before reading any claim from it, and MUST reject the request with 401 when any check fails. An ID token MUST NOT be accepted where an access token is expected. Where a decision uses a scope or authentication level claim (`scope`, `aal`, `acr`), the server MUST read the claim only after these checks and MUST enforce it.

**Why.** A token that is decoded but not verified lets anyone forge a user ID or role. Accepting `alg: none`, an attacker supplied key, or an expired token gives the same result. A token that is correctly signed but was issued for another application or another API of the same issuer passes a signature check alone, so the issuer, audience and type checks are part of verification.

**Implementation.**
- Verify tokens with the provider SDK or a maintained JWT library configured with a fixed algorithm list and a fixed key set or JWKS URL. Never trust `jku`, `x5u` or `jwk` headers.
- Treat a decode call without verification as a defect anywhere in server code.
- Set the expected issuer and audience in configuration. Read the library documentation to see which of `iss`, `aud` and token type it checks for you, and check the rest in code. Do not accept the project's publishable (anon) key token or a service role token as a signed in user's token.
- Default stack: in Next.js server code use Supabase `getClaims()` (verifies the signature) or `getUser()`. Never use `getSession()` in server code to decide who the caller is, because it reads the cookie without revalidating it.
- Proxy (formerly Middleware) checks are optimistic. The verified check must also happen in the Route Handler, Server Action or data access layer.

**Verify.**
1. Send seven bad tokens to three protected endpoints and expect 401 each time: none, a changed payload, `alg: none`, expired, another signer, wrong audience, wrong issuer.
2. Make it an automated test, with the endpoints chosen by the reviewer. Sign the wrong audience token (for example a token issued for another application) and the wrong issuer token with a test key that is trusted only in the test environment. Send each bad token in every channel the endpoint accepts (header, cookie and any other), and confirm a valid token in the same channel succeeds (positive control).
3. Run Semgrep for `jwt.decode(`, `jose.decodeJwt(`, and `supabase.auth.getSession(` in server files; each hit must be justified or removed.
4. Review the verification configuration for a fixed algorithm list and a fixed key source. In a scratch branch replace the verifier with a decode only call and confirm the test fails.

**Evidence.** Passing test file with the seven negative cases, and the Semgrep report.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-9.1.1, v5.0.0-9.1.2, v5.0.0-9.1.3, v5.0.0-9.2.1, v5.0.0-9.2.2, v5.0.0-9.2.3, v5.0.0-7.2.1 [SRC-010]; OWASP Top 10:2025 A07:2025 [SRC-020]; OWASP Cheat Sheet Series: JSON Web Token [SRC-030]; Supabase Auth session docs (`getClaims()` guidance) [SRC-121]; Next.js Authentication guide (optimistic versus secure checks) [SRC-080].

**AI Agent Instruction.** Before using any user ID, role or claim from a token in server code, call the provider's verifying function (`getClaims()` or `getUser()` on Supabase). Never use a decode only function or `getSession()` for an access decision. Verify issuer, audience and token type as well as the signature. Add the seven negative token tests when you add a protected endpoint.

---

### SEC-AUTH-008: No default, shared or seeded accounts in production

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Database |
| Automation | PARTIAL |
| Verification method | SECRET SCAN, CONFIG REVIEW |

**Requirement.** The production environment MUST NOT contain any account with a default, shared, documented, or seed file password, and seed scripts that create users MUST NOT run against production.

**Why.** Seeded `admin@example.com` style accounts with known passwords are an instant takeover, often with admin rights.

**Implementation.**
- Keep test users in seed files that only run against local and preview databases.
- Guard seed scripts so they refuse to run when the target is production.
- Create the first real admin through the normal sign up or invite flow, with MFA.
- Accounts created by AI agents or test tooling (QA, smoke test and end to end accounts) count as seeded accounts when they exist in production. Create them in staging or a preview database.

**Verify.**
1. Run Gitleaks over seed files, migrations and fixtures for fixed passwords.
2. List production users created by seed or migration scripts, and users whose email matches seed file emails; there must be none.
3. Confirm the seed script contains a production guard.
4. List production users whose email or creation source matches QA, test or agent tooling (for example addresses with `test`, `qa` or `example`, and users created from CI or agent sessions), and list non production accounts and credentials present in the production provider console; there must be none.

**Evidence.** Gitleaks report, the production user query result, and the seed script guard.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-6.3.2 [SRC-010]; CISA Secure by Design Pledge Goal 2 [SRC-064]; CISA Secure by Design principles [SRC-063].

**AI Agent Instruction.** Never write a migration or production script that inserts users with known passwords. Put test users only in seed files guarded against production. If you find a seeded account in production configuration, stop and report it as a BLOCKER.

---

### SEC-AUTH-010: No authentication bypass paths in production

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless, Mobile |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW, DYNAMIC TEST |

**Requirement.** A production build MUST NOT contain any route, flag, header, query parameter, or environment switch that creates a session or acts as a user without completing a documented authentication pathway. Every function that creates a session for, or acts as, a user other than through a sign in pathway MUST have an entry in the sign in pathway inventory (a Pro edition requirement in AUTH.md, or a list in the security decisions log) with its guard; a staff feature that signs in as a user is documented only when it has that entry.

**Why.** Dev login routes, test bypass flags and "act as user" headers left in production let anyone sign in as any user with no credentials.

**Implementation.**
- Keep development shortcuts out of production code paths entirely, not just behind an environment variable that could be set by mistake.
- Route all sign ins through the identity provider.
- Support impersonation, if it exists, follows the support tool rules in the authorization part of this file.
- Owned by SEC-DB-034 in DATABASE-SECURITY.md for this root cause (Credential tables writable through the Data API); report one finding.
- Layer: this requirement covers bypass paths in routes, flags and headers. Authorization attributes are covered by SEC-AUTHZ-005 and SEC-DB-006.

**Verify.**
1. Search for routes or handlers named like `dev-login`, `test-login`, `impersonate`, `bypass`, `as-user`, and for headers or query parameters that set a user ID.
2. List every environment variable read inside session creation and the authentication middleware, and explain each one; search for environment checks such as `NODE_ENV !== 'production'` around session creation. Search every function that creates or returns a session, whatever its name, and match each to the inventory.
3. Against the staging URL (never production), call any candidate route found; it must return 404 or 401.
4. A switch that is true only in production, such as a `NODE_ENV` branch, can differ between staging and production. Diff the environment variable names and the build flags of staging against production, and explain each difference, or run a production build in an isolated environment and repeat step 3 there.

**Evidence.** Search results and the dynamic test output.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-6.3.4, v5.0.0-6.1.3, v5.0.0-15.2.3 [SRC-010]; Escape, State of vibe coded apps (zero click account takeover cases, evidence only) [SRC-007]. Stage: BLOCKER controls apply from LAUNCH.

**AI Agent Instruction.** Never add a dev login, test bypass, or "sign in as" shortcut to application code, even temporarily. If a test needs an authenticated user, create a session through the provider in the test setup. If you find a bypass path, stop and report it as a BLOCKER.

---

## Session Management

### SEC-AUTH-017: Logout ends the session on the server

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Mobile |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, CODE REVIEW |

**Requirement.** After logout, the server MUST refuse the logged out session's refresh token at once, and MUST refuse its access token at once on sensitive actions (payments, account and credential changes, data export, and admin functions) and on every request after a recorded maximum access token lifetime of no more than 1 hour. A sensitive action that a client can reach by calling the Data API or another provider endpoint directly with its access token MUST be covered by the same check at that boundary, or be moved behind server code that makes the check.

**Why.** Logout that only clears the browser leaves a copied token working. Self contained JWTs keep verifying until they expire unless the server checks for revocation.

**Implementation.**
- Call the provider's sign out on the server side of logout, not just a client state reset.
- For sensitive actions (payments, account changes, data export, admin), check the token's session against the provider's session store.
- Keep access token lifetime at 1 hour or less.
- Record the list of sensitive actions the product has, by category (payments, account and credential changes, data export, admin), in the session policy (a Pro edition requirement).
- A check in the product's server code does not see a call that goes straight to the Data API. For sensitive tables, either route the access through server code that makes the check, or add a database policy that calls a function in a schema clients cannot reach, which confirms the session row for the token's `session_id` still exists. Follow the security definer rules of SEC-DB-008 in DATABASE-SECURITY.md for that function.
- Default stack: Supabase `signOut()` deletes the session row, but an issued access JWT still verifies until `exp`. On sensitive actions, check the JWT `session_id` against `auth.sessions` or call `getUser()`. Keep the JWT expiry at the 1 hour default or lower.
- Default stack: pass the sign out `scope` explicitly and record the choice in the session policy (a Pro edition requirement). The JavaScript client used by Next.js and Expo defaults to `global`, so a plain logout on a phone also ends the user's web sessions; the Dart and Kotlin clients default to `local`. Use `local` for an ordinary logout that should end only this device.
- Default stack (checked 2026-10-03): Supabase documents that `signOut()` removes the affected sessions and destroys their refresh tokens, that access tokens of revoked sessions stay valid until their `exp` claim, that the JavaScript client defaults to the `global` scope, and that checking the JWT `session_id` claim against `auth.sessions` shows whether the user signed out. Test the access token replay step with these facts in mind.
- A product with no server side logout at all is a finding under this requirement. A Pro edition requirement covers only whether an existing logout can be reached.

**Verify.**
1. Capture an access token and refresh token, log out, then replay both with curl directly against the API (WSTG-v42-SESS-06 method); the refresh must fail.
2. Replay the access token on one sensitive action for every category in the recorded list, not one chosen by the tester; each must fail.
3. Replay the access token on an ordinary endpoint after the recorded lifetime; it must fail.
4. Provider boundary: replay the captured access token straight against the Data API (a read and a write on a table that holds sensitive data) with the publishable key, without passing through the app server. Both must fail, or the table must be reachable only through server code.
5. A browser URL reload after logout is not valid evidence.

**Evidence.** curl transcripts of the replay for each category, the direct Data API transcript, and the configured JWT expiry.

**Exceptions.** Any waiver needs a named owner, an approver, a compensating control and an expiry date.

**References.** OWASP ASVS 5.0.0 v5.0.0-7.4.1 [SRC-010]; NIST SP 800-63B-4 §5.1 [SRC-060]; OWASP WSTG 4.2 WSTG-v42-SESS-06 [SRC-186]; OWASP Session Management Cheat Sheet [SRC-033]; Supabase Auth session docs [SRC-121]; Supabase Signing out (Sign out and scopes) [SRC-271].

**AI Agent Instruction.** When you implement logout, call the provider's server side sign out. On sensitive actions, add the session revocation check. Never treat clearing client state as logout, and never raise the access token lifetime above 1 hour.

---

## OAuth and OpenID Connect

### SEC-AUTH-030: Exact redirect URL allowlist in production

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, Mobile |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST |

**Requirement.** The production identity provider and every OAuth provider console MUST list redirect URLs as exact HTTPS values with no wildcard or glob characters and no `http` or localhost entries, and the production Site URL MUST be the production origin. An exact reverse domain custom scheme URL used for a mobile callback under a Pro edition requirement is also allowed.

**Why.** A wildcard or stray development URL lets an attacker receive authorization codes or tokens at a host they control and take over the account.

**Implementation.**
- Register each production callback as a full exact URL.
- This requirement covers the lists held in the provider consoles. A redirect in the product's own code that sends a user to an attacker chosen address is a finding under a Pro edition requirement, which owns that failure.
- A mobile app that uses a custom scheme under a Pro edition requirement registers the full exact callback (for example `com.example.app://auth/callback`), never a scheme or path pattern.
- Keep localhost, preview and Expo Go (`exp://`) redirect values in a separate non production project only (see SECRETS.md for environment separation).
- Default stack: Supabase Redirect URLs accept `*` and `**` globs, and the Site URL ships as `http://localhost:3000`. The production project must contain neither. Never add the suggested Vercel preview pattern (`https://*-<slug>.vercel.app/**`) to the production project.

**Verify.**
1. Export the production Supabase Auth URL configuration and each provider console's redirect list; confirm no `*`, no `**`, no `http://` and no localhost values, that every non HTTPS entry is an exact reverse domain custom scheme URL used under a Pro edition requirement, and that the Site URL equals the production origin.
2. Start a sign in and change `redirect_to` or `redirect_uri` to another host; the flow must fail.

**Evidence.** Configuration exports and the tamper test result.

**Exceptions.** Any waiver needs a named owner, an approver, a compensating control and an expiry date.

**References.** IETF RFC 9700 §2.1, §4.1.3, §2.6 [SRC-180]; OWASP ASVS 5.0.0 v5.0.0-10.4.1 [SRC-010]; OWASP Cheat Sheet Series: OAuth2 [SRC-030]; Supabase Auth redirect URLs [SRC-181]; Expo AuthSession (`makeRedirectUri`) [SRC-182].

**AI Agent Instruction.** Never add a wildcard, `http` or localhost redirect URL to production auth settings, and never pass a `redirectTo` built from user input. Add a custom scheme URL only as an exact value for a mobile callback under a Pro edition requirement. If a flow fails because a URL is missing from the allowlist, add the exact URL to the right environment or stop and report; do not widen the pattern.

---

### SEC-AUTH-034: External identities map to accounts by issuer and subject

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Mobile |
| Automation | PARTIAL |
| Verification method | MANUAL TEST, CODE REVIEW |

**Requirement.** Where the product offers sign in with an external identity provider or account linking, an external identity MUST be matched to an account only by its issuer plus subject (`iss` and `sub`). A new external identity MUST be linked to an existing account only when the user takes an explicit action while signed in to that account, or when both of these hold: the external provider asserts that the email address is verified, and the existing account's email address is confirmed (a Pro edition requirement). An email match against an address that is not verified at the provider, or not confirmed on the existing account, MUST NOT link identities or sign the user in.

**Why.** Linking on email lets an attacker who controls an email at one provider take over an account created elsewhere with the same address. The reverse also works: an attacker who registers a victim's address first, without confirming it, can wait for the victim to sign in with a social provider and share the account.

**Implementation.**
- Store provider identities keyed on issuer and subject.
- Offer "connect Google" or similar from account settings while signed in.
- Turn on email confirmation for every enabled provider (a Pro edition requirement), and enable only providers that return a verified email.
- Default stack (checked 2026-10-03): Supabase links a new OAuth identity to an existing user with the same email address automatically, and when it does it removes the other identities on that user that are not confirmed. The vendor guide describes this as the defence against pre account takeover and gives no setting that turns automatic linking off. Manual linking through `linkIdentity()` is a separate setting. So on Supabase the rule is met by these settings, all recorded in the security decisions log: email confirmation on, only providers that assert verified emails enabled, and the provider list reviewed whenever one is added.
- If the identity provider links on any email match, including an address the provider did not verify, this requirement is not met and cannot be accepted.

**Verify.**
1. Create an account with password on email X and confirm it. Sign in with a social provider whose account uses email X. Confirm the result is the owner of the account for email X, with the identity attached, and that no other person's session is created.
2. Review code that creates or links identities for email based matching, including any user lookup by email next to an OAuth callback.
3. Pre account takeover case: sign up with password on a victim's email X and do not confirm it. Then sign in with a social provider whose verified email is X. The password set at the first sign up must not work afterwards, and the first sign up must not hold a session on the merged account.
4. For each enabled provider, read its documentation or test whether it can return an email it has not verified. Disable any that can.

**Evidence.** Manual test record for steps 1 and 3, the provider list review, and code review notes.

**Exceptions.** Does not apply to a product with no external identity provider and no account linking. No acceptance is available for any other case: a finding here is in the authentication class under Protected classes in STANDARD.md. The fix is email confirmation on, a provider list limited to verified emails, and a link rule that meets the Requirement.

**References.** OWASP ASVS 5.0.0 v5.0.0-6.8.1, v5.0.0-10.3.3, v5.0.0-10.5.2 [SRC-010]; Supabase Auth identity linking guide [SRC-181]; OWASP Top 10:2025 A07:2025 [SRC-020].

**AI Agent Instruction.** Key external identities on issuer and subject. Never write code that links or signs in a user because an email matches unless the provider asserts it as verified and the existing account's email is confirmed.

---

## Access control model and enforcement

### SEC-AUTHZ-002: Server side permission check in every handler, deny by default

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless, Mobile |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, AUTOMATED TEST, DYNAMIC TEST, CODE REVIEW |

**Requirement.** Every server function that reads non public data or changes state, including every Server Action, Route Handler, API route and Edge Function, MUST check inside the handler that the caller's role permits that function, and MUST deny the request when the role is missing, unknown or not explicitly allowed. Client side checks, hidden UI elements and edge middleware MUST NOT be the only authorization check for any function. A handler that checks only that a session exists is not a role check: its function MUST be listed as any signed in user, with a reason, in the list of functions and the roles allowed to call each (the access matrix of a Pro edition requirement in AUTH.md, or an equivalent table in the repository). A handler missing from that list fails this requirement.

**Why.** Server Actions and Route Handlers are public endpoints that anyone can call directly. Broken function level authorization lets a normal or anonymous user run privileged operations. Middleware and UI checks are bypassed by calling the endpoint directly.

**Implementation.**
- Put the check in a shared server only helper (for example `requireRole(session, 'editor')`) called at the top of each handler, or in a Data Access Layer that every data call goes through.
- Write the check as an allowlist: grant only roles listed for that function; everything else returns 403.
- Default stack: Next.js Proxy (formerly Middleware) checks are optimistic only. Repeat the check inside each Server Action and Route Handler, and mark the helper module `server-only`.
- Default stack: in Expo apps, treat every call the app makes as public; the server or RLS policy is the control, never app code.
- Owned by SEC-AGENT-008 in AGENTIC-DEV-SECURITY.md for this root cause (MCP server authorization); report one finding.

**Verify.**
1. Run a Semgrep rule that flags exported Server Actions, Route Handlers and API routes with no call to the project's authorization helper. A call whose name merely contains auth or session is not a role check; read the helper. Search from the workspace root, not one folder, and count per exported method.
2. Generate the list of functions under test from the framework route table or file tree and from every exported Server Action, not from the access matrix. Diff it against the function list. For each function, call it with no session, with a session of a role marked deny, and with a valid allowed role; the first two MUST return 401 or 403 and change nothing, and the allowed role MUST succeed (positive control). Call every function with a valid session of the lowest role; every function that returns a 2xx response must be listed as any signed in user.
3. Replay captured requests for every state changing endpoint without a token and confirm denial (WSTG-v42-ATHZ-02 method).
4. For each function listed as any signed in user, read the reason and the function's purpose in the PRD or user stories. A function that changes other users' data, roles, plans or entitlements, or reads other people's data, and is listed as any signed in user, fails.

**Evidence.** Semgrep report with zero unguarded handlers, and a passing test run covering each function with denied and allowed roles.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1, v5.0.0-8.3.1 [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-02 [SRC-186]; OWASP API Security Top 10 2023 API5:2023 [SRC-021]; NIST SP 800-53 Rev 5 AC-3, AC-6(10) [SRC-062]; OWASP Authorization Cheat Sheet (Deny by Default, Validate the Permissions on Every Request) [SRC-034]; Next.js Data Security guide (Server Actions are public endpoints) [SRC-078]; Next.js Authentication guide (Optimistic versus secure checks) [SRC-080].

**AI Agent Instruction.** When you write or change any Server Action, Route Handler, API route or Edge Function, add the authorization helper call as the first statement after reading the session, and list the allowed roles explicitly. Never rely on middleware, a hidden button or a client check as the access control. If you find a handler without a check, stop, report it as a BLOCKER finding, and do not ship code that calls it until it is fixed.

---

### SEC-AUTHZ-003: Object level check for every record identified by request input

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless, Mobile, Database |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, DYNAMIC TEST, STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Every read, update or delete of a record identified by a value from the request (path parameter, query string, body or header) MUST confirm on the server that the authenticated caller may act on that specific record. Queries for user owned records MUST be scoped by the user ID taken from the verified session, never by a user ID taken from the request alone.

**Why.** Broken object level authorization (IDOR) is the most common API flaw: changing an ID in a request returns or changes another user's record. Random IDs such as UUIDs reduce guessing but do not stop a user who obtains a valid ID.

**Implementation.**
- Look records up through the caller's scope, for example `where id = $1 and owner_id = session.userId`, not `where id = $1`.
- Return 404 (or 403) when the record exists but is not the caller's, with the same response as a missing record.
- Default stack: when the request goes through the Supabase Data API with the user's JWT, RLS ownership policies (SEC-AUTHZ-010) perform this check. When server code uses a privileged client, the handler performs it (SEC-AUTHZ-007).
- Apply the same check to signed URL creation, exports, and any background job started from a request.
- Owned by SEC-AGENT-008 in AGENTIC-DEV-SECURITY.md for this root cause (MCP server authorization); report one finding.

**Verify.**
1. For each resource type, create records as user A and user B, then as user A request read, update and delete on user B's record IDs; every attempt MUST fail and change nothing (WSTG-v42-ATHZ-04 method). A denial counts only as a 401, 403 or 404 with the response of a missing record, followed by a read back with the owner credential that shows the data unchanged; a 400 or 422 is not a denial. Pair every denial with a positive control: the same request shape sent by the record owner succeeds. For one handler, remove the ownership filter in a scratch branch and confirm the test fails.
2. Run a Semgrep rule that flags queries on owned tables whose only filter is an ID from `params`, `searchParams` or the request body.
3. Review each data access function and confirm the owner filter comes from the session object.
4. Test parent and child ids together: request a child record through a path that names your own parent id with another tenant's child id, and try to insert another user into your own tenant; both must fail.

**Evidence.** Passing two user test run per resource type, and a Semgrep report with no unscoped owned table queries.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2 [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-04 [SRC-186]; OWASP API Security Top 10 2023 API1:2023 [SRC-021]; OWASP IDOR Prevention Cheat Sheet (Verifying access controls, Mitigation, Identifier complexity) [SRC-035]; Escape, State of Security of Vibe Coded Apps (12 confirmed BOLA) [SRC-007].

**AI Agent Instruction.** When you write any query that takes a record ID from the request, add the owner or tenant filter from the session in the same query. Never filter owned data by an ID from the request alone, and never trust a `userId` field sent by the client. If an existing route fetches by ID without an ownership check, report it as a VERIFIED or SUSPECTED BLOCKER finding before continuing.

---

### SEC-AUTHZ-004: Writable field allowlist, no privilege fields from the client

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless, Mobile, Database |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, AUTOMATED TEST, CODE REVIEW |

**Requirement.** Every create and update operation MUST accept only an explicit allowlist of fields for that action. The schema for each write MUST name the editable fields by hand: a schema generated from the table type, a passthrough schema, or a spread of request data MUST NOT be used on a table that holds a privilege, ownership, tenant, plan, balance, status or verification column. Fields that control privilege, ownership or value, including role, owner ID, tenant ID, plan, price, credit balance and verification flags, MUST NOT be taken from the client and MUST be set by the server.

**Why.** Spreading a request body into an insert or update (mass assignment) lets a user set `role: 'admin'`, move a record into another tenant, or change what they pay. It is a common pattern in AI generated code.

**Implementation.**
- Parse each request with a schema (for example zod) that lists only the editable fields, and pass only the parsed object to the database call.
- Set owner, tenant and privilege fields from the session and server state after parsing.
- Default stack: with direct Supabase Data API writes, restrict column level `UPDATE` grants or use a `WITH CHECK` policy and trigger so users cannot change `role`, `tenant_id` or `owner_id` columns.
- Never pass `req.body`, `formData` entries or `...input` directly to an ORM `create` or `update`.
- Owned by SEC-DB-033 in DATABASE-SECURITY.md for this root cause (Client writable privileged columns); report one finding. This requirement keeps the request body allowlist for server routes.
- Owned by SEC-DB-035 in DATABASE-SECURITY.md for this root cause (Shared content integrity); report one finding.

**Verify.**
1. Run a Semgrep rule that flags request bodies or spread objects passed directly into insert, update or upsert calls.
2. For each write endpoint, send every column of the table that is not on the allowlist, taken from the live column list (and `role`, `owner_id`, `tenant_id`, `price`, `is_admin` as well), and confirm they are rejected or ignored; read the row back with a server credential and confirm the stored values do not change (WSTG-v42-ATHZ-03 method).
3. For tables written through the Data API, attempt the same column changes as an authenticated user and confirm a permission error or unchanged row.

**Evidence.** Semgrep report with no direct body writes, and passing tests showing privilege fields cannot be set by the client.

**Exceptions.** An internal admin function MAY accept a role field when it passes SEC-AUTHZ-020 and logs the change under a Pro edition requirement. Record the function in the function list (the access matrix of a Pro edition requirement in AUTH.md, or an equivalent table in the repository).

**References.** OWASP ASVS 5.0.0 v5.0.0-15.3.3 (L2, promoted to LAUNCH) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-03 [SRC-186]; OWASP API Security Top 10 2023 API3:2023 [SRC-021]; OWASP Mass Assignment Cheat Sheet (General Solutions) [SRC-030].

**AI Agent Instruction.** For every write you add, define a schema with only the editable fields and set owner, tenant, role and price fields on the server. Refuse to spread a request body into a database write. If a feature seems to need the client to send a privilege field, stop and ask the human how the server should derive it.

---

### SEC-AUTHZ-005: Authorization attributes come only from server controlled data

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Database, Mobile |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Roles, tenant membership, plan and every other attribute used in an authorization decision MUST come from data the user cannot edit: a server controlled table, or token claims written only by the server. Authorization code and database policies MUST NOT read user editable profile data, including Supabase `user_metadata`.

**Why.** Supabase `user_metadata` can be changed by the signed in user through the client library. A policy or handler that reads a role or tenant from it lets any user grant themselves admin or join any tenant.

**Implementation.**
- Store roles and memberships in tables that `anon` and `authenticated` cannot write.
- Default stack: if a role or tenant ID must be in the token, write it to `app_metadata` or add it through the Supabase Custom Access Token Hook, which reads from a server controlled table.
- Default stack: revoke execute on the hook function from `anon`, `authenticated` and `public` so it is not callable through the Data API.
- Keep the rule for every client: mobile apps and browser code never decide roles.
- Owned by SEC-DB-033 in DATABASE-SECURITY.md for this root cause (Client writable privileged columns); report one finding.
- Layer: this requirement covers authorization code in the application layer. The SQL policy check is SEC-DB-006 and writability of the attribute columns is SEC-DB-033.

**Verify.**
1. Run Supabase advisors (security) and confirm lint 0015_rls_references_user_metadata reports nothing.
2. Search code and SQL for `user_metadata`, `raw_user_meta_data` and `auth.jwt() -> 'user_metadata'` and confirm none feed an authorization decision.
3. As a normal user, update your own `user_metadata` to include `role: admin` and a foreign `tenant_id`, then call admin and tenant endpoints; all MUST be denied.
4. For one resource, name the column or claim that each layer (handler, RLS policy, helper function, storage policy) uses to decide ownership; all layers must derive it from the same source.

**Evidence.** Advisor export with no 0015 findings, search results reviewed, and the passing self elevation test.

**Exceptions.** Projects not using Supabase Auth apply the same rule to their provider's user editable profile fields. Record the field names reviewed.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.3.1, v5.0.0-8.2.1 [SRC-010]; Supabase Row Level Security guide (`auth.jwt()` caution) [SRC-070]; Supabase Database Advisors lint 0015_rls_references_user_metadata [SRC-076]; Supabase Custom Access Token Hook and Auth Hooks security model [SRC-157].

**AI Agent Instruction.** Never read `user_metadata` or any user editable field to decide access. Read roles and memberships from server controlled tables or `app_metadata`. If existing code or a policy uses `user_metadata` for access, report it as a CRITICAL finding and do not copy the pattern.

---

### SEC-AUTHZ-006: Authorization errors result in denial

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW |

**Requirement.** When an authorization check throws, times out, or cannot reach the data it needs (session store, roles table, membership table, policy engine), the request MUST be denied and MUST NOT continue to the protected operation.

**Why.** Checks wrapped in a `try` block that logs and continues, or that default to allow when a lookup returns nothing, turn any outage or malformed input into an authorization bypass.

**Implementation.**
- Have the authorization helper return an explicit allow decision only on success; any exception or empty result returns deny.
- Do not catch authorization errors in handlers except to return 401, 403 or 503.
- Treat a missing role, missing membership row or null session as deny.
- This requirement owns fail closed behaviour for authorization checks. Errors in authentication, input validation and signature checks are covered by SEC-LOG-019 in OBSERVABILITY.md.

**Verify.**
1. In tests, mock the roles or membership lookup to throw and to return null, then call a protected function; it MUST return an error status and change nothing.
2. Review `catch` blocks around authorization calls and confirm none continue to the protected operation.

**Evidence.** Passing failure injection tests for the authorization helper, and code review notes for its call sites.

**Exceptions.** Only a written risk acceptance with a named owner, an approver, a compensating control and an expiry date.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1 (deny unless explicitly permitted, L1), v5.0.0-16.5.3 (L2) [SRC-010]; OWASP Authorization Cheat Sheet (Exit Safely when Authorization Checks Fail) [SRC-034]. Related: SEC-LOG-019. Stage LAUNCH because failing open breaks the explicit permission rule of v5.0.0-8.2.1 (L1); v5.0.0-16.5.3 is cited for the principle and is not promoted.

**AI Agent Instruction.** Write authorization checks so the only path to allow is an explicit successful check. Never add a fallback that allows access when a lookup fails. If you see a check that fails open, report it and fix it before other work in that handler.

---

### SEC-AUTHZ-007: Privileged clients never act for a user without that user's permissions

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Serverless, Database |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW, AUTOMATED TEST |

**Requirement.** Server code handling a user's request MUST access data with that user's identity (a client carrying the user's token so RLS applies), or MUST perform an explicit ownership and tenant check for that user before each privileged call. A key or role that bypasses RLS MUST NOT be used to serve a user request without that check.

**Why.** A server that holds a service role key acts as a confused deputy: it has more rights than the user it serves. If a handler uses that key with IDs from the request, every user can reach every row, and RLS gives no protection.

**Implementation.**
- Create a per request database client from the caller's session for all user scoped reads and writes.
- Limit privileged clients to a small server only module used for jobs with no user context (webhooks, cron, migrations) or for named admin functions guarded by SEC-AUTHZ-020.
- Default stack: create the Supabase server client inside each request handler with the user's session. A secret key request that also carries the user's access token runs under that user's policies.
- Default stack: never import the secret key module into Server Actions or Route Handlers that serve normal users unless the handler has an explicit check recorded in the function list (the access matrix of a Pro edition requirement in AUTH.md, or an equivalent table in the repository).

**Verify.**
1. Search for every use of the service role or secret key (`SUPABASE_SERVICE_ROLE_KEY`, `sb_secret_`, admin client factories) and list the handlers that import it.
2. For each listed handler reachable by a normal user, confirm an explicit ownership and tenant check precedes each privileged query.
3. Run the two user test from SEC-AUTHZ-003 against each listed handler.

**Evidence.** The list of privileged client call sites with the check reviewed for each, and passing two user tests.

**Exceptions.** Background jobs with no user context are out of scope. Record them in the function list as system functions.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2 (L1), v5.0.0-8.3.3 (L3) [SRC-010]; NIST SP 800-53 Rev 5 AC-6 [SRC-062]; Supabase Row Level Security guide (Bypassing RLS) [SRC-070]; Supabase API keys (Secret key bypasses RLS) [SRC-071]. Stage LAUNCH because this is how v5.0.0-8.2.2 (L1) is met when server code holds a privileged key; v5.0.0-8.3.3 is cited for the confused deputy principle and is not itself promoted. Tool calls made by product AI agents are covered in AI-SECURITY.md.

**AI Agent Instruction.** Use a user scoped database client for any request made on behalf of a user. Do not reach for the service role or secret key to make a query work. If RLS blocks a query you need, stop and report it instead of switching to a privileged client (HULLPROOF.md hard rule 9).

---

## Per user data isolation

### SEC-AUTHZ-010: Ownership policies on user owned tables

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Database (Supabase) |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, AUTOMATED TEST, DYNAMIC TEST |

**Requirement.** Every user owned table in a schema exposed to clients MUST have policies that limit select, update and delete to rows whose owner column equals the authenticated user's ID, and insert and update `WITH CHECK` clauses that reject rows owned by anyone else. Policies for `anon` or `authenticated` on a user owned table MUST NOT use an always true condition.

**Why.** RLS that is enabled but has a permissive policy such as `using (true)` lets every signed in user read and change every row. Misconfigured RLS is the leading real world failure in Supabase backed AI built apps.

**Implementation.**
- Use `using ((select auth.uid()) = owner_id)` for select, update and delete, and `with check ((select auth.uid()) = owner_id)` for insert and update.
- Name the role in each policy with the `TO` clause.
- Index the owner column.
- RLS enablement, grants, views and security definer functions are set by DATABASE-SECURITY.md; this requirement covers what the ownership policy says.
- Owned by SEC-AUTHZ-014 in AUTH.md for this root cause (Tenant membership insert); report one finding.

**Verify.**
1. Run Supabase advisors (security) and confirm lints 0013_rls_disabled_in_public and 0024_permissive_rls_policy report nothing for user owned tables.
2. As user A, using only the publishable key and A's token, query, update and delete user B's rows through the Data API; expect no rows or a permission error.
3. As user A, insert a row with `owner_id` set to user B; expect rejection.

**Evidence.** Advisor export, pgTAP or Data API test results for each user owned table.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2 [SRC-010]; Supabase Row Level Security guide (Policy per operation, Specify roles) [SRC-070]; Supabase Securing your API (Grants and RLS) [SRC-072]; Supabase Database Advisors lints 0013, 0024 [SRC-076]; PostgreSQL 18 Row Security Policies [SRC-077]; Escape, State of Security of Vibe Coded Apps (misconfigured RLS as most common root cause) [SRC-007].

**AI Agent Instruction.** When you create or change a user owned table, write one policy per operation tied to `auth.uid()` with both `USING` and `WITH CHECK` where they apply, in the same migration. Never write `using (true)` for client roles on owned data. If a requested feature needs broader access, stop and ask which roles and rows it should cover.

---

### SEC-AUTHZ-012: Server side caches keyed by user and tenant

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, Backend, Serverless |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, AUTOMATED TEST |

**Requirement.** Any server side cache that stores data belonging to a user or tenant (framework data caches, in memory or module scope values, Redis or KV entries, memoized functions) MUST be keyed by the user ID when the data is visible to one user, or MUST NOT be cached. A key by tenant ID alone is allowed only for data that every member of that tenant may read under the access rules, and the entry is recorded as such.

**Why.** A cache keyed only by route or query serves the first user's data to everyone who follows. On the default stack, cached responses and clients shared across warm serverless instances are documented causes of users seeing each other's sessions and data.

**Implementation.**
- Include the user or tenant ID as part of every cache key for private data, and read it from the session, never from the request body.
- Do not hold per user data or per user clients in module scope variables.
- Default stack: do not use static rendering or incremental static regeneration for routes that read the session. Create the Supabase client inside each request handler, never at module scope.
- HTTP `Cache-Control` rules for private responses are in the session part of this document.

**Verify.**
1. Search for cache APIs (`unstable_cache`, `use cache`, `cache(`, Redis `get` and `set`, module level `let` or `const` holding query results) and confirm each private data entry key contains the user ID, and each tenant keyed entry holds only data every member may read.
2. In an integration test, request the same cached endpoint as user A then user B and confirm B never receives A's data. Use two members of the same tenant, one with a lower role, as well as users of two tenants.

**Evidence.** Code review list of cache call sites with keys, and the passing two user cache test.

**Exceptions.** Data that is identical for all users (public catalog, feature flags) MAY be cached without user keys. Record those cache entries as public.

**References.** OWASP ASVS 5.0.0 v5.0.0-14.2.2 (L2), v5.0.0-8.4.1 (L2, promoted to LAUNCH) [SRC-010]; RFC 9111 HTTP Caching [SRC-189]; OWASP Session Management Cheat Sheet (Web Content Caching) [SRC-033]; Supabase Auth session docs (ISR and auth, Fluid compute client sharing) [SRC-121]. Stage LAUNCH: SRC-121 documents cache and shared client session mixups as real failures on the default stack.

**AI Agent Instruction.** Before caching anything, decide whether it is private. If it is, put the session user or tenant ID in the key or do not cache it. Never store a per user client or query result in module scope. Report any existing cache of private data without a user or tenant key as a CRITICAL finding.

---

## Multi-tenancy

### SEC-AUTHZ-013: No operation crosses a tenant boundary

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Database, AI features |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, DYNAMIC TEST, CODE REVIEW |

**Requirement.** An operation by a user, including list, search, export, create, update, delete, file access and AI retrieval, MUST NOT read or change data in a tenant the user is not a current member of.

**Why.** A check that confirms the user is signed in but not that the data belongs to their organisation exposes every customer's data to every other customer. In B2B products one missed filter is a breach of every tenant.

**Implementation.**
- Scope every query on tenant owned data by the active tenant resolved under SEC-AUTHZ-015.
- Apply the scope to list and search endpoints, not only to single record fetches.
- Enforce the same boundary in the database with SEC-AUTHZ-014.
- Retrieval and embedding stores follow the tenant rules in AI-SECURITY.md.
- Owned by SEC-AUTHZ-036 for this root cause (Realtime channel authorization); report one finding. Step 5 still lists the realtime surface.

**Verify.**
1. Seed tenant X and tenant Y. As an admin of X, call every list, search, export and single record endpoint with Y's IDs and with no filter; no Y data MAY appear.
2. As a member of X, attempt create, update and delete targeting Y's records or with Y's tenant ID; every attempt MUST fail.
3. Repeat step 1 through the Data API for tables exposed to clients.
4. As a member of X, create a child record in X that names a parent id belonging to Y, through the API and through the Data API; it must fail.
5. List every surface that can return or accept tenant data: endpoints, Data API tables and functions, storage, realtime channels, exports, search, and jobs started from a request. Each is covered by steps 1 to 4 or is recorded as not tenant scoped, with a reason.
6. A denial counts only as a 401, 403 or 404 with the response of a missing record, followed by a read back with the owner credential that shows the data unchanged; a 400 or 422 is not a denial. Pair every denial with a positive control: the same request shape sent by the record owner succeeds. In a scratch branch remove the tenant filter from one handler and confirm the test fails.

**Evidence.** Passing two tenant test run covering every endpoint and exposed table.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.4.1 (L2, promoted to LAUNCH) [SRC-010]; OWASP API Security Top 10 2023 API1:2023 [SRC-021]; OWASP IDOR Prevention Cheat Sheet (Mitigation) [SRC-035].

**AI Agent Instruction.** In a multi tenant project, add the active tenant filter to every query on tenant owned data, including lists and searches. If you cannot tell which tenant a query should be scoped to, stop and ask. Report any tenant owned query without a tenant scope as a BLOCKER finding.

---

### SEC-AUTHZ-014: Tenant column and membership based RLS on tenant tables

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Database (Supabase) |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, CODE REVIEW, AUTOMATED TEST |

**Requirement.** Every tenant owned table MUST carry a non null tenant ID column, and its RLS policies MUST allow each operation only when the authenticated user has an active row in a server controlled membership table for that tenant. The policies MUST test every state column on the membership row (status, accepted at, removed at, expires at); removal deletes the row or sets a state the policies test, and an invited user has no membership row until acceptance. A row that references a parent MUST carry the parent's tenant, enforced by a composite foreign key on tenant and parent id, or by a `WITH CHECK` that proves the parent's tenant equals the row's tenant.

**Why.** Tenant isolation held only in application code fails the first time a query misses its filter or a client talks to the Data API directly. Checking membership in the policy keeps isolation in force for every path into the table.

**Implementation.**
- Add `tenant_id uuid not null references tenants(id)` and an index on it to every tenant owned table.
- Write policies such as `using ((select private.is_member(tenant_id)))`, with the matching `WITH CHECK` for insert and update, where `private.is_member` is the helper described below. A policy that reads the membership table directly needs `usage` on its schema and `select` on the table for `authenticated`, plus RLS on that table, so the helper is the better shape.
- Keep the membership table in a schema clients cannot write, or with policies that let only tenant admins change it through a guarded server function.
- If a helper function is used, follow the policy helper pattern in SEC-DB-008 in DATABASE-SECURITY.md: a security definer function in a schema that is not exposed through the Data API, `usage` on that schema and `execute` on the function granted to `authenticated` only, `search_path` pinned, the caller read from `auth.uid()`, and the tenant id as its only parameter (for example `private.is_member(tenant uuid)`). Do not copy vendor examples that place it in `public`.
- Default stack (checked 2026-10-03): Supabase's own RLS examples show a membership join (`tenant_id in (select ... from memberships where user_id = (select auth.uid()))`) and a JWT claim pattern. This requirement asks for the membership join.

**Verify.**
1. List all tables with a tenant relationship and confirm each has a non null `tenant_id`, an index, and policies that reference the membership table.
2. Run the two tenant Data API test from SEC-AUTHZ-013 against each table, including the child in your own tenant that names another tenant's parent id. If a helper function is used, confirm it cannot be called through `/rest/v1/rpc`.
3. As a member, try to insert a membership row for yourself in another tenant; expect rejection.
4. As a tenant owner, try to insert an existing user who belongs to another tenant, or any user without an invitation they accept, into your tenant; expect rejection.
5. Set the membership row of a member to each non active state (removed, invited, expired), and as that user read and write through the API and the Data API; every request must be denied. Remove a member, replay an access token issued before the removal, and expect denial.

**Evidence.** Schema review list per table, and passing policy tests.

**Exceptions.** None. Products using schema per tenant or database per tenant MUST record the model in the security decisions log and show equivalent isolation tests. A table with no `tenant_id` of its own that reaches the tenant through a join to a tenant owned parent table meets this requirement when the join uses a non null foreign key, the parent table is itself covered, any tenant column the child does have equals the parent's, and the two tenant test passes. Record the parent table.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.4.1 (L2, promoted to LAUNCH) [SRC-010]; Supabase Row Level Security guide [SRC-070]; PostgreSQL 18 Row Security Policies [SRC-077]; Supabase Custom Claims and RBAC, Advanced pgTAP Testing [SRC-157]; Supabase RAG with Permissions (RLS over WHERE) [SRC-158].

**AI Agent Instruction.** When you create a tenant owned table, add the tenant column, index and membership based policies in the same migration. Never create a tenant owned table without them, and never disable RLS to make a query return rows.

---

### SEC-AUTHZ-015: Active tenant resolved on the server from verified membership

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Serverless |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, AUTOMATED TEST, CODE REVIEW |

**Requirement.** The server MUST determine the active tenant for each request from the user's verified memberships (membership table or server written token claims) and MUST reject or ignore tenant ID values in request bodies, query strings and headers that do not match a current membership.

**Why.** Accepting `tenant_id` from the client lets a user read from or write into any organisation by changing one value.

**Implementation.**
- Resolve the tenant in one server helper that returns the tenant ID only after a membership lookup for the session user.
- When a URL contains a tenant slug, treat it as a selector and confirm membership before use.
- Drop `tenant_id` from write schemas (SEC-AUTHZ-004) and set it from the resolved tenant.
- Default stack: if the tenant ID is placed in the token, write it with the Custom Access Token Hook from the membership table, never from `user_metadata`.

**Verify.**
1. Run a Semgrep rule that flags `tenant_id`, `org_id` or `organization_id` read from `params`, `searchParams`, request bodies or headers without passing through the resolver.
2. Send requests with a foreign tenant ID in the body, query and header; expect 403 or the caller's own tenant data only.

**Evidence.** Semgrep report, and passing foreign tenant ID tests.

**Exceptions.** Single tenant products record that the requirement does not apply.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.4.1 (L2, promoted to LAUNCH), v5.0.0-15.3.3 (L2, promoted to LAUNCH) [SRC-010]; OWASP Mass Assignment Cheat Sheet (General Solutions) [SRC-030]; OWASP IDOR Prevention Cheat Sheet (Mitigation) [SRC-035]; Supabase Row Level Security guide (`auth.jwt()` caution) [SRC-070]; Supabase Custom Access Token Hook [SRC-157].

**AI Agent Instruction.** Always get the active tenant from the server side resolver. Never trust a tenant ID from the client. If a request carries a tenant ID that does not match a membership, deny it rather than switching tenants silently.

---

## Admin systems

### SEC-AUTHZ-020: Admin functions guarded by a server side admin role check

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Serverless |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, DYNAMIC TEST, STATIC ANALYSIS |

**Requirement.** Every admin function (in product admin pages, admin APIs, admin Server Actions and admin Edge Functions) MUST check on the server that the caller holds an admin role read from a server controlled source, and MUST deny anonymous and normal user callers.

**Why.** Admin routes reachable by any signed in user, or by anyone, give direct control over every account and every record. This is one of the most damaging and most common function level flaws.

**Implementation.**
- Group admin handlers behind one `requireAdmin` helper that reads the role from the roles table or `app_metadata` (SEC-AUTHZ-005).
- Put admin code under a dedicated path or module so static rules can find every admin handler.
- Do not rely on an unlisted URL or a hidden link as protection.

**Verify.**
1. List the admin handlers from the framework route table and the exported Server Actions: every handler that reads or changes data of other users or tenants, or changes a role, plan or entitlement, whether or not the team classifies it as admin. Confirm each calls the admin guard (Semgrep rule on the admin path or module).
2. Call each admin handler with no session and with a normal user session; every call MUST return 401 or 403 and change nothing, and the same request by an admin MUST succeed (positive control). In a scratch branch remove the admin guard from one handler and confirm the test fails.

**Evidence.** Semgrep report and the passing normal user test run against every admin handler.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1 [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-02 [SRC-186]; OWASP API Security Top 10 2023 API5:2023 [SRC-021]; NIST SP 800-53 Rev 5 AC-6(10) [SRC-062].

**AI Agent Instruction.** Put every admin handler behind the admin guard, read the role from a server controlled source, and write the normal user denial test with it. Report any admin function without the guard as a BLOCKER finding.

---

### SEC-AUTHZ-021: MFA required for in product admin accounts

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CONFIG REVIEW |

**Requirement.** Every account holding an admin or support role in the product MUST complete multi factor authentication before any admin or support function is allowed, and admin functions MUST deny sessions that did not complete MFA. A code sent by SMS or email MUST NOT be the only second factor of an admin or support account. Recovery of an admin or support account MUST NOT remove or replace its MFA factor with an emailed link alone (a Pro edition requirement applies to these accounts from LAUNCH).

**Why.** A phished or reused password on an admin account gives the attacker every customer's data. MFA blocks most of these takeovers at low cost.

**Implementation.**
- Require MFA enrollment when a user is granted an admin or support role. Use an authenticator app code at the least, and a passkey or security key where the provider has one (a Pro edition requirement). Do not accept SMS or email codes as the second factor.
- In the admin guard, check the session's assurance level as well as the role.
- Default stack: with Supabase Auth, check the session's authenticator assurance level in the admin guard and in admin RLS policies. Supabase documents an `aal` claim in the JWT that becomes `aal2` after the second factor, and an `amr` claim listing the methods used.
- MFA for vendor consoles (Supabase, Vercel, GitHub, payment dashboards) is covered in INFRASTRUCTURE-SECURITY.md.

**Verify.**
1. Sign in as an admin with password only and call an admin function; expect denial.
2. Complete MFA and repeat; expect success.
3. Export the list of admin and support accounts and confirm each has an enrolled second factor.
4. Start recovery for an admin test account with MFA enrolled, using the emailed link only. The link must not remove or replace the MFA factor, and the next sign in must still ask for it.
5. Enrolment trust on first use: check that the second factor is bound by a step that proves the account owner, such as a signed in session that already passed another factor, so that whoever signs in first cannot bind a factor to someone else's admin account.
6. Enrol an admin test account with only a phone factor (SMS) and call an admin function; expect denial.

**Evidence.** Passing MFA gate tests, and the account export.

**Exceptions.** A CRITICAL exception needs a named owner, an approver, a compensating control and an expiry date per the Severity section of STANDARD.md.

**References.** NIST SP 800-63B-4 and the Hullproof AAL to stage mapping (admins: any MFA at LAUNCH) [SRC-060]; NIST SP 800-53 Rev 5 IA-2(1) [SRC-062]; CISA Secure by Design (Mandate MFA for privileged users) [SRC-063]; OWASP Multifactor Authentication Cheat Sheet [SRC-030]; OWASP ASVS 5.0.0 v5.0.0-6.4.4 [SRC-010]; OWASP Top 10:2025 A07:2025 [SRC-020].

**AI Agent Instruction.** Make the admin guard check both the admin role and a completed MFA level. Never add a bypass for admins without MFA, including for testing in production.

---

## Support tools

### SEC-AUTHZ-031: Support tools never hold an all tenant RLS bypass key

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Backend, Database (Supabase) |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, STATIC ANALYSIS |

**Requirement.** Support tools MUST read customer data through a server path that applies the target customer's user and tenant scope and the support role's rules, and MUST NOT hold or use a key or database role that bypasses RLS for all tenants.

**Why.** A support tool built on the service role key can read every tenant's data in one query. If a support account or the tool is compromised, every customer is exposed at once.

**Implementation.**
- Route support reads through server functions that take the target tenant, check the support role and the logged reason, and query only that tenant.
- Default stack: if a privileged client is unavoidable, confine it to these functions, add explicit tenant filters, and keep the key out of any support front end bundle.
- Use a dedicated database role for support queries with grants limited to the tables support needs.

**Verify.**
1. Search the support tool code for the service role or secret key and for admin clients; each use MUST be inside a guarded server function with a tenant filter.
2. As a support user scoped to tenant X, attempt a query that would return tenant Y data; expect denial or no rows.

**Evidence.** Code search results and the passing cross tenant support test.

**Exceptions.** A CRITICAL exception needs a named owner, an approver, a compensating control and an expiry date per the Severity section of STANDARD.md. For a small staff team, a written risk acceptance is acceptable when these compensating controls are in place and recorded: aal2 (second factor) for every support account, an audit record with a stated reason for each customer data view, and minimal support roles.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.4.1 (L2, promoted to LAUNCH) [SRC-010]; Supabase API keys (Secret key bypasses RLS) [SRC-071]; PostgreSQL 18 Row Security Policies (BYPASSRLS) [SRC-077]; NIST SP 800-53 Rev 5 AC-6 [SRC-062].

**AI Agent Instruction.** Do not build support features on an unscoped service role client. If the only way to get the data is to bypass RLS for all tenants, stop and report it.

---

### SEC-AUTHZ-036: Realtime channels authorize every join, broadcast and presence update per user and tenant

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile, Database (Supabase) |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, DYNAMIC TEST, CODE REVIEW |

**Requirement.** Where the product offers realtime channels (WebSocket or similar subscriptions, broadcast, presence, rooms or pub/sub topics) that carry user or tenant data, the server or a database policy MUST authorize each join, each message a client sends and each presence update, per user and per tenant, using the verified identity and the current membership. A channel name, topic or room id MUST NOT act as a secret or as the only check, and no public channel MAY carry user or tenant data. On Supabase, such channels MUST be private (`private: true` on the client) with row level security policies on `realtime.messages` that test membership or ownership of the topic for each operation (receive and send, broadcast and presence), and the project setting that allows public access to channels MUST be off. On Socket.IO or a similar server, a socket MUST join a room only after server code has checked the user's right to that room, and a room name or id sent by the client is an input to that check, not the check. Access MUST end within a stated time after membership is removed. This requirement applies only to products that use realtime channels.

**Why.** A channel named after a tenant id is easy to learn or guess, and a public channel delivers its events to anyone who can connect. A signed in user of one tenant then receives another tenant's live data, or sends forged events into it, while every endpoint and table test still passes because none of them touches the channel. Realtime caches the access decision for the life of the connection, so removing a member does not stop events that are already flowing.

**Implementation.**
- Supabase: create the policies on `realtime.messages` with `realtime.topic()` compared to a membership or ownership table, one policy for receive (`select`) and one for send (`insert`), and filter on the `extension` column for broadcast and presence. Set `private: true` when the client creates the channel. Turn off the public access setting under Realtime Settings so a client cannot fall back to a public channel [SRC-371].
- Supabase: the policy result is cached per connection and refreshed when the client connects and subscribes or sends a new JWT. A removed member keeps receiving until the token expires or a new one is sent, so keep the JWT lifetime short and disconnect the user on removal [SRC-371].
- Supabase Postgres Changes on a table follow that table's row level security, so the table policies of SEC-DB-001 and SEC-DB-002 govern them [SRC-371].
- Socket.IO and similar: rooms exist only on the server, so a client cannot join one by itself [SRC-372]. Put the membership check in the handler that calls `socket.join`, and do not rely on connection middleware alone, because it runs once per connection [SRC-372]. Derive the room name on the server from the verified user and tenant instead of accepting a name from the client.
- Check authorization again on each send, because a client that may listen to a channel is not always allowed to publish to it.
- Keep payloads small. Send ids and let the client fetch the record through an authorized endpoint when the event carries more than the channel's audience may see.
- Per tenant isolation of endpoints and tables is owned by SEC-AUTHZ-013; this requirement owns the realtime surface.

**Verify.**
1. List every realtime channel, topic, room and Postgres Changes subscription in the product, with what data it carries and who may join. Record any that carry no user or tenant data.
2. Seed tenant X and tenant Y. As a member of X, subscribe to Y's topic and to a guessed topic, then send a broadcast and a presence update to each. Expect a rejection or an empty subscription, and no event delivered to Y's members.
3. Run the positive control: a member of Y subscribes to Y's topic, receives an event sent by the server, and may send only if the policy allows sending.
4. Remove a member from the tenant while that member's connection is open. Expect events to stop within the stated time, and confirm the stated time in the evidence.
5. On Supabase, read the policies on `realtime.messages` and confirm each tests the topic against membership or ownership. Try joining the same topic with `private: false`; expect it to fail. Confirm the public access setting is off in Realtime Settings. On Socket.IO, search for every `join` call and confirm a server side check runs before it.

**Evidence.** The channel list, the two tenant test output including the positive control, the removal test result, and the policy or handler listing.

**Exceptions.** A channel that carries only data meant for every visitor, that clients cannot send to, and that is recorded as such in step 1 may be public. Products with no realtime channel record the search that shows it, for example a search for `channel(`, `.subscribe(`, `socket.io`, `WebSocket` and `realtime` over client and server code.

**References.** Supabase Realtime Authorization [SRC-371]; Socket.IO Rooms and Middlewares [SRC-372]; OWASP API Security Top 10 2023 API1:2023 [SRC-021]; OWASP Top 10:2025 A01:2025 [SRC-020].

**AI Agent Instruction.** When you add a realtime channel, make it private, add the membership policy or the server side check in the same change, and write the two tenant test. Never name a channel after a tenant id and treat the name as protection. If a feature asks a client to choose its own room or topic, stop and ask for the server side check.
