# Hullproof sample audit report: the hullproof demo app (Free scope)

This is a sample of the report that the Hullproof audit produces. It is the output of an audit of the deliberately vulnerable hullproof demo app, restricted to the Free requirement scope, which means every BLOCKER and CRITICAL requirement. It was produced by running the full audit and keeping only the Free scope. The demo is not a real product: its flaws were planted on purpose and no real data, account or key is involved.

The report reads top down. The verdict comes first, then findings from most to least severe, then what passed, then what could not be settled from the repository alone and who must act to settle it.

| Field | Value |
|---|---|
| Product | hullproof demo (deliberately vulnerable demonstration) |
| Audit date | 2026-10-05 |
| Commit audited | 41186de3ed50a4ca03f9ef8b9c1abf352d3d7d1a |
| Branch | dev |
| Audit type | CODE ONLY. Static review, no live target, no scanner output that names the commit. |
| Release scope | web, API |
| Project stage | GROWTH (declared and derived: a payment webhook that grants plans, an admin role, business customer data) |
| Markets served | Nigeria, EU, global |
| Hullproof version | 0.1.2 |
| Edition and scope | Hullproof Free: the BLOCKER and CRITICAL requirements only. HIGH, MEDIUM and LOW requirements are outside this scope and are not scored. G-6 is outside the scope. |
| Requirements in this scope | 110 (all BLOCKER and CRITICAL): 47 failed, 1 passed, 29 not assessed, 33 not applicable |

## Verdict

**NOT READY** (Free scope). 11 BLOCKER findings are open, 10 BLOCKER requirements and 19 CRITICAL requirements could not be settled from the repository, and no scan output names the audited commit. This verdict covers the Free scope only and says nothing about HIGH, MEDIUM or LOW requirements.

| Gate | Condition (short form) | Met? | Note |
|---|---|---|---|
| G-1 | Stage declared and recorded, not lower than the derived stage | YES | GROWTH in docs/security/STAGE.md, matching the triggers found. |
| G-2 | Audit report for this commit that covers every BLOCKER and CRITICAL requirement | YES | The full run covered all 110 Free requirements. This file is its Free scope extract. |
| G-3 | No open BLOCKER finding | NO | 11 open, all verified from code. |
| G-4 | Every BLOCKER requirement is PASS or NOT APPLICABLE | NO | 19 failed, 10 not assessed, 15 not applicable. |
| G-5 | Every CRITICAL requirement PASS or NOT APPLICABLE, or accepted outside the protected classes | NO | 28 failed, 19 not assessed. No acceptance exists, and several sit in authentication, payments, secrets and authorization, where acceptance is not available. |
| G-6 | HIGH findings | Outside the Free scope | Not evaluated. |
| G-7 | Secret, static and dependency scans ran on this commit with the kit configuration | NO | Static analysis ran with the kit rules but its output does not name the commit. The secret scan and the dependency scan output are absent. |
| G-8 | Rollback path known | NO | None recorded. |

| Finding rating | Findings |
|---|---|
| BLOCKER | 11 |
| CRITICAL | 12 |
| HIGH | 2 |
| MEDIUM | 1 |

The three findings rated below CRITICAL sit under a CRITICAL requirement and were lowered with written code evidence, which the finding shows. The requirement still counts as failed at the gate.

## Findings

Ordered by severity. Each finding lists only the Free requirement IDs it breaks.

### F-01: Notes table has no row level security and is open to the anon role and to every signed in user

- **Severity:** BLOCKER
- **Requirements:** SEC-AUTHZ-010 (BLOCKER), SEC-DATA-024 (BLOCKER), SEC-DB-001 (BLOCKER), SEC-DB-002 (CRITICAL), SEC-DB-003 (CRITICAL)
- **Location:** supabase/migrations/0002_notes.sql:2-9; supabase/migrations/0002_notes.sql:13-14; supabase/migrations/0003_files_billing.sql:2-8, :24-29
- **Why it matters:** Anyone holding the public API key can read every note with no login, and any signed in user can read, change or delete other people's notes. The notes migration never turns on row level security and grants read access to the anonymous role. Two other tables are also created with no explicit access rules.
- **Fix:** Add a forward migration that enables row level security on notes, removes the anonymous grant, and adds owner only policies for each action. Revoke default privileges for new tables so the next table starts locked. Test with the public key and with two users.

