# Staging Test Window Checklist

One session that settles every dynamic BLOCKER in `docs/hullproof/PRE-LAUNCH-AUDIT.md`. Run it against a staging copy of the audited commit, never against production data. Save the filled copy in the evidence folder named in `docs/security/STAGE.md`. Plan about two to four hours for a small app. Delete this note.

## Before you start

- [ ] Staging runs the audited commit: [SHA]. Staging database and storage are separate from production.
- [ ] Payment and webhook providers are in test mode with test keys only. No live keys are loaded.
- [ ] Test accounts exist: user A and user B (same tenant X), user C (tenant Y), a normal user with no admin role, and an admin if the product has one. Each owns at least one record of every resource type and one stored file.
- [ ] A way to replay requests (browser devtools, a proxy, or `curl`) and a place to store each request and response, with tokens removed.
- [ ] Nothing here uses load, brute force or fuzzing. A handful of requests per check.

## Record format

For every check write: the SEC ID, the exact request, the status and the body summary, pass or fail, the commit SHA the staging copy runs, date, who ran it. A result older than 30 days (Hullproof policy), or taken before the newest migration in the audited commit, is repeated. A check that was skipped is `NOT ASSESSED: NEEDS DYNAMIC TEST`, never blank. A screenshot, export or log from this window never moves a public exposure BLOCKER (public buckets and storage, anonymous data API access, exposed keys, open endpoints) to PASS by itself: the checker runs that anonymous request itself, or the row stays `NOT ASSESSED: NEEDS DYNAMIC TEST`. Your record is owner evidence for the human reviewer.

## Part 1: No credentials at all

- [ ] Replay every endpoint, Server Action and route handler with no cookie and no `Authorization` header. Every non public one returns 401 or 403 with no data and no change. (SEC-API-001)
- [ ] With only the publishable key, call every table and view, every RPC, every API route, server action and storage path. Scan bodies for email, phone, date of birth, bank or card numbers and national ids. None. (SEC-DATA-024, SEC-DB-001)
- [ ] Request a known object URL from each bucket holding user files, with no token. 400, 401, 403 or 404 only. (SEC-DATA-019)
- [ ] Send no token, a token with a changed payload, an `alg: none` token, an expired token and a token signed by another key to one protected endpoint. All rejected. (SEC-AUTH-002)
- [ ] Look for dev login, impersonation or bypass routes, and headers or query parameters that set a user id. None work. (SEC-AUTH-010)

## Part 2: Two users in one tenant

- [ ] As user A, read, update and delete user B's record ids for every resource type. All fail and change nothing. Include a parent id in the path with another user's child id. (SEC-AUTHZ-003)
- [ ] Repeat through the data API for every table exposed to clients. (SEC-AUTHZ-010)
- [ ] As user A, request download, upload and delete for user B's stored object. All refused. (SEC-DATA-020)
- [ ] As user B, call delete, export and correction with user A's id in body, query and path. Refused or only user B's data. With no session, 401. (SEC-DATA-040)
- [ ] AI features: as user A, ask for user B's record and conversation by id. Not in the model context and not returned. A new session loads no memory from user B. (SEC-AI-020, SEC-AI-043, SEC-AI-045)

## Part 3: Two tenants

- [ ] As a member of tenant X, create, update and delete records with tenant Y's ids and with Y's tenant id in the body. All fail, through the API and through the data API. Try inserting another user into your tenant. (SEC-AUTHZ-013, SEC-AUTHZ-014)
- [ ] Retrieval: tenant X queries a phrase unique to tenant Y's document, and again with a client supplied tenant id set to Y. Zero results from Y. Query embedding tables with the anon key: no rows. (SEC-AI-029, SEC-AI-034)

## Part 4: Admin functions

- [ ] Call every admin handler with no session and with a normal user session. 401 or 403, no change. (SEC-AUTHZ-020, SEC-AUTHZ-002)
- [ ] If anyone besides the owner holds a staff role, repeat as support and confirm only the support role's records and fields are readable.

## Part 5: Webhooks and payments (test mode)

- [ ] Each webhook route: unsigned, wrong signature, and a signed body with one byte changed are rejected. A valid test event is accepted. (SEC-API-101)
- [ ] Tamper with price, plan, currency and discount in the checkout request. The checkout uses catalog values. (SEC-API-125)
- [ ] Open the checkout success URL without paying, and post a fake purchase result from the mobile client. Nothing is granted. (SEC-API-126)
- [ ] RevenueCat webhook with no header and with a wrong header: rejected, no side effect. A sandbox payload sent to the production handler is rejected or ignored. A payload signed by a self made certificate chain is rejected. (SEC-API-132, SEC-API-133)

## Part 6: Product MCP server

- [ ] Each tool with no token, an expired token, a token for another audience and a token in the query string: 401 each. A low privilege token is denied on privileged tools. User A's token is denied on user B's and tenant B's ids. A revoked scope is denied on the next call. (SEC-AGENT-007, SEC-AGENT-008)

## Part 7: Secrets in responses

- [ ] Capture one full user journey and scan every response for key patterns (`sb_secret_`, service role JWTs, `sk_live_`, `sk_test_`, AI provider key shapes). None. (SEC-SECRETS-003)
- [ ] SQL injection probes that are read only on the endpoints the code review flagged. (SEC-API-017)

## Sign off

| Field | Value |
|-------|-------|
| Commit tested | |
| Environment | |
| Date | |
| Tester | |
| Checks passed | |
| Checks failed (finding ids) | |
| Checks not run (and why) | |

Not run here and needing other evidence: bundle and image secret scans (NEEDS BUILD), provider settings (see `templates/PROVIDER-EXPORTS.md`), and signed statements (ATTESTATION).
