# Hullproof Lite Checklist

A short checklist for a solo builder or small team that wants the 56 things not to get wrong before sharing a link. Every row comes from a full Hullproof requirement. Each one is a BLOCKER or a LAUNCH stage CRITICAL, and each has a five minute check you can run yourself.

## How this relates to the full free edition

Lite is a subset, not a smaller edition. The free edition still holds every BLOCKER and every LAUNCH stage CRITICAL requirement, and the gate verdict still comes from `/hullproof-prelaunch` run on all of them. Passing every row below is not the same as READY. Use Lite to catch the common failures early and to find out where to start.

## How to mark results

Tick the box when you ran the check and it passed. Leave it empty when you have not checked or it failed, and write what you found next to the row. If a row does not apply to your product, write N/A and one line saying why. The ID links to the full requirement, which has the complete verification steps and the evidence to keep.

## Authentication

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-AUTH-001](AUTH.md#sec-auth-001-no-custom-password-storage-or-token-generation) | CRITICAL | Use your auth provider for passwords and sessions. Do not write your own hashing, token or reset code. | Search the auth, session and reset code for bcrypt, createHash, createHmac and Math.random. Any hit needs a written reason. |
| [ ] | [SEC-AUTH-002](AUTH.md#sec-auth-002-server-verifies-identity-tokens-before-trusting-them) | BLOCKER | Make the server check every login token before it trusts it. Refuse a token with a changed body, no signature, or the wrong signer, audience or issuer. | Send each of these to one protected endpoint: no token, an edited token, an expired token, an alg: none token, a token signed by another key, a signed token for another audience, and one for another issuer. All seven must return 401 or 403. |
| [ ] | [SEC-AUTH-008](AUTH.md#sec-auth-008-no-default-shared-or-seeded-accounts-in-production) | BLOCKER | Remove test, demo and seeded accounts from production. Nobody should share a login. | List production users and compare them with your seed files. There should be no matches. |
| [ ] | [SEC-AUTH-010](AUTH.md#sec-auth-010-no-authentication-bypass-paths-in-production) | BLOCKER | Delete any shortcut that skips login, such as a dev login route or a header that sets the user. | Search for routes and flags named dev-login, test-login, impersonate and bypass. Confirm none works in production. |
| [ ] | [SEC-AUTH-017](AUTH.md#sec-auth-017-logout-ends-the-session-on-the-server) | CRITICAL | Make logout end the session on the server, not only in the browser. | Copy your tokens, log out, then replay them with curl. The refresh token must fail at once, the old access token must fail on a sensitive action such as a payment or an account change, and any call must fail once the access token lifetime has passed. |

## Authorization

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-AUTHZ-002](AUTH.md#sec-authz-002-server-side-permission-check-in-every-handler-deny-by-default) | BLOCKER | Check permissions inside every server handler and refuse by default. Hiding a button is not a check. | List your route handlers and server actions. Each one must call your permission check before it reads or writes. |
| [ ] | [SEC-AUTHZ-003](AUTH.md#sec-authz-003-object-level-check-for-every-record-identified-by-request-input) | BLOCKER | When a request names a record, confirm the signed in user owns it or may access it. | As user A, read, edit and delete a record owned by user B. Every attempt must fail and change nothing. |
| [ ] | [SEC-AUTHZ-004](AUTH.md#sec-authz-004-writable-field-allowlist-no-privilege-fields-from-the-client) | CRITICAL | Accept only a fixed list of fields from the client. Never let a request set role, owner, price or admin flags. | Send role, owner_id, tenant_id and is_admin in a normal update request. They must be ignored or refused. |
| [ ] | [SEC-AUTHZ-010](AUTH.md#sec-authz-010-ownership-policies-on-user-owned-tables) | BLOCKER | Turn on ownership rules in the database for tables that hold user data, so users can only reach their own rows. | Using only the public key and user A's token, try to read, edit and delete user B's rows. Expect no rows or a permission error. |
| [ ] | [SEC-AUTHZ-013](AUTH.md#sec-authz-013-no-operation-crosses-a-tenant-boundary) | BLOCKER | If you have teams or workspaces, never let one team see or change another team's data. | Create two teams. As an admin of team X, request team Y's records by ID and with no filter. No Y data may appear. |
| [ ] | [SEC-AUTHZ-020](AUTH.md#sec-authz-020-admin-functions-guarded-by-a-server-side-admin-role-check) | BLOCKER | Guard every admin function with a server side admin check. | List your admin routes and actions. Call each one as a normal user and confirm it is refused. |
| [ ] | [SEC-DATA-040](PRIVACY.md#sec-data-040-deletion-and-export-act-only-on-the-callers-own-data) | BLOCKER | Make account deletion, export and correction act only on the signed in user's own data. | As user B, call delete, export and correction with user A's id in the body, query and path. Each must be refused or touch only user B's data. |

## API security

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-API-001](API-SECURITY.md#sec-api-001-authenticate-every-non-public-endpoint) | BLOCKER | Require a signed in user on every endpoint that is not meant to be public. | Replay every request your app makes with no cookie and no token. Each non public one must return 401 or 403 and no data. |
| [ ] | [SEC-API-101](API-SECURITY.md#sec-api-101-verify-the-webhook-sender-before-processing) | BLOCKER | Check the sender signature on every webhook before you act on it. | Send an unsigned request, a wrongly signed one and a signed one with one byte changed. Each must be refused and create nothing. |
| [ ] | [SEC-API-125](API-SECURITY.md#sec-api-125-set-prices-and-plans-from-the-server-catalog) | BLOCKER | Take prices and plans from your own server catalog, never from the request. | In test mode, change the price, plan and currency in the checkout request. The checkout must still use your catalog values. |
| [ ] | [SEC-API-126](API-SECURITY.md#sec-api-126-grant-entitlements-only-from-verified-server-side-signals) | BLOCKER | Grant paid access only when a verified payment signal reaches your server. | Open the checkout success URL without paying. Nothing must be granted. |
| [ ] | [SEC-API-127](API-SECURITY.md#sec-api-127-match-provider-payment-details-to-the-order-before-granting) | CRITICAL | Before granting access, match the payment amount, currency and order to what you expected. | Replay a verified event with a lower amount or a different product. None of them may grant access. |
| [ ] | [SEC-DATA-024](PRIVACY.md#sec-data-024-no-endpoint-returns-personal-data-to-an-unauthenticated-caller) | BLOCKER | Make sure no endpoint, table or view returns personal data to someone who is not signed in. | Using only the public key, call every table, view, function and route. Search the responses for email, phone, birth date and national ID patterns. Expect none. |

## Secrets

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-SECRETS-001](SECRETS.md#sec-secrets-001-no-secret-in-client-bundles-or-public-environment-variables) | BLOCKER | Keep secrets out of the browser bundle and out of public environment variables. | Build the app and search the output folder for your key formats. Also check no secret name starts with NEXT_PUBLIC_ or EXPO_PUBLIC_. |
| [ ] | [SEC-SECRETS-003](SECRETS.md#sec-secrets-003-keys-that-bypass-access-control-stay-in-trusted-server-code) | BLOCKER | Use keys that bypass access control, such as a Supabase service role key, only in trusted server code. | Search the code for every place the key is read. Each must be server only. |
| [ ] | [SEC-SECRETS-004](SECRETS.md#sec-secrets-004-no-valid-secret-in-the-repository-or-its-history) | BLOCKER | Make sure no working secret sits in your repository or its history. | Run gitleaks over the full history of all branches. Expect zero findings, or only keys you have already revoked. |
| [ ] | [SEC-SECRETS-010](SECRETS.md#sec-secrets-010-leaked-secrets-are-revoked-and-rotated-first) | CRITICAL | Write down how to revoke and replace each production secret, and do it first when one leaks. | Read the steps for each secret. Rotate one on staging and confirm the old value is refused. |
| [ ] | [SEC-LOG-001](OBSERVABILITY.md#sec-log-001-no-credentials-or-payment-data-in-logs) | CRITICAL | Keep passwords, tokens and card data out of your logs and error reports. | Run sign in, reset, magic link, invite, payment and webhook flows on staging, force a failure, then search the exported logs for the test credentials and tokens, including tokens that sit in URLs. |

## Database

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-DB-001](DATABASE-SECURITY.md#sec-db-001-row-level-security-enabled-on-every-exposed-table) | BLOCKER | Turn on row level security for every table the app can reach. | Run the Supabase security advisor and confirm no rls_disabled findings. Also list tables where rowsecurity is false in your exposed schemas. |
| [ ] | [SEC-DB-002](DATABASE-SECURITY.md#sec-db-002-one-explicit-policy-per-allowed-operation-scoped-to-a-role) | CRITICAL | Write one explicit rule per allowed action and scope it to a role. Never use a rule that is simply true. | Review pg_policies. Each allowed action has a policy and none on user data is open to everyone. |
| [ ] | [SEC-DB-003](DATABASE-SECURITY.md#sec-db-003-new-tables-and-functions-are-not-exposed-by-default-privileges) | CRITICAL | Make sure new tables and functions are not open to the public API by default. | Create a test table with no grants and request it with the public key. You should get a permission error. |
| [ ] | [SEC-DB-033](DATABASE-SECURITY.md#sec-db-033-client-roles-cannot-write-billing-entitlement-verification-role-or-credential-columns) | BLOCKER | Stop client roles from writing billing, plan, role, verification or credential columns. | Run the column privileges query for anon and authenticated. No sensitive column should allow insert or update. |
| [ ] | [SEC-DB-034](DATABASE-SECURITY.md#sec-db-034-credential-and-token-tables-have-no-client-grants-and-are-not-reachable-through-the-data-api) | BLOCKER | Keep credential and token tables out of reach of the public API. | List tables with hash, token, secret or code columns. Confirm client roles have no grants on them. |
| [ ] | [SEC-DB-017](DATABASE-SECURITY.md#sec-db-017-automated-production-database-backups) | CRITICAL | Run automated backups of the production database and test a restore. | Confirm a successful backup in the last 24 hours and read the record of a restore into a scratch environment. |

## Dependencies

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-SUPPLY-002](DEPENDENCIES.md#sec-supply-002-dependency-vulnerability-gate-in-ci) | CRITICAL | Make your pipeline fail when a dependency has a known serious vulnerability. | On a branch, add a package version with a known advisory. The CI run must fail. |
| [ ] | [SEC-SUPPLY-016](DEPENDENCIES.md#sec-supply-016-pipeline-secrets-only-in-the-ci-secret-store) | BLOCKER | Keep pipeline credentials in the CI secret store only, never in workflow files. | Run gitleaks over workflow files and history, and read each workflow to confirm every credential comes from the secret store. |
| [ ] | [SEC-SUPPLY-026](DEPENDENCIES.md#sec-supply-026-no-source-control-metadata-on-deployed-sites) | CRITICAL | Do not deploy your .git folder or other source control files. | Request /.git/HEAD and /.git/config on every production and preview host. Expect 403 or 404. |
| [ ] | [SEC-SUPPLY-032](DEPENDENCIES.md#sec-supply-032-no-untrusted-event-data-expanded-into-workflow-scripts) | CRITICAL | Do not paste untrusted event data, such as a pull request title, into workflow scripts. | Run zizmor and actionlint on your workflows and confirm there are no template injection findings. |
| [ ] | [SEC-AGENT-011](AGENTIC-DEV-SECURITY.md#sec-agent-011-no-production-secrets-in-coding-agent-context) | BLOCKER | Keep production secrets out of the environment your coding agent can read. | Run env in the agent's shell and scan the working folder and .env files with gitleaks. No production values should appear. |

## Frontend

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-WEB-022](FRONTEND-SECURITY.md#sec-web-022-choose-cors-origins-from-an-exact-allowlist) | CRITICAL | Allow only an exact list of origins in CORS. Never echo back whatever origin asks. | Send requests with Origin set to https://evil.example and null. Neither may be allowed on a private route. |
| [ ] | [SEC-WEB-026](FRONTEND-SECURITY.md#sec-web-026-protect-cookie-authenticated-state-changes-against-forgery) | CRITICAL | Protect actions that use cookies from forged requests sent by other sites. | While signed in, submit each state changing route from a page on another origin. Every one must fail. |
| [ ] | [SEC-WEB-031](FRONTEND-SECURITY.md#sec-web-031-list-and-justify-every-raw-html-sink) | CRITICAL | List every place the app writes raw HTML, such as dangerouslySetInnerHTML or innerHTML, and justify each. | Search the whole source for each raw HTML sink and compare the hits with your list. |
| [ ] | [SEC-WEB-032](FRONTEND-SECURITY.md#sec-web-032-sanitize-user-supplied-html-with-a-maintained-library) | CRITICAL | Clean any user supplied HTML with a maintained sanitizer library before showing it. | Store an img onerror payload and a javascript: link through each rich text input. Render them and confirm no script runs. |
| [ ] | [SEC-DATA-011](DATA-PROTECTION.md#sec-data-011-external-endpoints-use-tls-12-or-13-with-trusted-certificates) | CRITICAL | Serve every public hostname over TLS 1.2 or 1.3 with a valid certificate. | Run testssl.sh or SSL Labs against each hostname. Fail on TLS 1.0, TLS 1.1, or an expired or mismatched certificate. |

## Backend

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-API-017](BACKEND-SECURITY.md#sec-api-017-parameterize-every-database-query) | BLOCKER | Pass user input to the database as parameters, never by joining strings into a query. | Search for template literals or string joins passed to raw, execute, query, rpc and filter calls. Review each hit. |
| [ ] | [SEC-API-020](BACKEND-SECURITY.md#sec-api-020-never-run-shell-commands-built-from-untrusted-data) | BLOCKER | Never build shell commands from user data. | Search for exec, execSync and spawn with shell true, and for template strings passed to any process call. |
| [ ] | [SEC-API-021](BACKEND-SECURITY.md#sec-api-021-never-evaluate-untrusted-data-or-model-output-as-code) | BLOCKER | Never run user data or model output as code. | Search for eval, new Function, vm.run and dynamic import or require with a variable path. |
| [ ] | [SEC-API-027](BACKEND-SECURITY.md#sec-api-027-authorize-at-the-point-of-data-access-never-only-in-proxy) | CRITICAL | Check permissions where the data is read, not only in middleware or proxy. | Call each protected server action and route directly, skipping the redirect. Each must still refuse. |
| [ ] | [SEC-API-035](BACKEND-SECURITY.md#sec-api-035-guard-user-and-model-supplied-urls-before-connecting) | CRITICAL | Before fetching a URL a user or the model gave you, refuse private and internal addresses. | Submit http://169.254.169.254/, http://localhost, http://[::1] and file:/// URLs. All must be rejected. |
| [ ] | [SEC-API-045](BACKEND-SECURITY.md#sec-api-045-never-serve-uploads-as-active-content-from-the-app-origin) | CRITICAL | Never serve uploaded files as active content from your app's own origin. | Upload an HTML file and open its download link. It must download or load from a different origin and run nothing. |

## Deployment

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-CLOUD-012](INFRASTRUCTURE-SECURITY.md#sec-cloud-012-mfa-on-every-privileged-platform-account) | CRITICAL | Turn on two factor sign in for every account that can deploy, read production keys, or change DNS and billing. Owner and admin accounts use a passkey or security key where the platform offers one, and SMS alone does not count. | List members on each platform with their capabilities and MFA status. Include the domain registrar. For each owner account, confirm a passkey or security key is registered. |
| [ ] | [SEC-CLOUD-016](INFRASTRUCTURE-SECURITY.md#sec-cloud-016-no-secrets-in-container-images) | BLOCKER | Keep secrets out of container images. | Scan the built image with trivy or gitleaks and read docker history for ENV, ARG and COPY values. |
| [ ] | [SEC-DB-016](DATABASE-SECURITY.md#sec-db-016-no-reset-style-rollback-against-remote-databases-or-real-data) | CRITICAL | Never run reset or rollback commands against a remote database or real data. | Search scripts, CI and agent config for migration down, db reset, `--linked` and `--db-url`. None may target a real database. |
| [ ] | [SEC-DATA-019](DATA-PROTECTION.md#sec-data-019-buckets-holding-user-data-have-no-public-access-path) | BLOCKER | Make sure storage buckets holding user files cannot be read publicly. | Request a known object URL without a token. Expect 400, 401, 403 or 404. |
| [ ] | [SEC-LOG-019](OBSERVABILITY.md#sec-log-019-authentication-validation-and-signature-checks-fail-closed) | CRITICAL | Make login, input validation and signature checks refuse when they error, never let the request through. | Force the auth client, validator and signature check to throw in a test. Each protected route must deny and write nothing. |

## AI security

| Done | ID | Severity | What to do | How to check in five minutes |
|---|---|---|---|---|
| [ ] | [SEC-AI-015](AI-SECURITY.md#sec-ai-015-security-decisions-enforced-in-code-never-by-the-model) | BLOCKER | Enforce security decisions in your code. The model may suggest, but it must never decide who can do what. | For each AI feature, trace every privileged action and confirm a server check that does not depend on model output. |
| [ ] | [SEC-AI-020](AI-SECURITY.md#sec-ai-020-tools-run-as-the-end-user-never-as-a-service-role) | BLOCKER | Run AI tools as the signed in user, never with a service role key. | Start the tool server with the service key removed. Every tool should still work for a normal user or fail safely. |
| [ ] | [SEC-AI-041](AI-SECURITY.md#sec-ai-041-model-provider-and-vector-store-keys-stay-on-the-server) | BLOCKER | Keep model provider and vector store keys on the server. | Run gitleaks on the repo and search the build output for provider key patterns and public prefixed AI key names. |
| [ ] | [SEC-AI-043](AI-SECURITY.md#sec-ai-043-model-context-holds-only-data-the-current-user-may-see) | BLOCKER | Put only data in the model context that the current user is allowed to see. | Ask as user A about a record of user B. Inspect the provider request and confirm the record is not in it. |
| [ ] | [SEC-AI-045](AI-SECURITY.md#sec-ai-045-conversation-history-and-memory-isolated-per-user-and-tenant) | BLOCKER | Keep chat history and AI memory separate for each user and team. | As user A, request user B's conversation ID and start a new session. Both must show nothing from B. |
| [ ] | [SEC-AI-002](AI-SECURITY.md#sec-ai-002-per-user-ai-usage-budget-enforced-in-the-app) | CRITICAL | Cap how much AI each user can spend, and enforce the cap in your app. | Set a tiny budget for a test user and send requests until it is exceeded. The next request must be refused with zero model calls. |

## What Lite does not cover

Lite leaves out areas the full free edition covers, including payments beyond the basics above, file uploads, webhooks in depth, multi tenant data separation beyond the core checks, privacy and the markets you serve, incident response and breach deadlines, mobile apps, MCP servers, retrieval over your own documents (RAG), and tables whose content several users read. If your product touches any of these, Lite is not enough, so run `/hullproof-prelaunch` on the full set.

## Free and Pro

The free edition holds every BLOCKER and every LAUNCH stage CRITICAL requirement, with the standard, the audit workflow and the pre launch gate. Pro holds every requirement in the registry, including the HIGH, MEDIUM and LOW ones, with the same tooling. Lite is the same in both editions.