### F-02: Any signed in user can set their own role and plan

- **Severity:** BLOCKER
- **Requirements:** SEC-DB-033 (BLOCKER), SEC-AUTHZ-004 (CRITICAL), SEC-AUTHZ-005 (CRITICAL)
- **Location:** src/app/actions/profile.ts:9-13; supabase/migrations/0001_profiles.sql:16-21; src/app/dashboard/page.tsx:99
- **Why it matters:** A signed in user can send their own role or plan to the profile action, or change it through the database API, so any account can become an admin or get a paid plan for free.
- **Fix:** Accept only the display name in the action and in the database grant. Move role and plan to a place no client role can write. Test by sending role and plan as a normal user.

### F-03: Admin API has no server side role check; any signed in user can list, promote and delete users and their data

- **Severity:** BLOCKER
- **Requirements:** SEC-AUTHZ-002 (BLOCKER), SEC-AUTHZ-020 (BLOCKER), SEC-DATA-020 (BLOCKER), SEC-DATA-040 (BLOCKER), SEC-API-027 (CRITICAL)
- **Location:** src/app/api/admin/users/route.ts:10, :18, :26; src/app/admin/page.tsx:31; src/middleware.ts:6, :8-14
- **Why it matters:** The admin routes only check that a session exists. Anyone who signs up can list every user, make anyone an admin, or delete users together with their notes and files. The middleware only looks for a cookie of any value, and the role check lives in the browser.
- **Fix:** Check the admin role on the server at the start of every admin handler, reading it from the database. Treat middleware and page checks as convenience only. Test that a normal user gets 403 on every admin route.

### F-04: Unauthenticated endpoint returns every note and every owner email

- **Severity:** BLOCKER
- **Requirements:** SEC-API-001 (BLOCKER), SEC-DATA-024 (BLOCKER)
- **Location:** src/app/api/notes/export/route.ts:5-8; src/middleware.ts:8-14
- **Why it matters:** One request with no cookie returns every note and the owner's email for every user.
- **Fix:** Require a service credential or remove the route. Return counts only, which is all the code comment says the job needs. Replay with no cookie and expect 401.

### F-05: Note read has no ownership check (direct object reference)

- **Severity:** BLOCKER
- **Requirements:** SEC-AUTHZ-003 (BLOCKER)
- **Location:** src/app/api/notes/[id]/route.ts:13; src/lib/ai/tools.ts:10-12
- **Why it matters:** The note route reads a note by id without checking who owns it. Note ids appear in other responses, so one user can read another user's private notes.
- **Fix:** Add the owner filter to the read query and return 404 when no row matches. Test with two users.

### F-06: SQL injection in note search

- **Severity:** BLOCKER
- **Requirements:** SEC-API-017 (BLOCKER)
- **Location:** src/app/api/search/route.ts:8-10
- **Why it matters:** The search term is pasted into the SQL text. A signed in user can read other users' notes, emails and password hashes, and the error handler shows the SQL error back to them.
- **Fix:** Use a prepared statement with bound values, cap the search length, and test with quote and union payloads.

### F-07: Payment webhook does not enforce its signature and grants plans anyway

- **Severity:** BLOCKER
- **Requirements:** SEC-API-101 (BLOCKER), SEC-API-126 (BLOCKER), SEC-LOG-019 (CRITICAL)
- **Location:** src/app/api/webhooks/payfake/route.ts:15-16; src/lib/config.ts:2
- **Why it matters:** The webhook checks the signature, logs a warning when it fails, then carries on and upgrades the plan. Anyone can send an unsigned request and upgrade any account.
- **Fix:** Return 401 before parsing the body when the signature check fails. Test with unsigned, wrong and altered bodies.

### F-08: Service role key is read from a NEXT_PUBLIC variable and used in browser code

