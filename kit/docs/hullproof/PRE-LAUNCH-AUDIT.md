# Pre Launch Audit

_Generated from the requirement documents. Do not edit by hand._

The release checklist for Hullproof. It lists every BLOCKER requirement and every CRITICAL requirement, with how to check each one and what evidence to keep. The `/hullproof-prelaunch` skill runs this list.

## When to run it

Run it before every production release, and before any due diligence or security questionnaire review.

## How to use it

1. Record the commit SHA being released, the target (URL, app build, or environment), the declared stage (LAUNCH, GROWTH, or SCALE), and the date.
Record these in `docs/security/STAGE.md` (stage, markets served, where risk acceptances live, rollback path) so every run reuses them.
2. Work through each item and record one result per item from the states below. Do not invent other states.
3. Attach evidence for every PASS and every NOT APPLICABLE. The Evidence line under each item says what to keep. The full Verify steps and Exceptions live in the linked requirement.
Gate answers in `docs/security/STAGE.md` (the Applicability gates table under each domain document's coverage map lists the gates) mark ranges of items NOT APPLICABLE, with the gate named as the reason. A gate whose list holds a BLOCKER clears it only with a recorded search that names the commit, the exact search patterns and the result counts, and only after the reviewer has re run that search over every tracked file except dependency folders in this session and found nothing. The owner's statement alone never clears a BLOCKER. A search must include protocol terms and route patterns for hand written endpoints, not only library names. A gate answered Yes or left blank keeps its items in scope.
4. Fill in the results table and the sign off block at the end. The table has one row per item with its severity and owning document already filled in. Add the result, a root cause or finding id (rows that fail for the same underlying fix share one id, so 40 FAIL rows that need 15 fixes read as 15 fixes), the evidence class, whether the result was reused from an earlier run or rechecked on this commit, the evidence link, and notes. Only a FAIL row, or a PASS row that is not a BLOCKER, from a report you wrote yourself in this release is ever reused. Every BLOCKER is rechecked on this commit.
In the free edition, write the gate outcome in the sign off block as READY (FREE SCOPE) or READY WITH ACCEPTED RISK (FREE SCOPE), and record the edition and scope. The label means the gate was met for the free edition's requirement set only, and the HIGH, MEDIUM and LOW requirements that only Hullproof Pro holds are outside the free scope. Hullproof Pro keeps READY.

## Result states

| Result | Meaning |
|--------|---------|
| PASS | The Verify steps were run on this commit or target and the evidence is attached. With evidence class static it is written PASS (static), and it counts for a BLOCKER only where the requirement's Verify and Evidence lines can be satisfied by reading the repository. |
| FAIL | The requirement is not met. Record the finding or root cause id. Rate it with the Severity rules in STANDARD.md; a rating below a BLOCKER item goes in the Lowered BLOCKER requirements table. |
| NOT APPLICABLE | The system type in Applies To does not exist in the project, or the requirement's own Exceptions field is met. Record the reason and attach the evidence. |
| NOT ASSESSED | The item could not be settled in this run. It must carry one of the routed sub states below. An unsettled BLOCKER or CRITICAL item counts as open at the gate. |

NOT ASSESSED always names a route, so the owner knows what to do next.

| Sub state | Owner action |
|-----------|--------------|
| NEEDS DASHBOARD | The owner opens the provider dashboard or console and records the setting with a screenshot or export. |
| NEEDS BUILD | The owner runs a production build or CI job and attaches the output. |
| NEEDS DYNAMIC TEST | Someone tests the running app or a staging copy, then records the request and the response. |
| ASK OWNER | The owner answers a question that the code and the dashboards cannot answer. Write the question in Notes. |
| ATTESTATION | The owner or the provider gives a written statement, with the date and who made it. |
| UNKNOWN | The reviewer could not tell which route applies. Choose one of the routes above before sign off. |

A static run, which reads code and configuration only, cannot end READY while any BLOCKER or CRITICAL item is in NOT ASSESSED, whatever the sub state. Each of those items needs its owner action done and the result changed to PASS, FAIL or NOT APPLICABLE first (or, for a CRITICAL item, a current written acceptance within the limits in STANDARD.md). A dashboard export, a provider screenshot or a test result settles an item only if it names the commit or the date, is no more than 30 days old (Hullproof policy), and was taken after the newest migration in the audited commit. An export, screenshot or test log never moves a public exposure BLOCKER (public buckets and storage, anonymous data API access, exposed keys, open endpoints) to PASS: the checker runs the anonymous request itself, or the row stays NOT ASSESSED: NEEDS DYNAMIC TEST and the export is owner evidence for the human reviewer.

Evidence class says how the result was proven: static (code or configuration read), dashboard, build, or dynamic (tested against a running system). Reused or rechecked says whether the result was carried over from an earlier run on the same commit or checked again now.

## How results map to the gate outcome

The outcome follows the Production Security Gate in [STANDARD.md](STANDARD.md).

| Result | Gate outcome |
|--------|--------------|
| Any BLOCKER item is FAIL at any rating (a lowered rating does not change this), or NOT ASSESSED in any sub state | NOT READY. BLOCKER requirements cannot be waived. |
| Any CRITICAL item is FAIL or NOT ASSESSED with no fix, no settling evidence and no current written acceptance | NOT READY |
| Every failed CRITICAL item outside the protected classes (credentials and secrets exposure, authentication, tenant isolation, payments) has a written acceptance, and every unsettled CRITICAL item outside them is settled or accepted. A protected class item is fixed, never accepted. Each acceptance names the owner, an independent approver, the compensating control and an expiry date, within the limits in STANDARD.md (at most 90 days, one renewal, no more than 3 open per release, Hullproof policy) | READY WITH ACCEPTED RISK, if the rest of the gate holds |
| No BLOCKER or CRITICAL item failed or left unsettled | READY, if the rest of the gate holds. In the free edition the label is READY (FREE SCOPE). |

This list covers gate conditions G-3, G-4 and G-5. G-3 also needs the Lowered BLOCKER requirements table reviewed: a finding under a BLOCKER requirement is never rated below CRITICAL, and a lowered row needs code evidence and an independent reviewer. If an audit report and this checklist both exist for this commit, compare them on every BLOCKER and keep the worse status until evidence settles it (G-4). A READY outcome also needs G-1, G-2, G-6, G-7 and G-8: a declared stage, an audit report for this commit (one still in progress does not count), every HIGH finding resolved or accepted, scan results attached, and a known rollback path. G-1 and G-7 do not accept a self declared fact without the file that shows it and its date. HIGH, MEDIUM and LOW requirements are covered by a full audit report in the format of [templates/AUDIT-REPORT.md](templates/AUDIT-REPORT.md), not by this list. Hullproof Pro produces one with `/hullproof-security-audit`; in the free edition, attach an audit report made by hand or by a reviewer in that format, or the outcome stays NOT READY.

Stage definitions are in [STANDARD.md](STANDARD.md). Where an item shows a Market stage line, the stage depends on the markets served. Every market a requirement names applies unless `docs/security/STAGE.md` excludes it.

## Part 1: BLOCKER requirements

Every BLOCKER applies from LAUNCH and cannot be waived. 43 items.

### AUTH.md

- [ ] **SEC-AUTH-002** Server verifies identity tokens before trusting them ([AUTH.md](AUTH.md#sec-auth-002-server-verifies-identity-tokens-before-trusting-them)) | BLOCKER | PARTIAL | AUTOMATED TEST, STATIC ANALYSIS
  Check: (1) Write an automated test that calls three protected endpoints chosen by the reviewer with: no token, a token with a changed payload and the original signature, an `alg: none` token, an expired token, and a token signed by a different key. (2) Run Semgrep for `jwt.decode(`, `jose.decodeJwt(`, and `supabase.auth.getSession(` in server files; each hit must be justified or removed. (3) Review the verification configuration for a fixed algorithm list and a fixed key source.
  Evidence: Passing test file with the five negative cases, and the Semgrep report.
- [ ] **SEC-AUTH-008** No default, shared or seeded accounts in production ([AUTH.md](AUTH.md#sec-auth-008-no-default-shared-or-seeded-accounts-in-production)) | BLOCKER | PARTIAL | SECRET SCAN, CONFIG REVIEW
  Check: (1) Run Gitleaks over seed files, migrations and fixtures for fixed passwords. (2) List production users created by seed or migration scripts, and users whose email matches seed file emails; there must be none. (3) Confirm the seed script contains a production guard. (4) List production users whose email or creation source matches QA, test or agent tooling (for example addresses with `test`, `qa` or `example`, and users created from CI or agent sessions), and list non production accounts and credentials present in the production provider console; there must be none.
  Evidence: Gitleaks report, the production user query result, and the seed script guard.
- [ ] **SEC-AUTH-010** No authentication bypass paths in production ([AUTH.md](AUTH.md#sec-auth-010-no-authentication-bypass-paths-in-production)) | BLOCKER | PARTIAL | STATIC ANALYSIS, CODE REVIEW, DYNAMIC TEST
  Check: (1) Search for routes or handlers named like `dev-login`, `test-login`, `impersonate`, `bypass`, `as-user`, and for headers or query parameters that set a user ID. (2) List every environment variable read inside session creation and the authentication middleware, and explain each one; search for environment checks such as `NODE_ENV !== 'production'` around session creation. (3) Against the staging URL (never production), call any candidate route found; it must return 404 or 401.
  Evidence: Search results and the dynamic test output.
- [ ] **SEC-AUTHZ-002** Server side permission check in every handler, deny by default ([AUTH.md](AUTH.md#sec-authz-002-server-side-permission-check-in-every-handler-deny-by-default)) | BLOCKER | PARTIAL | STATIC ANALYSIS, AUTOMATED TEST, DYNAMIC TEST, CODE REVIEW
  Check: (1) Run a Semgrep rule that flags exported Server Actions, Route Handlers and API routes with no call to the project's authorization helper. (2) Generate the list of functions under test from the framework route table or file tree and from every exported Server Action, not from the access matrix. (3) Replay captured requests for every state changing endpoint without a token and confirm denial (WSTG-v42-ATHZ-02 method).
  Evidence: Semgrep report with zero unguarded handlers, and a passing test run covering each function with denied and allowed roles.
- [ ] **SEC-AUTHZ-003** Object level check for every record identified by request input ([AUTH.md](AUTH.md#sec-authz-003-object-level-check-for-every-record-identified-by-request-input)) | BLOCKER | PARTIAL | AUTOMATED TEST, DYNAMIC TEST, STATIC ANALYSIS, CODE REVIEW
  Check: (1) For each resource type, create records as user A and user B, then as user A request read, update and delete on user B's record IDs; every attempt MUST fail and change nothing (WSTG-v42-ATHZ-04 method). (2) Run a Semgrep rule that flags queries on owned tables whose only filter is an ID from `params`, `searchParams` or the request body. (3) Review each data access function and confirm the owner filter comes from the session object. (4) Test parent and child ids together: request a child record through a path that names your own parent id with another tenant's child id, and try to insert another user into your own tenant; both must fail.
  Evidence: Passing two user test run per resource type, and a Semgrep report with no unscoped owned table queries.
- [ ] **SEC-AUTHZ-010** Ownership policies on user owned tables ([AUTH.md](AUTH.md#sec-authz-010-ownership-policies-on-user-owned-tables)) | BLOCKER | PARTIAL | CONFIG REVIEW, AUTOMATED TEST, DYNAMIC TEST
  Check: (1) Run Supabase advisors (security) and confirm lints 0013_rls_disabled_in_public and 0024_permissive_rls_policy report nothing for user owned tables. (2) As user A, using only the publishable key and A's token, query, update and delete user B's rows through the Data API; expect no rows or a permission error. (3) As user A, insert a row with `owner_id` set to user B; expect rejection.
  Evidence: Advisor export, pgTAP or Data API test results for each user owned table.
- [ ] **SEC-AUTHZ-013** No operation crosses a tenant boundary ([AUTH.md](AUTH.md#sec-authz-013-no-operation-crosses-a-tenant-boundary)) | BLOCKER | PARTIAL | AUTOMATED TEST, DYNAMIC TEST, CODE REVIEW
  Check: (1) Seed tenant X and tenant Y. (2) As a member of X, attempt create, update and delete targeting Y's records or with Y's tenant ID; every attempt MUST fail. (3) Repeat step 1 through the Data API for tables exposed to clients. (4) As a member of X, create a child record in X that names a parent id belonging to Y, through the API and through the Data API; it must fail. (5) List every surface that can return or accept tenant data: endpoints, Data API tables and functions, storage, realtime channels, exports, search, and jobs started from a request. (6) A denial counts only as a 401, 403 or 404 with the response of a missing record, followed by a read back with the owner credential that shows the data unchanged; a 400 or 422 is not a denial.
  Evidence: Passing two tenant test run covering every endpoint and exposed table.
- [ ] **SEC-AUTHZ-014** Tenant column and membership based RLS on tenant tables ([AUTH.md](AUTH.md#sec-authz-014-tenant-column-and-membership-based-rls-on-tenant-tables)) | BLOCKER | PARTIAL | CONFIG REVIEW, CODE REVIEW, AUTOMATED TEST
  Check: (1) List all tables with a tenant relationship and confirm each has a non null `tenant_id`, an index, and policies that reference the membership table. (2) Run the two tenant Data API test from SEC-AUTHZ-013 against each table, including the child in your own tenant that names another tenant's parent id. (3) As a member, try to insert a membership row for yourself in another tenant; expect rejection. (4) As a tenant owner, try to insert an existing user who belongs to another tenant, or any user without an invitation they accept, into your tenant; expect rejection. (5) Set the membership row of a member to each non active state (removed, invited, expired), and as that user read and write through the API and the Data API; every request must be denied.
  Evidence: Schema review list per table, and passing policy tests.
- [ ] **SEC-AUTHZ-020** Admin functions guarded by a server side admin role check ([AUTH.md](AUTH.md#sec-authz-020-admin-functions-guarded-by-a-server-side-admin-role-check)) | BLOCKER | PARTIAL | AUTOMATED TEST, DYNAMIC TEST, STATIC ANALYSIS
  Check: (1) List the admin handlers from the framework route table and the exported Server Actions: every handler that reads or changes data of other users or tenants, or changes a role, plan or entitlement, whether or not the team classifies it as admin. (2) Call each admin handler with no session and with a normal user session; every call MUST return 401 or 403 and change nothing, and the same request by an admin MUST succeed (positive control).
  Evidence: Semgrep report and the passing normal user test run against every admin handler.

### API-SECURITY.md

- [ ] **SEC-API-001** Authenticate every non public endpoint ([API-SECURITY.md](API-SECURITY.md#sec-api-001-authenticate-every-non-public-endpoint)) | BLOCKER | PARTIAL | DYNAMIC TEST, AUTOMATED TEST, STATIC ANALYSIS
  Check: (1) Capture every API request the app makes (browser devtools or a proxy) and list every Server Action and Route Handler from the code. (2) Replay each one with no cookie, no `Authorization` header and no secret; every non allowlisted endpoint must return 401 or 403 with no data and no state change. (3) Run a Semgrep rule that flags `"use server"` functions and route handlers with no call to the shared auth helper before data access. (4) Call each cron and internal route without its secret and with a wrong secret; expect 401.
  Evidence: Endpoint list with the public allowlist; passing unauthenticated replay test suite; Semgrep report with zero unresolved findings.
- [ ] **SEC-API-101** Verify the webhook sender before processing ([API-SECURITY.md](API-SECURITY.md#sec-api-101-verify-the-webhook-sender-before-processing)) | BLOCKER | PARTIAL | DYNAMIC TEST, AUTOMATED TEST, STATIC ANALYSIS, CODE REVIEW
  Check: (1) Send an unsigned request, a request with a wrong signature, and a correctly signed request whose body has one byte changed. (2) Send a valid signed event from the provider's test mode or CLI. It must be accepted. (3) Run Semgrep for `JSON.stringify(req.body)`, `request.json()` or framework body parsers inside webhook verification code. (4) Review every route registered with a provider and confirm verification runs as the first operation in each. (5) In a staging deploy, unset and then blank the verification secret.
  Evidence: Passing automated test file covering the four negative cases and one positive case per webhook route; Semgrep report with no findings on webhook code.
- [ ] **SEC-API-125** Set prices and plans from the server catalog ([API-SECURITY.md](API-SECURITY.md#sec-api-125-set-prices-and-plans-from-the-server-catalog)) | BLOCKER | PARTIAL | MANUAL TEST, STATIC ANALYSIS, CODE REVIEW
  Check: (1) Using provider test keys only, tamper with price, plan, currency and discount in the checkout request. The created checkout must use catalog values. (2) Run Semgrep for checkout code reading `amount`, `price`, `currency` or `discount` from the request body.
  Evidence: Manual test record with tampered requests; clean Semgrep report.
- [ ] **SEC-API-126** Grant entitlements only from verified server side signals ([API-SECURITY.md](API-SECURITY.md#sec-api-126-grant-entitlements-only-from-verified-server-side-signals)) | BLOCKER | PARTIAL | MANUAL TEST, STATIC ANALYSIS, CODE REVIEW
  Check: (1) Visit the checkout success URL without paying, and post a fake purchase result from the mobile client. Nothing must be granted. (2) Run Semgrep for writes to entitlement tables outside the webhook and verify paths. (3) Confirm client roles cannot write entitlement tables (RLS test).
  Evidence: Manual test record; Semgrep report; RLS test output.
- [ ] **SEC-API-132** Require the RevenueCat authorization header ([API-SECURITY.md](API-SECURITY.md#sec-api-132-require-the-revenuecat-authorization-header)) | BLOCKER | PARTIAL | CONFIG REVIEW, DYNAMIC TEST, CODE REVIEW
  Check: (1) Send a webhook request with no header and with a wrong header. Both must be rejected with no side effect. (2) Confirm the header is set in the RevenueCat dashboard for every environment.
  Evidence: Passing negative tests; dashboard configuration record.
- [ ] **SEC-API-133** Verify Apple notifications with the full certificate chain ([API-SECURITY.md](API-SECURITY.md#sec-api-133-verify-apple-notifications-with-the-full-certificate-chain)) | BLOCKER | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) Send a payload signed with a self generated certificate chain. It must be rejected. (2) Send a valid sandbox payload to the production handler. It must be rejected or ignored (SEC-API-135). (3) Review the verifier configuration for bundle ID and environment.
  Evidence: Passing negative tests; code review note.

### BACKEND-SECURITY.md

- [ ] **SEC-API-017** Parameterize every database query ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-017-parameterize-every-database-query)) | BLOCKER | PARTIAL | STATIC ANALYSIS, CODE REVIEW, DYNAMIC TEST
  Check: (1) Run Semgrep rules for template literals or string concatenation passed to `sql.raw`, `execute`, `query`, `rpc` and similar sinks, and to the filter sinks `.or(`, `.and(`, `.not(`, `.filter(`, `.textSearch(`, `.select(` and `.order(` and to GraphQL query strings. (2) Review every raw SQL call that remains. (3) In a non production environment, send injection payloads to every search, filter, select and identifier parameter, in the dialect of the sink that parameter reaches.
  Evidence: Semgrep report with zero unresolved findings, the list of reviewed raw SQL and filter string sites, and the dynamic test output.
- [ ] **SEC-API-020** Never run shell commands built from untrusted data ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-020-never-run-shell-commands-built-from-untrusted-data)) | BLOCKER | PARTIAL | STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run Semgrep for `child_process.exec`, `execSync`, `spawn` with `shell: true`, and template literals passed to any process API. (2) Run Semgrep for `execFile`, `spawn`, `execa` and `fork` whose first argument is a shell, an interpreter, `git`, `tar`, `ssh`, `find`, `env`, `xargs`, `curl` or `ffmpeg`, or whose argument array holds a non literal element. (3) For each subprocess call that takes an untrusted value, send a help flag, a version flag, a short option and an output option in every untrusted argument position and assert the value is rejected or treated as data.
  Evidence: Semgrep report with zero unresolved findings, the list of reviewed subprocess sites with the source of each untrusted argument, and the option probe results.
- [ ] **SEC-API-021** Never evaluate untrusted data or model output as code ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-021-never-evaluate-untrusted-data-or-model-output-as-code)) | BLOCKER | PARTIAL | STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run Semgrep for `eval(`, `new Function(`, `Function(`, `vm.run*`, `vm.Script`, `vm.compileFunction`, `import(` and `require(` with a non constant specifier, and string arguments to timers, then run the rule over the indirect forms named in the Requirement. (2) Review each hit and trace its input to a constant source. (3) For each dependency hit, trace it with `pnpm why` or `npm ls` and classify it as reachable from request handling or build only. (4) Search for template compile or render calls whose template argument is not a constant or a file path, then send template syntax (`{{7*7}}`, `${7*7}`, `<%= 7*7 %>`) in every field that feeds a template or an expression; the output must show the literal text.
  Evidence: Semgrep report with zero unresolved findings, the list of reviewed eval, template and expression sites, and the template probe output.

### DATABASE-SECURITY.md

- [ ] **SEC-DB-001** Row level security enabled on every exposed table ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-001-row-level-security-enabled-on-every-exposed-table)) | BLOCKER | FULL | CONFIG REVIEW, DYNAMIC TEST
  Check: (1) Run the Supabase security advisor (`get_advisors` with type security, or Studio Advisors) and confirm zero findings for lint `0013_rls_disabled_in_public` and `0007_policy_exists_rls_disabled`. (2) Run `select schemaname, tablename from pg_tables where schemaname in (<exposed schemas>) and rowsecurity = false;` and expect no rows. (3) For every exposed table, send `GET /rest/v1/<table>?select=*` and an insert with only the publishable key and no user token (curl), and expect an empty result or a permission error.
  Evidence: Advisor export with no 0013 or 0007 findings, the query output above, and the saved unauthenticated replay results dated before release.
- [ ] **SEC-DB-033** Client roles cannot write billing, entitlement, verification, role or credential columns ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-033-client-roles-cannot-write-billing-entitlement-verification-role-or-credential-columns)) | BLOCKER | PARTIAL | CONFIG REVIEW, DYNAMIC TEST, STATIC ANALYSIS
  Check: (1) On the live database, list client write grants on the privileged columns: `select table_schema, table_name, column_name, grantee, privilege_type from information_schema.column_privileges where grantee in ('anon', 'authenticated', 'PUBLIC') and privilege_type in ('INSERT', 'UPDATE') and table_schema in (<exposed schemas>);`. (2) Read `supabase/migrations` in order and rebuild the final grants and policies for every table with a client write policy (or run the Hullproof Pro helper `tools/hullproof/helpers/policy_set.py` where installed), and confirm no client writable column that holds billing, entitlement, verification, role or credential state remains. (3) Two user negative test. (4) For every table with a client write policy, confirm the record from Implementation exists. (5) Derive the record instead of accepting it.
  Evidence: The step 1 query output with its date, the rebuilt grant and policy set, the saved negative test requests and responses, the per table record, and the step 5 search results.
- [ ] **SEC-DB-034** Credential and token tables have no client grants and are not reachable through the Data API ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-034-credential-and-token-tables-have-no-client-grants-and-are-not-reachable-through-the-data-api)) | BLOCKER | PARTIAL | CONFIG REVIEW, DYNAMIC TEST
  Check: (1) List tables with credential like columns in the exposed schemas: search `supabase/migrations` and `information_schema.columns` for names containing `hash`, `token`, `secret`, `api_key`, `code`, `invite`, `recovery` or `refresh`, and mark each table that holds a credential. (2) For each marked table, check each client role with `select has_table_privilege('<role>', '<schema>.<table>', 'SELECT, INSERT, UPDATE, DELETE')` for `anon` and `authenticated`, or query `information_schema.role_table_grants`. (3) As a signed in user, send `GET`, `POST` (with a credential hash you chose), `PATCH` and `DELETE` for each table through the Data API with the publishable key.
  Evidence: The marked table list, the privilege query output, and the saved Data API requests with responses and the failed authentication attempt.
- [ ] **SEC-DB-035** Content shown to more than one user without author attribution is written only by server code ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-035-content-shown-to-more-than-one-user-without-author-attribution-is-written-only-by-server-code)) | BLOCKER | PARTIAL | CONFIG REVIEW, DYNAMIC TEST, CODE REVIEW
  Check: (1) List every table and column whose content is read by someone other than the writer and is not shown under the writer's name: cached summaries, shared plans and reports, public page content, content used in emails, stored model output. (2) For each, query `pg_policies` for `insert`, `update`, `delete` and `all` policies that name `anon`, `authenticated` or `public`, and check `has_table_privilege` for those roles. (3) Two user test. (4) For content that members author for other readers, confirm the write goes through a server route that validates it, and trace one value from the database to the page and to an email to confirm it is encoded on output.
  Evidence: The list from step 1, the `pg_policies` and privilege output, and the saved negative test results.

### DATA-PROTECTION.md

- [ ] **SEC-DATA-019** Buckets holding user data have no public access path ([DATA-PROTECTION.md](DATA-PROTECTION.md#sec-data-019-buckets-holding-user-data-have-no-public-access-path)) | BLOCKER | PARTIAL | CONFIG REVIEW, DYNAMIC TEST
  Check: (1) Export the bucket list with public flags (Supabase dashboard or API; R2 bucket settings, listing `r2.dev` and every custom domain per bucket). (2) For each bucket holding user files, request a known object URL without a token and confirm 400, 401, 403 or 404.
  Evidence: Bucket configuration export and the failed anonymous request results.
- [ ] **SEC-DATA-020** Object access is limited to the owning user or tenant ([DATA-PROTECTION.md](DATA-PROTECTION.md#sec-data-020-object-access-is-limited-to-the-owning-user-or-tenant)) | BLOCKER | PARTIAL | AUTOMATED TEST, DYNAMIC TEST, CODE REVIEW
  Check: (1) Automated test: user B requests a download URL, upload URL and delete for user A's object, and every request is refused. (2) Automated test per Supabase storage policy for anonymous, owner, second user and second tenant. (3) Review the signing function and confirm the ownership query runs before signing. (4) Client presented keys: run the Verify steps of SEC-DATA-059.
  Evidence: Passing authorization tests and the review note.

### PRIVACY.md

- [ ] **SEC-DATA-024** No endpoint returns personal data to an unauthenticated caller ([PRIVACY.md](PRIVACY.md#sec-data-024-no-endpoint-returns-personal-data-to-an-unauthenticated-caller)) | BLOCKER | PARTIAL | DYNAMIC TEST, CONFIG REVIEW
  Check: (1) With only the publishable key, call every PostgREST table and view, every RPC, every API route and server action, and every storage path. (2) Scan response bodies for email, phone, date of birth, IBAN or bank number, and national ID patterns, and fail on any match. (3) Confirm the Supabase advisor reports zero for lints 0002, 0013 and 0023. (4) For server rendered public pages, read each public route that fetches user data and confirm no personal data field is passed as a prop to a client component, because props passed across the server and client boundary are serialized into the page HTML.
  Evidence: Dynamic test report listing every endpoint called and the result, plus advisor output.
- [ ] **SEC-DATA-040** Deletion and export act only on the caller's own data ([PRIVACY.md](PRIVACY.md#sec-data-040-deletion-and-export-act-only-on-the-callers-own-data)) | BLOCKER | FULL | AUTOMATED TEST, DYNAMIC TEST
  Check: (1) Automated test: user B calls delete, export and correction with user A's identifier in the body, query and path, and every call is refused or acts only on user B. (2) Test the same endpoints with no session and expect 401. (3) Search the route, server action and RPC definitions for account deletion, export and correction handlers.
  Evidence: Passing negative tests.

### SECRETS.md

- [ ] **SEC-SECRETS-001** No secret in client bundles or public environment variables ([SECRETS.md](SECRETS.md#sec-secrets-001-no-secret-in-client-bundles-or-public-environment-variables)) | BLOCKER | FULL | SECRET SCAN, STATIC ANALYSIS
  Check: (1) Build the list of secret formats the project holds from the platform variable list and the secrets inventory (SEC-SECRETS-012). (2) Flag every `NEXT_PUBLIC_` or `EXPO_PUBLIC_` variable whose name contains SECRET, PRIVATE, SERVICE, TOKEN or KEY (other than a known publishable key) and confirm its value is public by design. (3) On the deployed site, review every served JavaScript file and any exposed source map for keys, and test whether each key found is restricted.
  Evidence: Build output scan report with zero secret findings, the public variable review, and the deployed site review, each dated for the release.
- [ ] **SEC-SECRETS-003** Keys that bypass access control stay in trusted server code ([SECRETS.md](SECRETS.md#sec-secrets-003-keys-that-bypass-access-control-stay-in-trusted-server-code)) | BLOCKER | PARTIAL | CODE REVIEW, SECRET SCAN, DYNAMIC TEST
  Check: (1) Grep the codebase for every place the secret or service role key is read and confirm each is server only. (2) Scan API responses, rendered HTML, server component payloads and error bodies in staging (for example with a proxy capture of a full user journey) with the evidence scan of SEC-SECRETS-001, which must first have found a planted value, for key patterns. (3) Confirm no route reads an API key or database credential from request headers or body.
  Evidence: Code review notes listing each use, and the response scan result.
- [ ] **SEC-SECRETS-004** No valid secret in the repository or its history ([SECRETS.md](SECRETS.md#sec-secrets-004-no-valid-secret-in-the-repository-or-its-history)) | BLOCKER | FULL | SECRET SCAN
  Check: (1) Run `gitleaks git` (or `trufflehog git`) over the full history of all branches, with the evidence configuration of SEC-SECRETS-001 and the pull request refs fetched into the clone, and confirm zero findings, or that every finding maps to a key recorded as revoked. (2) Commit a fake key, remove it in the next commit and push the branch; confirm CI fails on the first commit. (3) List tracked files that carry CLI link metadata or project references written by the tools in use (for example the `.vercel` folder) and confirm they are ignored or hold only non secret identifiers.
  Evidence: Full history scan report and the revocation record for any historical finding.

### AI-SECURITY.md

- [ ] **SEC-AI-015** Security decisions enforced in code, never by the model ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-015-security-decisions-enforced-in-code-never-by-the-model)) | BLOCKER | PARTIAL | CODE REVIEW, AUTOMATED TEST
  Check: (1) Code review: for each AI feature, trace every privileged action and data load, including every place server code applies model output as a write, a message or a parameter, and confirm a server side check that does not depend on model output. (2) Automated test: instruct the model (or a mocked model response) to act outside the user's scope and assert the server refuses.
  Evidence: Review notes per feature and the passing refusal test.
- [ ] **SEC-AI-020** Tools run as the end user, never as a service role ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-020-tools-run-as-the-end-user-never-as-a-service-role)) | BLOCKER | PARTIAL | CODE REVIEW, AUTOMATED TEST
  Check: (1) Build the import graph of each tool and MCP handler entry from the bundler metadata and search every reachable module, not only the tool modules, for service role keys, admin clients (including helpers that return one) and owner connection strings. (2) Start the tool server with the service key removed and confirm every tool still works for an ordinary user. (3) Automated test: user A asks the agent for user B's record; assert denial at the tool or database layer, not a model refusal.
  Evidence: Search results showing no privileged credentials in tool code and the passing two user test.
- [ ] **SEC-AI-029** Authorization inside the retrieval query ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-029-authorization-inside-the-retrieval-query)) | BLOCKER | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) Automated test with two tenants: tenant A queries for a phrase unique to tenant B's document; assert zero tenant B chunks returned. (2) Repeat with a client supplied tenant ID set to tenant B; assert zero results. (3) Code review: no post retrieval filter is the only boundary.
  Evidence: Passing two tenant retrieval tests.
- [ ] **SEC-AI-034** Row level security on embedding tables ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-034-row-level-security-on-embedding-tables)) | BLOCKER | FULL | CONFIG REVIEW, AUTOMATED TEST
  Check: (1) Run Supabase advisors and confirm no `0013_rls_disabled_in_public` finding on these tables. (2) Automated test: query the table with the anon key and assert no rows; query with tenant A's JWT and assert no tenant B rows.
  Evidence: Advisor report and passing tests.
- [ ] **SEC-AI-035** Similarity search functions run with the caller's rights ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-035-similarity-search-functions-run-with-the-callers-rights)) | BLOCKER | FULL | STATIC ANALYSIS, CONFIG REVIEW
  Check: (1) Search migrations for `security definer` on functions touching embedding tables. (2) Run Supabase advisors and confirm no 0028 or 0029 findings for these functions.
  Evidence: Search results and advisor report.
- [ ] **SEC-AI-041** Model provider and vector store keys stay on the server ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-041-model-provider-and-vector-store-keys-stay-on-the-server)) | BLOCKER | FULL | SECRET SCAN
  Check: (1) Run Gitleaks on the repository and its history. (2) Scan build output (for example `.next/static` and the Expo export) for provider key patterns. (3) Search environment files for public prefixed AI key names.
  Evidence: Clean secret scan reports for repository and build output.
- [ ] **SEC-AI-043** Model context holds only data the current user may see ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-043-model-context-holds-only-data-the-current-user-may-see)) | BLOCKER | PARTIAL | CODE REVIEW, AUTOMATED TEST
  Check: (1) Code review: context assembly uses the user scoped client. (2) Automated test: user A asks about a record of user B by ID; assert the record is not in the context sent to the model (inspect the mocked provider request).
  Evidence: Passing test.
- [ ] **SEC-AI-045** Conversation history and memory isolated per user and tenant ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-045-conversation-history-and-memory-isolated-per-user-and-tenant)) | BLOCKER | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) Automated test: user A requests user B's conversation ID; assert denial. (2) Test that a new session for user A loads no memory from user B. (3) Read one stored per user AI output (a summary or cached generation) as another user and confirm it is denied.
  Evidence: Passing tests.

### AGENTIC-DEV-SECURITY.md

- [ ] **SEC-AGENT-007** Authenticate every call to a product MCP server ([AGENTIC-DEV-SECURITY.md](AGENTIC-DEV-SECURITY.md#sec-agent-007-authenticate-every-call-to-a-product-mcp-server)) | BLOCKER | PARTIAL | DYNAMIC TEST, AUTOMATED TEST, CODE REVIEW
  Check: (1) Call each tool with no token and expect 401. (2) Call with an expired token, a token for another audience, and a token in the query string, and expect 401 each time. (3) Call with a valid token and confirm success. (4) Keep these cases as automated tests in CI. (5) Present a valid web or mobile session token of the same user to the MCP server and expect 401. (6) Present a valid MCP token at an ordinary API route and expect 401.
  Evidence: Passing automated test run covering the token cases in steps 1 to 3, 5 and 6 for every exposed tool.
- [ ] **SEC-AGENT-008** Authorize each product MCP tool call for the caller ([AGENTIC-DEV-SECURITY.md](AGENTIC-DEV-SECURITY.md#sec-agent-008-authorize-each-product-mcp-tool-call-for-the-caller)) | BLOCKER | PARTIAL | DYNAMIC TEST, AUTOMATED TEST, CODE REVIEW
  Check: (1) With a low privilege token, call every privileged tool and expect denial. (2) With user A's token, call each tool with user B's or tenant B's record IDs and expect denial. (3) Revoke a scope and confirm the next call is denied without reconnecting. (4) Call each write tool with a read scoped token and expect 403.
  Evidence: Passing automated authorization tests for every exposed tool, including cross user and cross tenant cases.
- [ ] **SEC-AGENT-011** No production secrets in coding agent context ([AGENTIC-DEV-SECURITY.md](AGENTIC-DEV-SECURITY.md#sec-agent-011-no-production-secrets-in-coding-agent-context)) | BLOCKER | PARTIAL | SECRET SCAN, CONFIG REVIEW
  Check: (1) Run Gitleaks or TruffleHog over the working directory including untracked files, and over `~/.config`, shell profiles and any `.env*` files, using the Gitleaks `--redact` flag so findings print without the secret; compare found keys against production key prefixes or values from the platform dashboard. (2) Run `env | cut -d= -f1` in the agent's shell to list variable names only, and confirm no production variable name appears; where a name is also in production, compare `shasum` of the two values without printing either. (3) Check Supabase, Vercel, AWS, Stripe and similar CLI logins on the machine and confirm none point at production. (4) Confirm every MCP server token in the inventory targets development resources. (5) Release environment check: compare the project identifiers in local environment files and CLI link metadata with the production identifiers in `docs/security/STAGE.md`, comparing identifiers and fingerprints, never printing key values.
  Evidence: Dated scan report and checklist per developer machine and agent container, signed off by the developer, and an export or screenshot of the connector settings.

### DEPENDENCIES.md

- [ ] **SEC-SUPPLY-016** Pipeline secrets only in the CI secret store ([DEPENDENCIES.md](DEPENDENCIES.md#sec-supply-016-pipeline-secrets-only-in-the-ci-secret-store)) | BLOCKER | FULL | SECRET SCAN, CONFIG REVIEW
  Check: (1) Run Gitleaks over workflow files, build configuration and the full repository history. (2) Read each workflow and confirm every credential comes from the secret store. (3) Review recent pipeline logs for unmasked credential values. (4) Search the workflows for the `pull_request_target` and `workflow_run` events and read every hit: a workflow that checks out or runs pull request or fork code must not have a secret in scope.
  Evidence: Clean Gitleaks report including history, and the workflow review notes.

### INFRASTRUCTURE-SECURITY.md

- [ ] **SEC-CLOUD-016** No secrets in container images ([INFRASTRUCTURE-SECURITY.md](INFRASTRUCTURE-SECURITY.md#sec-cloud-016-no-secrets-in-container-images)) | BLOCKER | FULL | SECRET SCAN, STATIC ANALYSIS
  Check: (1) Run a secret scanner such as Trivy or Gitleaks against the built image. (2) Inspect `docker history --no-trunc` output and the Dockerfile for secret values in `ENV`, `ARG` or `COPY`.
  Evidence: Clean image scan report and the Dockerfile review.

### MOBILE-SECURITY.md

- [ ] **SEC-MOBILE-001** The app bundle contains no secrets ([MOBILE-SECURITY.md](MOBILE-SECURITY.md#sec-mobile-001-the-app-bundle-contains-no-secrets)) | BLOCKER | FULL | SECRET SCAN, CONFIG REVIEW
  Check: (1) Run Gitleaks on the repository, including `.env*`, `app.json`, `app.config.*` and `eas.json`. (2) Build the production bundle with `npx expo export`, then search the output for provider key patterns such as `sk_live`, `sk-ant-` and `sk-`, and run Gitleaks with no git mode over the output folder. (3) Review every `EXPO_PUBLIC_` variable and `extra` field and confirm each is safe to publish.
  Evidence: Gitleaks reports for the repository and the exported bundle with zero findings, and the reviewed list of public variables.

## Part 2: CRITICAL requirements at LAUNCH

Includes requirements that apply at LAUNCH only in the markets named where the law applies. 63 items.

### AUTH.md

- [ ] **SEC-AUTH-001** No custom password storage or token generation ([AUTH.md](AUTH.md#sec-auth-001-no-custom-password-storage-or-token-generation)) | CRITICAL | PARTIAL | STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run Semgrep over the repository for `bcrypt`, `argon2`, `scrypt`, `pbkdf2`, `crypto.createHash`, `createHmac` and `Math.random` inside auth, session, reset and invite code paths. (2) Review each hit and confirm it is either absent from auth logic or covered by a recorded decision. See the requirement for step 3.
  Evidence: Semgrep report with no unexplained hits in auth paths, and the security decisions log entry naming the identity provider.
- [ ] **SEC-AUTH-017** Logout ends the session on the server ([AUTH.md](AUTH.md#sec-auth-017-logout-ends-the-session-on-the-server)) | CRITICAL | PARTIAL | DYNAMIC TEST, CODE REVIEW
  Check: (1) Capture an access token and refresh token, log out, then replay both with curl directly against the API (WSTG-v42-SESS-06 method). (2) Replay the access token on an ordinary endpoint after the recorded lifetime; it must fail. (3) A browser URL reload after logout is not valid evidence.
  Evidence: curl transcripts of the replay, and the configured JWT expiry.
- [ ] **SEC-AUTH-030** Exact redirect URL allowlist in production ([AUTH.md](AUTH.md#sec-auth-030-exact-redirect-url-allowlist-in-production)) | CRITICAL | PARTIAL | CONFIG REVIEW, DYNAMIC TEST
  Check: (1) Export the production Supabase Auth URL configuration and each provider console's redirect list; confirm no `*`, no `**`, no `http://` and no localhost values, that every non HTTPS entry is an exact reverse domain custom scheme URL used under SEC-AUTH-033, and that the Site URL equals the production origin. See the requirement for step 2.
  Evidence: Configuration exports and the tamper test result.
- [ ] **SEC-AUTH-034** External identities map to accounts by issuer and subject ([AUTH.md](AUTH.md#sec-auth-034-external-identities-map-to-accounts-by-issuer-and-subject)) | CRITICAL | PARTIAL | MANUAL TEST, CODE REVIEW
  Check: (1) Create an account with password on email X. (2) Review code that creates or links identities for email based matching, including any user lookup by email next to an OAuth callback. See the requirement for step 3.
  Evidence: Manual test record and code review notes.
- [ ] **SEC-AUTHZ-004** Writable field allowlist, no privilege fields from the client ([AUTH.md](AUTH.md#sec-authz-004-writable-field-allowlist-no-privilege-fields-from-the-client)) | CRITICAL | PARTIAL | STATIC ANALYSIS, AUTOMATED TEST, CODE REVIEW
  Check: (1) Run a Semgrep rule that flags request bodies or spread objects passed directly into insert, update or upsert calls. See the requirement for steps 2 to 3.
  Evidence: Semgrep report with no direct body writes, and passing tests showing privilege fields cannot be set by the client.
- [ ] **SEC-AUTHZ-005** Authorization attributes come only from server controlled data ([AUTH.md](AUTH.md#sec-authz-005-authorization-attributes-come-only-from-server-controlled-data)) | CRITICAL | PARTIAL | CONFIG REVIEW, STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run Supabase advisors (security) and confirm lint 0015_rls_references_user_metadata reports nothing. (2) Search code and SQL for `user_metadata`, `raw_user_meta_data` and `auth.jwt() -> 'user_metadata'` and confirm none feed an authorization decision. See the requirement for steps 3 to 4.
  Evidence: Advisor export with no 0015 findings, search results reviewed, and the passing self elevation test.
- [ ] **SEC-AUTHZ-006** Authorization errors result in denial ([AUTH.md](AUTH.md#sec-authz-006-authorization-errors-result-in-denial)) | CRITICAL | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) In tests, mock the roles or membership lookup to throw and to return null, then call a protected function; it MUST return an error status and change nothing. (2) Review `catch` blocks around authorization calls and confirm none continue to the protected operation.
  Evidence: Passing failure injection tests for the authorization helper, and code review notes for its call sites.
- [ ] **SEC-AUTHZ-007** Privileged clients never act for a user without that user's permissions ([AUTH.md](AUTH.md#sec-authz-007-privileged-clients-never-act-for-a-user-without-that-users-permissions)) | CRITICAL | PARTIAL | STATIC ANALYSIS, CODE REVIEW, AUTOMATED TEST
  Check: (1) Search for every use of the service role or secret key (`SUPABASE_SERVICE_ROLE_KEY`, `sb_secret_`, admin client factories) and list the handlers that import it. (2) For each listed handler reachable by a normal user, confirm an explicit ownership and tenant check precedes each privileged query. See the requirement for step 3.
  Evidence: The list of privileged client call sites with the check reviewed for each, and passing two user tests.
- [ ] **SEC-AUTHZ-012** Server side caches keyed by user and tenant ([AUTH.md](AUTH.md#sec-authz-012-server-side-caches-keyed-by-user-and-tenant)) | CRITICAL | PARTIAL | CODE REVIEW, AUTOMATED TEST
  Check: (1) Search for cache APIs (`unstable_cache`, `use cache`, `cache(`, Redis `get` and `set`, module level `let` or `const` holding query results) and confirm each private data entry key contains the user ID, and each tenant keyed entry holds only data every member may read. See the requirement for step 2.
  Evidence: Code review list of cache call sites with keys, and the passing two user cache test.
- [ ] **SEC-AUTHZ-015** Active tenant resolved on the server from verified membership ([AUTH.md](AUTH.md#sec-authz-015-active-tenant-resolved-on-the-server-from-verified-membership)) | CRITICAL | PARTIAL | STATIC ANALYSIS, AUTOMATED TEST, CODE REVIEW
  Check: (1) Run a Semgrep rule that flags `tenant_id`, `org_id` or `organization_id` read from `params`, `searchParams`, request bodies or headers without passing through the resolver. (2) Send requests with a foreign tenant ID in the body, query and header; expect 403 or the caller's own tenant data only.
  Evidence: Semgrep report, and passing foreign tenant ID tests.
- [ ] **SEC-AUTHZ-021** MFA required for in product admin accounts ([AUTH.md](AUTH.md#sec-authz-021-mfa-required-for-in-product-admin-accounts)) | CRITICAL | PARTIAL | AUTOMATED TEST, CONFIG REVIEW
  Check: (1) Sign in as an admin with password only and call an admin function; expect denial. (2) Complete MFA and repeat; expect success. (3) Export the list of admin and support accounts and confirm each has an enrolled second factor. See the requirement for step 4.
  Evidence: Passing MFA gate tests, and the account export.
- [ ] **SEC-AUTHZ-031** Support tools never hold an all tenant RLS bypass key ([AUTH.md](AUTH.md#sec-authz-031-support-tools-never-hold-an-all-tenant-rls-bypass-key)) | CRITICAL | PARTIAL | CODE REVIEW, STATIC ANALYSIS
  Check: (1) Search the support tool code for the service role or secret key and for admin clients; each use MUST be inside a guarded server function with a tenant filter. (2) As a support user scoped to tenant X, attempt a query that would return tenant Y data; expect denial or no rows.
  Evidence: Code search results and the passing cross tenant support test.

### API-SECURITY.md

- [ ] **SEC-API-114** Fail closed when the limiter is unavailable on paid routes ([API-SECURITY.md](API-SECURITY.md#sec-api-114-fail-closed-when-the-limiter-is-unavailable-on-paid-routes)) | CRITICAL | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) For each paid route, including every AI model route, mock the limiter to time out and then to throw, and call the route. (2) Review each paid route for the timeout check and for any error path that continues to the paid call. (3) Repeat step 1 for the login, signup, password reset and OTP limiters.
  Evidence: Passing fail closed test per paid route.
- [ ] **SEC-API-127** Match provider payment details to the order before granting ([API-SECURITY.md](API-SECURITY.md#sec-api-127-match-provider-payment-details-to-the-order-before-granting)) | CRITICAL | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) In tests, deliver verified events with a lower amount, a different currency, a pending state and a different product ID. None must grant. (2) Deliver a verified event whose state is completed and whose amount, currency and reference match the order. It must grant exactly once. See the requirement for step 3.
  Evidence: Passing mismatch tests.
- [ ] **SEC-API-128** Grant each payment at most once, in one transaction ([API-SECURITY.md](API-SECURITY.md#sec-api-128-grant-each-payment-at-most-once-in-one-transaction)) | CRITICAL | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) Deliver the same verified payment twice, and concurrently through the webhook and the verify path. Exactly one grant must result. (2) Reuse a Google `purchaseToken` in a test. It must be refused.
  Evidence: Passing duplicate and race tests; migration showing the unique index.
- [ ] **SEC-API-135** Never grant production entitlements from sandbox events ([API-SECURITY.md](API-SECURITY.md#sec-api-135-never-grant-production-entitlements-from-sandbox-events)) | CRITICAL | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) Deliver a verified sandbox event to the production handler. No production entitlement must be granted. (2) Grep the entitlement code for the environment check (for example the RevenueCat `environment` field or Stripe `livemode`) and confirm it runs before every grant path.
  Evidence: Passing test.
- [ ] **SEC-API-137** Collect card data only through the provider's hosted checkout ([API-SECURITY.md](API-SECURITY.md#sec-api-137-collect-card-data-only-through-the-providers-hosted-checkout)) | CRITICAL | PARTIAL | CODE REVIEW, STATIC ANALYSIS
  Check: (1) Search the code for form fields named like card number, CVC or expiry, and for request schemas containing them. (2) Review the checkout flow and confirm card entry happens on a provider domain or provider iframe.
  Evidence: Code search output; checkout flow review note.

### BACKEND-SECURITY.md

- [ ] **SEC-API-018** Map query structure input through a fixed allowlist ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-018-map-query-structure-input-through-a-fixed-allowlist)) | CRITICAL | PARTIAL | CODE REVIEW, AUTOMATED TEST
  Check: (1) Find every query whose table, column, order or operator comes from request data. (2) Confirm each passes through an allowlist map. See the requirement for step 3.
  Evidence: Code review notes listing each dynamic identifier and its allowlist; test output.
- [ ] **SEC-API-019** Keep dynamic SQL out of client callable database functions ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-019-keep-dynamic-sql-out-of-client-callable-database-functions)) | CRITICAL | PARTIAL | CODE REVIEW, STATIC ANALYSIS
  Check: (1) List every function in exposed schemas and grep their bodies for `EXECUTE`, `format(` and string concatenation. (2) Review each hit for arguments reaching query text. (3) Call each such RPC with injection payloads in every argument in a non production database.
  Evidence: Function list with review notes; test output.
- [ ] **SEC-API-027** Authorize at the point of data access, never only in Proxy ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-027-authorize-at-the-point-of-data-access-never-only-in-proxy)) | CRITICAL | PARTIAL | CODE REVIEW, STATIC ANALYSIS, DYNAMIC TEST
  Check: (1) List every route protected in Proxy and confirm the matching handlers or data functions repeat the check. (2) Call each protected Server Action and Route Handler directly with a session that Proxy would redirect; expect denial. (3) Search for database client imports outside the Data Access Layer.
  Evidence: Review notes mapping Proxy rules to handler checks; direct call test output.
- [ ] **SEC-API-034** Restrict fixed outbound calls to an allowlist of hosts ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-034-restrict-fixed-outbound-calls-to-an-allowlist-of-hosts)) | CRITICAL | PARTIAL | STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run Semgrep for `fetch`, `axios` and `got` calls whose URL includes request data. (2) Confirm each outbound call goes through the shared client with the host allowlist. (3) Try to change the host through every user controlled field; expect rejection. See the requirement for step 4.
  Evidence: Semgrep report; allowlist configuration.
- [ ] **SEC-API-035** Guard user and model supplied URLs before connecting ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-035-guard-user-and-model-supplied-urls-before-connecting)) | CRITICAL | PARTIAL | AUTOMATED TEST, DYNAMIC TEST, STATIC ANALYSIS
  Check: (1) Unit test the guard with `http://169.254.169.254/`, `http://localhost`, `http://127.1`, `http://2130706433`, `http://[::1]`, `http://[::ffff:127.0.0.1]`, `file:///etc/passwd` and `gopher://` URLs; all must be rejected. (2) Test a hostname that resolves to a private address; it must be rejected. See the requirement for steps 3 to 7.
  Evidence: Guard unit test output; dynamic test output per feature; the worker, resolver stub and redirect test output; the call site list.
- [ ] **SEC-API-045** Never serve uploads as active content from the app origin ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-045-never-serve-uploads-as-active-content-from-the-app-origin)) | CRITICAL | PARTIAL | DYNAMIC TEST, CONFIG REVIEW
  Check: (1) Upload an HTML file (where allowed, or by bypassing the client) and open its download URL. (2) It must download or render from a different origin, never execute in the app origin. See the requirement for step 3.
  Evidence: Test output; file serving configuration.
- [ ] **SEC-API-056** Keep queues off the Data API unless each exposed queue is locked down ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-056-keep-queues-off-the-data-api-unless-each-exposed-queue-is-locked-down)) | CRITICAL | PARTIAL | CONFIG REVIEW, DYNAMIC TEST
  Check: (1) Open Integrations, Queues, Settings in the Supabase Dashboard and record whether "Expose Queues via PostgREST" is on, and whether `pgmq_public` is in the exposed schemas list. See the requirement for steps 2 to 4.
  Evidence: Queues settings screenshot or export; query output for RLS and grants; failed anonymous call output.
- [ ] **SEC-API-057** Keep job platform request verification on in deployed environments ([BACKEND-SECURITY.md](BACKEND-SECURITY.md#sec-api-057-keep-job-platform-request-verification-on-in-deployed-environments)) | CRITICAL | PARTIAL | CONFIG REVIEW, DYNAMIC TEST, STATIC ANALYSIS
  Check: (1) Export environment variable names for every deployed environment (Vercel production and preview, Render) and confirm each job platform's signing key or `CRON_SECRET` is set and `INNGEST_DEV` is absent. See the requirement for steps 2 to 4.
  Evidence: Environment variable name exports; grep output; rejected request test output per endpoint.

### FRONTEND-SECURITY.md

- [ ] **SEC-WEB-022** Choose CORS origins from an exact allowlist ([FRONTEND-SECURITY.md](FRONTEND-SECURITY.md#sec-web-022-choose-cors-origins-from-an-exact-allowlist)) | CRITICAL | PARTIAL | DYNAMIC TEST, STATIC ANALYSIS, CONFIG REVIEW
  Check: (1) For every API route, `curl -sI -H 'Origin: https://evil.example'`, `-H 'Origin: null'`, a suffix lookalike and a prefix lookalike of the real origin, and a host under each shared hosting domain the project uses (for example a name registered on the preview platform); fail if the origin is echoed or `*` is returned on a private route. See the requirement for steps 2 to 3.
  Evidence: Saved probe output for each route; Semgrep report; the allowlist configuration per environment.
- [ ] **SEC-WEB-026** Protect cookie authenticated state changes against forgery ([FRONTEND-SECURITY.md](FRONTEND-SECURITY.md#sec-web-026-protect-cookie-authenticated-state-changes-against-forgery)) | CRITICAL | PARTIAL | DYNAMIC TEST, CODE REVIEW
  Check: (1) List every state changing route handler and exported Server Action from the framework route table (not from memory). (2) Send each request with `Content-Type: text/plain` and no custom header; it must be rejected. See the requirement for step 3.
  Evidence: Cross origin test record or automated test results.
- [ ] **SEC-WEB-031** List and justify every raw HTML sink ([FRONTEND-SECURITY.md](FRONTEND-SECURITY.md#sec-web-031-list-and-justify-every-raw-html-sink)) | CRITICAL | PARTIAL | STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run Semgrep for the sinks named in the Requirement and for `eval` and `new Function` in client code; compare results to the inventory. (2) For each listed sink, trace the data source and confirm it is constant or sanitized.
  Evidence: Semgrep report matching the inventory; CI rule configuration.
- [ ] **SEC-WEB-032** Sanitize user supplied HTML with a maintained library ([FRONTEND-SECURITY.md](FRONTEND-SECURITY.md#sec-web-032-sanitize-user-supplied-html-with-a-maintained-library)) | CRITICAL | PARTIAL | AUTOMATED TEST, CODE REVIEW, DEPENDENCY SCAN
  Check: (1) Store payloads such as `<img src=x onerror=alert(1)>`, `<a href="javascript:alert(1)">x</a>` and `<svg><script>alert(1)</script></svg>` through every rich text input, render them in Playwright, and assert no script runs. (2) Run a dependency scan and confirm the sanitizer has no open advisory.
  Evidence: Passing payload tests; dependency scan report.

### DATABASE-SECURITY.md

- [ ] **SEC-DB-002** One explicit policy per allowed operation, scoped to a role ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-002-one-explicit-policy-per-allowed-operation-scoped-to-a-role)) | CRITICAL | PARTIAL | CODE REVIEW, CONFIG REVIEW, DYNAMIC TEST
  Check: (1) Run the security advisor and confirm zero findings for lint `0024_permissive_rls_policy`. See the requirement for steps 2 to 3.
  Evidence: `pg_policies` export reviewed and signed off in the PR (or the decisions log entry or commit trailer under the Solo builder path in STANDARD.md), advisor export, and the cross user test results.
- [ ] **SEC-DB-003** New tables and functions are not exposed by default privileges ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-003-new-tables-and-functions-are-not-exposed-by-default-privileges)) | CRITICAL | FULL | CONFIG REVIEW, STATIC ANALYSIS
  Check: (1) Query `pg_default_acl` for each exposed schema and confirm no entry grants privileges to `anon` or `authenticated`. (2) In a branch or local database, create a test table without grants and confirm `GET /rest/v1/<table>` with the publishable key returns a permission error. See the requirement for step 3.
  Evidence: `pg_default_acl` output and the test result from step 2, stored with the release record.
- [ ] **SEC-DB-006** RLS policies never trust user editable claims ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-006-rls-policies-never-trust-user-editable-claims)) | CRITICAL | FULL | CONFIG REVIEW, STATIC ANALYSIS
  Check: (1) Run the security advisor and confirm zero findings for lint `0015_rls_references_user_metadata`. (2) Grep migrations and `pg_policies` for `user_metadata` and `raw_user_meta_data`. See the requirement for step 3.
  Evidence: Advisor export, grep output, and the step 3 test result.
- [ ] **SEC-DB-007** Exposed views run with the caller's permissions ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-007-exposed-views-run-with-the-callers-permissions)) | CRITICAL | FULL | CONFIG REVIEW
  Check: (1) Run the security advisor and confirm zero findings for lints `0010_security_definer_view` and `0002_auth_users_exposed`. (2) Query `pg_class` for views in exposed schemas whose `reloptions` lack `security_invoker=true`.
  Evidence: Advisor export and query output.
- [ ] **SEC-DB-008** Security definer functions are not callable by clients ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-008-security-definer-functions-are-not-callable-by-clients)) | CRITICAL | FULL | CONFIG REVIEW, STATIC ANALYSIS
  Check: (1) Run the security advisor and confirm zero findings for lints `0028` and `0029` (security definer function executable by `anon` or `authenticated`). See the requirement for steps 2 to 4.
  Evidence: Advisor export, query output, and the RPC call results.
- [ ] **SEC-DB-016** No reset style rollback against remote databases or real data ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-016-no-reset-style-rollback-against-remote-databases-or-real-data)) | CRITICAL | MANUAL | DOCUMENT REVIEW, CODE REVIEW
  Check: (1) Search scripts, CI workflows, package scripts and agent configuration at every scope (project, local, user and parent folder) for `migration down`, `db reset`, `--linked` and `--db-url` and confirm none target a remote, linked or real data database other than a recorded disposable project. See the requirement for steps 2 to 3.
  Evidence: Search results, the runbook section, and the undo route record for each destructive migration (PR description, or the decisions log entry or commit trailer under the Solo builder path in STANDARD.md).
- [ ] **SEC-DB-017** Automated production database backups ([DATABASE-SECURITY.md](DATABASE-SECURITY.md#sec-db-017-automated-production-database-backups)) | CRITICAL | PARTIAL | CONFIG REVIEW, DOCUMENT REVIEW
  Check: (1) Check the provider backup page or the scheduled job history and confirm a successful backup in the last 24 hours. (2) Confirm the schedule is documented and the retention is at least 7 days for every backup location. See the requirement for step 3.
  Evidence: Backup listing or job history, the documented schedule and retention, and the restore record.

### DATA-PROTECTION.md

- [ ] **SEC-DATA-001** Unguessable values come from a CSPRNG ([DATA-PROTECTION.md](DATA-PROTECTION.md#sec-data-001-unguessable-values-come-from-a-csprng)) | CRITICAL | PARTIAL | STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run a Semgrep rule that flags `Math.random`, `Date.now` or counters used inside functions or variables named like token, code, secret, invite, reset, share or id. See the requirement for steps 2 to 3.
  Evidence: Semgrep report with zero findings for the rule, and the review note listing each generator with its source and length.
- [ ] **SEC-DATA-005** Passwords stored under an SEC-AUTH-001 exception use an approved slow hash ([DATA-PROTECTION.md](DATA-PROTECTION.md#sec-data-005-passwords-stored-under-an-sec-auth-001-exception-use-an-approved-slow-hash)) | CRITICAL | PARTIAL | CODE REVIEW, DOCUMENT REVIEW
  Check: (1) Check the security decisions log for a recorded SEC-AUTH-001 exception. (2) Search for password write paths (`hash(`, `bcrypt`, `argon2`, `pbkdf2`, `scrypt`, `createHash` near `password`) and confirm the function and parameters against the Appendix C table. See the requirement for step 3.
  Evidence: The recorded SEC-AUTH-001 exception and a code review note with the function and parameters.
- [ ] **SEC-DATA-011** External endpoints use TLS 1.2 or 1.3 with trusted certificates ([DATA-PROTECTION.md](DATA-PROTECTION.md#sec-data-011-external-endpoints-use-tls-12-or-13-with-trusted-certificates)) | CRITICAL | FULL | DYNAMIC TEST, CONFIG REVIEW
  Check: (1) Run testssl.sh or SSL Labs against every public hostname, including API, app, marketing, storage custom domains and webhook receivers. (2) Fail if TLS 1.0, TLS 1.1 or SSL is offered, or the certificate is untrusted, expired or mismatched.
  Evidence: Scan output per hostname, dated within the release cycle.
- [ ] **SEC-DATA-059** Storage keys presented by the client resolve to a record issued to the caller's tenant ([DATA-PROTECTION.md](DATA-PROTECTION.md#sec-data-059-storage-keys-presented-by-the-client-resolve-to-a-record-issued-to-the-callers-tenant)) | CRITICAL | PARTIAL | AUTOMATED TEST, CODE REVIEW
  Check: (1) List every route that takes a key, path, file id or URL from the request body, query or path (search for `key`, `path`, `objectKey`, `fileId`, `storagePath`) and open each handler. (2) Two tenant test. See the requirement for step 3.
  Evidence: The route list with the lookup location per route, the saved two tenant and replay test results, and the object check after the delete attempt.

### PRIVACY.md

- [ ] **SEC-GOV-051** No AI feature performs an EU prohibited AI practice ([PRIVACY.md](PRIVACY.md#sec-gov-051-no-ai-feature-performs-an-eu-prohibited-ai-practice)) | CRITICAL | MANUAL | DOCUMENT REVIEW, CODE REVIEW
  Stage: LAUNCH where the law applies (EU); GROWTH otherwise
  Market stage: NG GROWTH, EU LAUNCH, other markets GROWTH
  Check: (1) Open the threat model entry of every AI feature reaching EU users and confirm the Article 5(1) screen is complete, dated and signed by the owner. See the requirement for step 2.
  Evidence: Completed screen per feature; search output with dispositions.

### SECRETS.md

- [ ] **SEC-SECRETS-010** Leaked secrets are revoked and rotated first ([SECRETS.md](SECRETS.md#sec-secrets-010-leaked-secrets-are-revoked-and-rotated-first)) | CRITICAL | MANUAL | DOCUMENT REVIEW, MANUAL TEST
  Check: (1) Read the procedure and confirm each production secret has a revoke, reissue and redeploy entry and a log check step. (2) Run one real rotation of the payment or service role key on staging copies, time it, confirm the old value is refused by the provider, and record the result. See the requirement for step 3.
  Evidence: The dated procedure and the rotation drill record.

### AI-SECURITY.md

- [ ] **SEC-AI-002** Per user AI usage budget enforced in the app ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-002-per-user-ai-usage-budget-enforced-in-the-app)) | CRITICAL | PARTIAL | DYNAMIC TEST, CODE REVIEW
  Check: (1) Write a test that sets a small budget for a test user, sends requests until it is exceeded, and asserts the next request is refused without a model call (mock the provider and assert zero calls). (2) Run a scripted burst against staging as one user and confirm refusal at the configured budget. See the requirement for step 3.
  Evidence: The passing budget test and a list of model call sites showing the budget check on each.
- [ ] **SEC-AI-006** No customer data sent to free or unpaid model tiers ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-006-no-customer-data-sent-to-free-or-unpaid-model-tiers)) | CRITICAL | MANUAL | CONFIG REVIEW, DOCUMENT REVIEW
  Check: (1) For each provider project used in production, confirm a paid plan or billing account is attached; for Google Cloud run `gcloud billing projects describe PROJECT_ID` and confirm `billingEnabled: true`. (2) Confirm the provider terms for that plan state no training on API data. See the requirement for step 3.
  Evidence: Provider billing configuration export and the data terms reviewed, recorded with the date.
- [ ] **SEC-AI-017** No unconfirmed outbound action in features that read untrusted input and sensitive data ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-017-no-unconfirmed-outbound-action-in-features-that-read-untrusted-input-and-sensitive-data)) | CRITICAL | MANUAL | DOCUMENT REVIEW, CODE REVIEW
  Check: (1) For each feature, read its classification against the definitions in the Requirement (do not accept the team's own definitions) and confirm outbound and state changing actions need confirmation where all three are present. See the requirement for step 2.
  Evidence: Written classification, risk acceptance record and the test result.
- [ ] **SEC-AI-021** Authorization checked at every tool call ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-021-authorization-checked-at-every-tool-call)) | CRITICAL | PARTIAL | CODE REVIEW, AUTOMATED TEST
  Check: (1) Code review: each tool handler contains its own authorization check. (2) Automated test: start a run with valid access, revoke access mid run, and assert the next tool call is denied.
  Evidence: Review notes per tool and the passing revocation test.
- [ ] **SEC-AI-031** User contributed content kept out of shared retrieval sets until reviewed ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-031-user-contributed-content-kept-out-of-shared-retrieval-sets-until-reviewed)) | CRITICAL | MANUAL | CODE REVIEW, DOCUMENT REVIEW
  Check: (1) Trace every ingestion path into shared sets (user upload, email, crawl, feed, repository, ticket) and confirm each has an injection screen and a provenance check, or a recorded human review. See the requirement for step 2.
  Evidence: Ingestion path review and promotion logs.
- [ ] **SEC-AI-040** Model generated code runs only in an isolated sandbox ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-040-model-generated-code-runs-only-in-an-isolated-sandbox)) | CRITICAL | MANUAL | CONFIG REVIEW, DYNAMIC TEST
  Check: (1) From inside the sandbox, attempt to read environment variables, reach an external host and reach the app's internal endpoints; all must fail. (2) Run an infinite loop and confirm the time limit stops it. See the requirement for step 3.
  Evidence: Sandbox configuration and test record.
- [ ] **SEC-AI-042** No secrets in hidden context ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-042-no-secrets-in-hidden-context)) | CRITICAL | PARTIAL | CODE REVIEW, SECRET SCAN, MANUAL TEST
  Check: (1) Secret scan prompt and tool definition files, for example `gitleaks detect --no-git --source <prompt and tool definition paths>`. See the requirement for step 2.
  Evidence: Scan report and extraction test notes.
- [ ] **SEC-AI-060** Generation features block non consensual intimate imagery and child abuse material ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-060-generation-features-block-non-consensual-intimate-imagery-and-child-abuse-material)) | CRITICAL | PARTIAL | AUTOMATED TEST, CONFIG REVIEW
  Check: (1) Run an adversarial prompt set in staging (sexual prompts naming public figures, sexual edits of an uploaded test photo of a consenting staff member, prompts implying minors) and confirm every request is refused or every output blocked. See the requirement for steps 2 to 3.
  Evidence: Adversarial prompt set and results with date; safety setting screenshots or config; report path test.
- [ ] **SEC-AI-061** Agent driven browsers isolated from real sessions and limited to allowed domains ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-061-agent-driven-browsers-isolated-from-real-sessions-and-limited-to-allowed-domains)) | CRITICAL | PARTIAL | DYNAMIC TEST, CONFIG REVIEW
  Check: (1) Automated test `browser_agent_clean_context`: at the start of a run, call `context.cookies()` and read `localStorage` on a first party page; pass if both are empty. See the requirement for steps 2 to 4.
  Evidence: Browser launch configuration, the allowlist and egress rules, and the passing test output.
- [ ] **SEC-AI-062** Model written SQL runs as a read only role under row level security ([AI-SECURITY.md](AI-SECURITY.md#sec-ai-062-model-written-sql-runs-as-a-read-only-role-under-row-level-security)) | CRITICAL | PARTIAL | AUTOMATED TEST, CONFIG REVIEW
  Check: (1) Automated test `ai_sql_rejects_writes`: send the executor `DELETE FROM invoices`, `DROP TABLE invoices`, `SET TRANSACTION READ WRITE; UPDATE invoices SET total = 0`, `SELECT 1; DELETE FROM invoices`, `CREATE TABLE x ()` and `SELECT set_config('request.jwt.claims', '{"sub":"<tenant B user id>"}', true)`; pass if every one is rejected and the invoices row count and schema are unchanged. See the requirement for steps 2 to 5.
  Evidence: The role migration, the executor code, the query output and the passing tests.

### AGENTIC-DEV-SECURITY.md

- [ ] **SEC-AGENT-009** No token passthrough from a product MCP server ([AGENTIC-DEV-SECURITY.md](AGENTIC-DEV-SECURITY.md#sec-agent-009-no-token-passthrough-from-a-product-mcp-server)) | CRITICAL | PARTIAL | CODE REVIEW, DYNAMIC TEST
  Check: (1) Search the server code for outbound requests that reuse the incoming Authorization header or token variable. (2) Capture outbound traffic in a test environment and confirm the token sent upstream differs from the token the client presented.
  Evidence: Code review record and a captured test showing distinct upstream credentials.
- [ ] **SEC-AGENT-014** No direct agent path to production ([AGENTIC-DEV-SECURITY.md](AGENTIC-DEV-SECURITY.md#sec-agent-014-no-direct-agent-path-to-production)) | CRITICAL | PARTIAL | CONFIG REVIEW
  Check: (1) Export the production branch ruleset and confirm pull request required, no force push, and no agent identity on the bypass list. (2) Using the agent's token, attempt a direct push to the production branch in a test and confirm it is rejected. See the requirement for steps 3 to 5.
  Evidence: Ruleset export, rejected push output, app permission screenshot, and the provider audit log check.

### DEPENDENCIES.md

- [ ] **SEC-SUPPLY-002** Dependency vulnerability gate in CI ([DEPENDENCIES.md](DEPENDENCIES.md#sec-supply-002-dependency-vulnerability-gate-in-ci)) | CRITICAL | FULL | DEPENDENCY SCAN, CONFIG REVIEW
  Check: (1) Confirm the scan step runs on every pull request to the production branch and is a required status check (see SEC-SUPPLY-015). See the requirement for steps 2 to 4.
  Evidence: CI workflow showing the scan step, a passing scan report for the current release, the failing run from step 2, and the exception records for any ignored findings.
- [ ] **SEC-SUPPLY-026** No source control metadata on deployed sites ([DEPENDENCIES.md](DEPENDENCIES.md#sec-supply-026-no-source-control-metadata-on-deployed-sites)) | CRITICAL | FULL | DYNAMIC TEST
  Check: (1) Request `https://<host>/.git/HEAD` and `https://<host>/.git/config` on every production and preview host; expect 403 or 404. (2) Run `find <build output> -name .git` on the deployed build output (for example the Vercel build output or static export folder); expect no results.
  Evidence: Response codes for each host.
- [ ] **SEC-SUPPLY-032** No untrusted event data expanded into workflow scripts ([DEPENDENCIES.md](DEPENDENCIES.md#sec-supply-032-no-untrusted-event-data-expanded-into-workflow-scripts)) | CRITICAL | FULL | STATIC ANALYSIS
  Check: (1) Run `zizmor .github/workflows/ .github/actions/` and confirm no open `template-injection` or `github-env` findings. (2) Run `actionlint` and confirm no `[expression]` errors that mention a potentially untrusted input. See the requirement for step 3.
  Evidence: zizmor and actionlint output and the reviewed grep result.

### INFRASTRUCTURE-SECURITY.md

- [ ] **SEC-CLOUD-012** MFA on every privileged platform account ([INFRASTRUCTURE-SECURITY.md](INFRASTRUCTURE-SECURITY.md#sec-cloud-012-mfa-on-every-privileged-platform-account)) | CRITICAL | PARTIAL | CONFIG REVIEW
  Check: (1) For each platform, read the enforcement setting or list every member with their capabilities (read production keys, deploy, change data, DNS or billing) and their MFA status, including members whose role is named developer, contractor or similar. See the requirement for step 2.
  Evidence: Per platform export or screenshot of MFA status and enforcement settings, dated.

### OBSERVABILITY.md

- [ ] **SEC-LOG-001** No credentials or payment data in logs ([OBSERVABILITY.md](OBSERVABILITY.md#sec-log-001-no-credentials-or-payment-data-in-logs)) | CRITICAL | PARTIAL | SECRET SCAN, STATIC ANALYSIS, CONFIG REVIEW
  Check: (1) In staging, exercise sign in, password reset, payment, webhook and API key flows, then export the platform logs and a sample of error tracker events. (2) Run Gitleaks or TruffleHog over the export. Expect zero findings. See the requirement for steps 3 to 4.
  Evidence: Secret scan report over exported logs with zero findings, Semgrep run output, logger configuration file, and an export or screenshot of the error tracker scrubbing settings.
- [ ] **SEC-LOG-003** Authentication and authorization events are logged ([OBSERVABILITY.md](OBSERVABILITY.md#sec-log-003-authentication-and-authorization-events-are-logged)) | CRITICAL | PARTIAL | AUTOMATED TEST, CONFIG REVIEW
  Check: (1) Write an automated test against staging that performs a failed sign in, a successful sign in, a password reset request and a request for another user's object, then queries the log store. (2) Assert that one record exists per action with actor or anonymous marker, event type, outcome and time. See the requirement for steps 3 to 4.
  Evidence: Passing test run with its test file, and the provider log configuration export.
- [ ] **SEC-LOG-019** Authentication, validation and signature checks fail closed ([OBSERVABILITY.md](OBSERVABILITY.md#sec-log-019-authentication-validation-and-signature-checks-fail-closed)) | CRITICAL | PARTIAL | AUTOMATED TEST, STATIC ANALYSIS
  Check: (1) Write automated tests that force the auth client, the input validator and the signature verifier to throw, then assert each protected route returns a denial and performs no write. (2) Run Semgrep rules for empty catch blocks and catch blocks that continue after auth, validation or verification calls.
  Evidence: Passing test run with its test file, and Semgrep output.

### INCIDENT-RESPONSE.md

- [ ] **SEC-LOG-024** A breach runbook meets each served market's deadline ([INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md#sec-log-024-a-breach-runbook-meets-each-served-markets-deadline)) | CRITICAL | MANUAL | DOCUMENT REVIEW, MANUAL TEST
  Check: (1) Review the runbook for each served market's deadlines, recipients and template content. See the requirement for steps 2 to 3.
  Evidence: The runbook, templates and the tabletop timing record.

### MOBILE-SECURITY.md

- [ ] **SEC-MOBILE-002** Tokens are stored only in keystore backed storage ([MOBILE-SECURITY.md](MOBILE-SECURITY.md#sec-mobile-002-tokens-are-stored-only-in-keystore-backed-storage)) | CRITICAL | PARTIAL | STATIC ANALYSIS, CODE REVIEW
  Check: (1) Run Semgrep rules that flag AsyncStorage, MMKV without an encryption key, SQLite or file writes receiving token or session values that were not first encrypted with a SecureStore held key, and a Supabase client created without a SecureStore based `auth.storage` adapter. See the requirement for steps 2 to 3.
  Evidence: Semgrep output, the adapter source, and the device inspection record.

## Beyond this list

This list holds every BLOCKER and every CRITICAL requirement. Hullproof Pro adds the HIGH, MEDIUM and LOW requirements, which are covered by a full audit report.

## Results

| ID | Result | Severity | Owning doc | Root cause or finding id | Evidence class | Reused or rechecked | Evidence link | Notes |
|----|--------|----------|------------|--------------------------|----------------|---------------------|---------------|-------|
| SEC-AUTH-002 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTH-008 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTH-010 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTHZ-002 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTHZ-003 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTHZ-010 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTHZ-013 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTHZ-014 | | BLOCKER | AUTH.md | | | | | |
| SEC-AUTHZ-020 | | BLOCKER | AUTH.md | | | | | |
| SEC-API-001 | | BLOCKER | API-SECURITY.md | | | | | |
| SEC-API-101 | | BLOCKER | API-SECURITY.md | | | | | |
| SEC-API-125 | | BLOCKER | API-SECURITY.md | | | | | |
| SEC-API-126 | | BLOCKER | API-SECURITY.md | | | | | |
| SEC-API-132 | | BLOCKER | API-SECURITY.md | | | | | |
| SEC-API-133 | | BLOCKER | API-SECURITY.md | | | | | |
| SEC-API-017 | | BLOCKER | BACKEND-SECURITY.md | | | | | |
| SEC-API-020 | | BLOCKER | BACKEND-SECURITY.md | | | | | |
| SEC-API-021 | | BLOCKER | BACKEND-SECURITY.md | | | | | |
| SEC-DB-001 | | BLOCKER | DATABASE-SECURITY.md | | | | | |
| SEC-DB-033 | | BLOCKER | DATABASE-SECURITY.md | | | | | |
| SEC-DB-034 | | BLOCKER | DATABASE-SECURITY.md | | | | | |
| SEC-DB-035 | | BLOCKER | DATABASE-SECURITY.md | | | | | |
| SEC-DATA-019 | | BLOCKER | DATA-PROTECTION.md | | | | | |
| SEC-DATA-020 | | BLOCKER | DATA-PROTECTION.md | | | | | |
| SEC-DATA-024 | | BLOCKER | PRIVACY.md | | | | | |
| SEC-DATA-040 | | BLOCKER | PRIVACY.md | | | | | |
| SEC-SECRETS-001 | | BLOCKER | SECRETS.md | | | | | |
| SEC-SECRETS-003 | | BLOCKER | SECRETS.md | | | | | |
| SEC-SECRETS-004 | | BLOCKER | SECRETS.md | | | | | |
| SEC-AI-015 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AI-020 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AI-029 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AI-034 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AI-035 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AI-041 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AI-043 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AI-045 | | BLOCKER | AI-SECURITY.md | | | | | |
| SEC-AGENT-007 | | BLOCKER | AGENTIC-DEV-SECURITY.md | | | | | |
| SEC-AGENT-008 | | BLOCKER | AGENTIC-DEV-SECURITY.md | | | | | |
| SEC-AGENT-011 | | BLOCKER | AGENTIC-DEV-SECURITY.md | | | | | |
| SEC-SUPPLY-016 | | BLOCKER | DEPENDENCIES.md | | | | | |
| SEC-CLOUD-016 | | BLOCKER | INFRASTRUCTURE-SECURITY.md | | | | | |
| SEC-MOBILE-001 | | BLOCKER | MOBILE-SECURITY.md | | | | | |
| SEC-AUTH-001 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTH-017 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTH-030 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTH-034 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-004 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-005 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-006 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-007 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-012 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-015 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-021 | | CRITICAL | AUTH.md | | | | | |
| SEC-AUTHZ-031 | | CRITICAL | AUTH.md | | | | | |
| SEC-API-114 | | CRITICAL | API-SECURITY.md | | | | | |
| SEC-API-127 | | CRITICAL | API-SECURITY.md | | | | | |
| SEC-API-128 | | CRITICAL | API-SECURITY.md | | | | | |
| SEC-API-135 | | CRITICAL | API-SECURITY.md | | | | | |
| SEC-API-137 | | CRITICAL | API-SECURITY.md | | | | | |
| SEC-API-018 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-API-019 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-API-027 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-API-034 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-API-035 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-API-045 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-API-056 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-API-057 | | CRITICAL | BACKEND-SECURITY.md | | | | | |
| SEC-WEB-022 | | CRITICAL | FRONTEND-SECURITY.md | | | | | |
| SEC-WEB-026 | | CRITICAL | FRONTEND-SECURITY.md | | | | | |
| SEC-WEB-031 | | CRITICAL | FRONTEND-SECURITY.md | | | | | |
| SEC-WEB-032 | | CRITICAL | FRONTEND-SECURITY.md | | | | | |
| SEC-DB-002 | | CRITICAL | DATABASE-SECURITY.md | | | | | |
| SEC-DB-003 | | CRITICAL | DATABASE-SECURITY.md | | | | | |
| SEC-DB-006 | | CRITICAL | DATABASE-SECURITY.md | | | | | |
| SEC-DB-007 | | CRITICAL | DATABASE-SECURITY.md | | | | | |
| SEC-DB-008 | | CRITICAL | DATABASE-SECURITY.md | | | | | |
| SEC-DB-016 | | CRITICAL | DATABASE-SECURITY.md | | | | | |
| SEC-DB-017 | | CRITICAL | DATABASE-SECURITY.md | | | | | |
| SEC-DATA-001 | | CRITICAL | DATA-PROTECTION.md | | | | | |
| SEC-DATA-005 | | CRITICAL | DATA-PROTECTION.md | | | | | |
| SEC-DATA-011 | | CRITICAL | DATA-PROTECTION.md | | | | | |
| SEC-DATA-059 | | CRITICAL | DATA-PROTECTION.md | | | | | |
| SEC-GOV-051 | | CRITICAL | PRIVACY.md | | | | | |
| SEC-SECRETS-010 | | CRITICAL | SECRETS.md | | | | | |
| SEC-AI-002 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-006 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-017 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-021 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-031 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-040 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-042 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-060 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-061 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AI-062 | | CRITICAL | AI-SECURITY.md | | | | | |
| SEC-AGENT-009 | | CRITICAL | AGENTIC-DEV-SECURITY.md | | | | | |
| SEC-AGENT-014 | | CRITICAL | AGENTIC-DEV-SECURITY.md | | | | | |
| SEC-SUPPLY-002 | | CRITICAL | DEPENDENCIES.md | | | | | |
| SEC-SUPPLY-026 | | CRITICAL | DEPENDENCIES.md | | | | | |
| SEC-SUPPLY-032 | | CRITICAL | DEPENDENCIES.md | | | | | |
| SEC-CLOUD-012 | | CRITICAL | INFRASTRUCTURE-SECURITY.md | | | | | |
| SEC-LOG-001 | | CRITICAL | OBSERVABILITY.md | | | | | |
| SEC-LOG-003 | | CRITICAL | OBSERVABILITY.md | | | | | |
| SEC-LOG-019 | | CRITICAL | OBSERVABILITY.md | | | | | |
| SEC-LOG-024 | | CRITICAL | INCIDENT-RESPONSE.md | | | | | |
| SEC-MOBILE-002 | | CRITICAL | MOBILE-SECURITY.md | | | | | |

## Sign off

| Field | Value |
|-------|-------|
| Commit SHA | |
| Target | |
| Declared stage | |
| Date | |
| Edition and scope | Pro (all requirements) or Free (BLOCKERs and CRITICALs at LAUNCH only) |
| Gate outcome | NOT READY, READY WITH ACCEPTED RISK, or READY. In the free edition: NOT READY, READY WITH ACCEPTED RISK (FREE SCOPE), or READY (FREE SCOPE) |
| Accepted risks (ID, owner, compensating control, expiry) | |
| Reviewer | |