- **Severity:** BLOCKER
- **Requirements:** SEC-DATA-024 (BLOCKER), SEC-SECRETS-001 (BLOCKER), SEC-SECRETS-003 (BLOCKER), SEC-AUTHZ-007 (CRITICAL), SEC-AUTHZ-031 (CRITICAL)
- **Location:** src/lib/adminClient.ts:4; src/lib/adminClient.ts:8; src/components/AdminStats.tsx:1 and :10; src/app/admin/page.tsx:4,36; .env.example:2
- **Why it matters:** A variable whose name starts with NEXT_PUBLIC is placed into the browser bundle. The admin stats component reads a service role key from it, so any visitor would receive a key that skips every access rule. The repository holds a placeholder only, so the exposure depends on the variable being set in a deployment.
- **Fix:** Remove the public variable, rotate any key that was ever set this way, and compute the counts on the server after an admin check. Scan the built output for the key.

### F-09: Hardcoded webhook signing secret committed in source

- **Severity:** BLOCKER
- **Requirements:** SEC-SECRETS-004 (BLOCKER)
- **Location:** src/lib/config.ts:2; src/lib/payfake.ts:2,6
- **Why it matters:** A signing secret for the payment webhook is written in a source file, the same in every environment, and cannot be rotated without a code change. The file calls it made up, but the code uses it as the real key.
- **Fix:** Load it from a server only environment variable, stop at startup when it is missing, and rotate the committed value, treating it as exposed.

### F-10: Server side sessions never expire

- **Severity:** BLOCKER
- **Requirements:** SEC-AUTH-002 (BLOCKER)
- **Location:** src/lib/session.ts:12-22; src/lib/fakeAuth.ts:35
- **Why it matters:** Session rows have no expiry and the server never checks their age. A token that leaks, for example through the logs or the injection above, works for ever. A proposal to rate this lower was reviewed and rejected, because the evidence did not limit reach or impact.
- **Fix:** Add an expiry and last seen time, check them on every lookup, and set a 30 day absolute limit with a shorter one for admins.

### F-11: AI tools run without per user scoping

- **Severity:** BLOCKER
- **Requirements:** SEC-AI-015 (BLOCKER), SEC-AI-020 (BLOCKER), SEC-AI-021 (CRITICAL)
- **Location:** src/lib/ai/tools.ts:10-12; src/lib/ai/tools.ts:17-20; src/lib/ai/tools.ts:3,7,13; src/app/api/ai/assistant/route.ts:41-44; src/lib/ai/fakeModel.ts:7-16
- **Why it matters:** The read_note tool selects a note by id with no owner filter, so a user can have the assistant return another user's note. The email tool accepts any address the model names, and any tool the model names runs at once.
- **Fix:** Scope each tool to the signed in user, validate the arguments of each tool, send mail only to the user's own address, and test with two users.

### F-12: Payment webhook grants plans with no order match, no deduplication, no ordering, no environment check and no refund handling

- **Severity:** CRITICAL
- **Requirements:** SEC-API-127 (CRITICAL), SEC-API-128 (CRITICAL), SEC-API-135 (CRITICAL)
- **Location:** src/app/api/webhooks/payfake/route.ts:6-11
- **Why it matters:** The webhook trusts the plan in the event body. It does not match an order, amount or currency, does not store event ids so a replay repeats, does not check the environment, and never revokes on refunds or chargebacks.
- **Fix:** Create orders on the server at checkout, match each event to an order, store the provider event id under a unique constraint, reject test events in production, and handle refunds.

### F-13: Server side request forgery in import from URL

- **Severity:** CRITICAL
- **Requirements:** SEC-API-035 (CRITICAL)
- **Location:** src/app/api/notes/import-url/route.ts:6, :14-16, :17-22
- **Why it matters:** Any signed in user can make the server fetch any URL, including internal addresses, and the fetched text is stored as a note the user can read back. Rated CRITICAL: it moves to BLOCKER if the host exposes a metadata address or an internal service.
- **Fix:** Allow only http and https, resolve and check every address against a blocked range list, pin the connection to the checked address, treat redirects the same way, and set time and size limits.

### F-14: Home made authentication with no recorded reason

- **Severity:** CRITICAL
- **Requirements:** SEC-AUTH-001 (CRITICAL), SEC-DATA-005 (CRITICAL)
- **Location:** src/lib/fakeAuth.ts:7-18; src/lib/fakeAuth.ts:34-35; src/lib/db.ts:11-15
- **Why it matters:** Sign in is built by hand: scrypt with default cost settings and session tokens stored unhashed, with no recorded reason for not using a managed identity service.
- **Fix:** Use a managed identity provider, or record the exception with owner and expiry, hash session tokens and raise the scrypt cost.

### F-15: No multi factor authentication for anyone, including admins

- **Severity:** CRITICAL
- **Requirements:** SEC-AUTHZ-021 (CRITICAL)
- **Location:** src/lib/fakeAuth.ts:29-37; src/app/api/admin/users/route.ts
- **Why it matters:** A password is the only factor for everyone, including admins, and the product holds payment state and personal data.
- **Fix:** Add TOTP or passkeys and require the second factor on every admin route.

### F-16: CORS reflects any Origin and allows credentials on every API route

- **Severity:** CRITICAL
- **Requirements:** SEC-WEB-022 (CRITICAL)
- **Location:** src/middleware.ts:17-22; src/middleware.ts:26
- **Why it matters:** Every API route repeats the caller's Origin back and allows credentials, so any site that can send the session cookie can read private responses.
- **Fix:** Match the origin against an exact list per environment, send no CORS headers otherwise, and never combine a reflected origin with credentials.

### F-17: No CSRF control on cookie authenticated state changes

- **Severity:** CRITICAL
- **Requirements:** SEC-WEB-026 (CRITICAL)
- **Location:** src/middleware.ts:4-26; src/app/actions/profile.ts:15; src/app/api/auth/login/route.ts:13; state changing handlers under src/app/api (notes, files, admin, assistant, import)
- **Why it matters:** State changing routes and the profile action rely on the cookie alone, with no origin or fetch metadata check. A request from another site or a sibling host can change data, delete notes or change roles.
- **Fix:** Reject non GET requests that are cross site or from an unlisted origin, require a JSON content type, and set allowed origins for server actions.

### F-18: Session token and email address are written to logs

- **Severity:** CRITICAL
- **Requirements:** SEC-LOG-001 (CRITICAL)
- **Location:** src/app/api/auth/login/route.ts:24; src/app/api/auth/login/route.ts:20
- **Why it matters:** Login writes the new session token and the email to the logs, so anyone who can read logs can take over a session.
- **Fix:** Remove the token and email from log calls, log a user id and outcome only, add redaction and a lint rule.

### F-19: Authentication and authorization events are mostly not logged

- **Severity:** CRITICAL
- **Requirements:** SEC-LOG-003 (CRITICAL)
- **Location:** src/lib/http.ts:10; src/app/api/auth/signup/route.ts:10-15; src/app/api/auth/logout/route.ts:6-11; src/app/api/notes/[id]/route.ts:26, :33
- **Why it matters:** Failed logins, denials, sign up and sign out leave no log entry, so password guessing and probing of other users' objects cannot be seen.
- **Fix:** Add one helper that logs every denial and authentication event with a request id, and call it from every route.

### F-20: CI workflow puts pull request text into a shell on a write all token

- **Severity:** CRITICAL
- **Requirements:** SEC-SUPPLY-032 (CRITICAL)
- **Location:** .github/workflows/ci.yml:4; .github/workflows/ci.yml:9; .github/workflows/ci.yml:20
- **Why it matters:** The workflow runs on pull_request_target with a write all token and puts the pull request title inside a shell command. A crafted title runs a command with write rights on the repository.
- **Fix:** Use pull_request or pass the title through an environment variable, set read only permissions at the top, and run a workflow linter in CI.

### F-21: Prompt injection chain reaches an outbound send with no human confirmation

- **Severity:** CRITICAL
- **Requirements:** SEC-AI-017 (CRITICAL)
- **Location:** src/app/api/notes/import-url/route.ts:14-21; src/app/api/ai/assistant/route.ts:32-44; src/lib/ai/tools.ts:17-20
- **Why it matters:** Imported web pages and note text sit in the same prompt as the user's question, and a tool marker inside them is run. Nothing asks the user to confirm before data is sent out.
- **Fix:** Do not run tool calls inside the request. Return proposed actions with a description built by the server, and require a confirmation tied to the exact arguments.

### F-22: No breach runbook and no secret rotation procedure

- **Severity:** CRITICAL
- **Requirements:** SEC-LOG-024 (CRITICAL), SEC-SECRETS-010 (CRITICAL)
- **Location:** No runbook or rotation procedure exists anywhere in the repository
- **Why it matters:** There is no breach notification runbook and no procedure to rotate a leaked secret, while exposed secrets and an open export route exist. The EU and Nigeria clocks are 72 hours.
- **Fix:** Write the runbook with a decision tree and templates for each market, add one page per secret covering revoke, reissue and redeploy within a working day, and rehearse it once.

### F-23: No backup, restore or rollback path

- **Severity:** CRITICAL
- **Requirements:** SEC-DB-017 (CRITICAL)
- **Location:** src/lib/db.ts:41-45; src/lib/db.ts:30-36
- **Why it matters:** The only database is in memory, so a restart wipes users, notes and files. There is no backup, no restore record and no rollback path.
- **Fix:** Move to the persistent database the migrations describe, enable backups and point in time recovery, keep an off account copy, and record a restore test.

### F-24: AI usage budget lives in process memory

- **Severity:** HIGH
- **Requirements:** SEC-AI-002 (CRITICAL)
- **Location:** src/app/api/ai/assistant/route.ts:13-22
- **Why it matters:** The per user daily limit for the assistant is a map in process memory. It resets on restart and is separate on every instance. The model is a local function today, so no money is spent yet.
- **Fix:** Keep the counter in the database or a shared store, count tokens or cost, and increment atomically.

### F-25: Dependency scan runs on an unlocked tree with no schedule

- **Severity:** HIGH
- **Requirements:** SEC-SUPPLY-002 (CRITICAL)
- **Location:** package.json (no lockfile); .github/workflows/ci.yml:3-7; .github/workflows/ci.yml:21-22
- **Why it matters:** The dependency scan runs on a tree that CI has just resolved with no lockfile, has no schedule, and skips dev dependencies that run in CI. A step that fails on high findings does exist.
- **Fix:** Commit a lockfile, scan it with the OSV scanner on every change, and add a weekly scheduled run.

### F-26: No record that the AI feature was screened against prohibited practices

- **Severity:** MEDIUM
- **Requirements:** SEC-GOV-051 (CRITICAL)
- **Location:** src/app/api/ai/assistant/route.ts:9-46; src/lib/ai/tools.ts:9-21
- **Why it matters:** No record shows the AI feature was screened against prohibited practices. A search found none present, so the gap is a missing record.
- **Fix:** Record the screen result and the search in the threat model for the feature.

## Passed

| Requirement | Evidence |
|---|---|
| SEC-API-137 (CRITICAL) | Searches for card, cvc and checkout terms and for payment provider names over the 45 product files return no hits, and no form field or schema collects card data. |

One pass is not much. Most BLOCKER and CRITICAL requirements can only be settled by a dashboard export, a test run or a build, so a repository only run cannot pass them.

## Not assessed: what the owner must do

These requirements could not be settled from the repository. They stay open at the gate until the action is done, and none counts as passing. The actions are grouped so one export or one test session closes many.

### A staging test session (templates/STAGING-TEST-WINDOW.md)

| Requirement | Severity | Title | What closes it |
|---|---|---|---|
| SEC-AI-029 | BLOCKER | Authorization inside the retrieval query | Run a two user retrieval test on staging. |
| SEC-AI-043 | BLOCKER | Model context holds only data the current user may see | Ask as user A for user B's note on staging and inspect the model request. |
| SEC-AUTH-010 | BLOCKER | No authentication bypass paths in production | Try test login, bypass and impersonation routes against a production build and confirm none opens. |
| SEC-DATA-019 | BLOCKER | Buckets holding user data have no public access path | Export the bucket list with public flags, and request a known object URL with no token. |
| SEC-DB-034 | BLOCKER | Credential and token tables have no client grants and are not reachable through the Data API | Run the four verbs with the public key against every table holding credentials on a staging project and attach the result. |
| SEC-DB-035 | BLOCKER | Content shown to more than one user without author attribution is written only by server code | Run a two user write test against any table whose content is shown to several users, on staging. |
| SEC-AGENT-014 | CRITICAL | No direct agent path to production | Export the branch ruleset and show that a push with the agent token is rejected. |
| SEC-AI-042 | CRITICAL | No secrets in hidden context | Run a prompt extraction test on staging. |
| SEC-API-018 | CRITICAL | Map query structure input through a fixed allowlist | Send malicious identifier values to sort, filter and column parameters on a running copy and confirm they are refused. |
| SEC-API-045 | CRITICAL | Never serve uploads as active content from the app origin | Upload an HTML file on a running copy, open the download URL and confirm it is saved, not rendered. |
| SEC-API-114 | CRITICAL | Fail closed when the limiter is unavailable on paid routes | Make the limiter store unavailable on a running copy and confirm the route refuses instead of allowing. |
| SEC-AUTH-017 | CRITICAL | Logout ends the session on the server | Capture a token, log out, replay it on a sensitive route and an ordinary route. Both must fail. |
| SEC-AUTHZ-006 | CRITICAL | Authorization errors result in denial | Force the session lookup to throw and to return nothing on a running copy. Both must deny. |
| SEC-AUTHZ-012 | CRITICAL | Server side caches keyed by user and tenant | Request the same route as two users and confirm no data crosses between them. |
| SEC-DATA-001 | CRITICAL | Unguessable values come from a CSPRNG | Generate 1,000 tokens and ids, check they are unique, and attach the result. |
| SEC-DATA-011 | CRITICAL | External endpoints use TLS 1.2 or 1.3 with trusted certificates | Run a TLS test on every public hostname. |
| SEC-DATA-059 | CRITICAL | Storage keys presented by the client resolve to a record issued to the caller's tenant | Run the two tenant test on file access. |
| SEC-DB-006 | CRITICAL | RLS policies never trust user editable claims | Call the identity update with a role claim on a staging project and confirm no policy trusts it. |
| SEC-SUPPLY-026 | CRITICAL | No source control metadata on deployed sites | Request the repository metadata paths on every deployed host. |
| SEC-WEB-031 | CRITICAL | List and justify every raw HTML sink | Store script and markup payloads and render them in a browser to confirm nothing runs. |

### Provider exports (templates/PROVIDER-EXPORTS.md)

| Requirement | Severity | Title | What closes it |
|---|---|---|---|
| SEC-AGENT-011 | BLOCKER | No production secrets in coding agent context | Run the redacted scan of each agent machine for production keys, logins and connector grants and attach the counts. |
| SEC-AUTH-008 | BLOCKER | No default, shared or seeded accounts in production | List the users in every deployed database and confirm no seeded account exists. |
| SEC-SUPPLY-016 | BLOCKER | Pipeline secrets only in the CI secret store | Export the repository, environment and organisation secret names and the environment branch restriction, and scan history with the kit's secret scanner. |
| SEC-CLOUD-012 | CRITICAL | MFA on every privileged platform account | Export the MFA status of every privileged member on the source host, hosting, database, DNS, registrar and payment accounts. |
| SEC-DB-007 | CRITICAL | Views, materialized views and foreign tables cannot bypass row level security | List views and foreign tables in the exposed schemas and confirm none bypasses row level security. |
| SEC-DB-008 | CRITICAL | Security definer functions are not callable by clients | List functions in the exposed schemas and confirm none is a security definer callable by clients. |
| SEC-DB-016 | CRITICAL | No reset style rollback against remote databases or real data | Owner confirms in writing that no coding agent holds production database credentials (agent settings sit outside the repository). |
| SEC-SUPPLY-035 | CRITICAL | No account wide or organisation wide credential in CI or an agent workspace | Export the secret list and token scopes for repository, environment and organisation, and show a cross project denial. |

### A production build from this commit, scanned

| Requirement | Severity | Title | What closes it |
|---|---|---|---|
| SEC-AI-041 | BLOCKER | Model provider and vector store keys stay on the server | Build from this commit and scan the output and history with the kit's secret scanner. |

## What this report does not cover

The Pro edition checks a further 545 requirements (HIGH, MEDIUM and LOW), and this Free report does not score them. The same run reported 48 further findings that sit only under those requirements.

## Limits

This report reflects the commit and date above. It is based on code review and one static analysis output, not on live testing, and no exploitation is claimed. NOT READY means the known risks in the Free scope are open. A READY (FREE SCOPE) outcome would say nothing about HIGH, MEDIUM or LOW requirements.

