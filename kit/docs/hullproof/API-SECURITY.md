# API Security

| Field | Value |
|-------|-------|
| Domain codes | SEC-API |
| Topics covered | API Security, Input Validation, Third-Party Integrations, Webhooks, Rate Limiting, Abuse Prevention, Payments |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers the server side surface of a product: endpoints and Server Actions, input validation, server side interpreters, backend service behavior, outbound requests, file uploads, and calls to third party APIs. Object and tenant authorization rules live in [AUTH.md](AUTH.md), row level security and database roles in [DATABASE-SECURITY.md](DATABASE-SECURITY.md), browser side controls in [FRONTEND-SECURITY.md](FRONTEND-SECURITY.md), storage buckets and signed download URLs in [DATA-PROTECTION.md](DATA-PROTECTION.md), error responses and failure handling in [OBSERVABILITY.md](OBSERVABILITY.md), dependency versions in [DEPENDENCIES.md](DEPENDENCIES.md), and model specific output handling in [AI-SECURITY.md](AI-SECURITY.md). The core requirements are numbered from SEC-API-001; webhooks, rate limiting, abuse prevention and payments start at SEC-API-101. API keys, API versioning and idempotency are Pro edition requirements, and outbound webhooks the product sends are Pro edition requirements.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 12 of the 60 requirements in this domain: every BLOCKER and every CRITICAL requirement in it. Hullproof Pro holds the other 48. Pro covers the wider API surface, including how responses are shaped, how webhooks and payments are handled, how keys are issued and how abuse is limited.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-API-001](#sec-api-001-authenticate-every-non-public-endpoint) | Authenticate every non public endpoint | BLOCKER | LAUNCH | API, Backend, Serverless, SaaS |
| [SEC-API-101](#sec-api-101-verify-the-webhook-sender-before-processing) | Verify the webhook sender before processing | BLOCKER | LAUNCH | API, Backend, Serverless |
| [SEC-API-114](#sec-api-114-fail-closed-when-the-limiter-is-unavailable-on-paid-routes) | Fail closed when the limiter is unavailable on paid routes | CRITICAL | LAUNCH | API, Serverless, AI features |
| [SEC-API-125](#sec-api-125-set-prices-and-plans-from-the-server-catalog) | Set prices and plans from the server catalog | BLOCKER | LAUNCH | SaaS, API, Backend, Mobile |
| [SEC-API-126](#sec-api-126-grant-entitlements-only-from-verified-server-side-signals) | Grant entitlements only from verified server side signals | BLOCKER | LAUNCH | SaaS, API, Backend, Mobile |
| [SEC-API-127](#sec-api-127-match-provider-payment-details-to-the-order-before-granting) | Match provider payment details to the order before granting | CRITICAL | LAUNCH | SaaS, API, Backend, Mobile |
| [SEC-API-128](#sec-api-128-grant-each-payment-at-most-once-in-one-transaction) | Grant each payment at most once, in one transaction | CRITICAL | LAUNCH | API, Backend, Database |
| [SEC-API-132](#sec-api-132-authenticate-revenuecat-webhook-requests) | Authenticate RevenueCat webhook requests | BLOCKER | LAUNCH | API (RevenueCat), Mobile |
| [SEC-API-133](#sec-api-133-verify-apple-notifications-with-the-full-certificate-chain) | Verify Apple notifications with the full certificate chain | BLOCKER | LAUNCH | API (Apple App Store), Mobile |
| [SEC-API-134](#sec-api-134-authenticate-google-play-rtdn-push-requests) | Authenticate Google Play RTDN push requests | BLOCKER | LAUNCH | API (Google Play), Cloud, Mobile |
| [SEC-API-135](#sec-api-135-never-grant-production-entitlements-from-sandbox-events) | Never grant production entitlements from sandbox events | CRITICAL | LAUNCH | API, Backend, Mobile |
| [SEC-API-137](#sec-api-137-collect-card-data-only-through-the-providers-hosted-checkout) | Collect card data only through the provider's hosted checkout | CRITICAL | LAUNCH | SaaS, Web, Mobile, API |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Object level authorization | AUTH.md, DATABASE-SECURITY.md, BACKEND-SECURITY.md, DATA-PROTECTION.md | None | None in this document |
| Function level authorization, including a documented rule per endpoint that tests check | AUTH.md | None | None in this document |
| Resource exhaustion (payload size, pagination, query cost, timeouts, expensive operations) | BACKEND-SECURITY.md, AI-SECURITY.md, OBSERVABILITY.md, INFRASTRUCTURE-SECURITY.md | None | SEC-API-114 (more in Pro edition) |
| Webhooks | SECRETS.md, OBSERVABILITY.md, BACKEND-SECURITY.md | None | SEC-API-101, SEC-API-132, SEC-API-133, SEC-API-134, SEC-API-135 (more in Pro edition) |
| Replay attacks | AUTH.md | None | SEC-API-128 (more in Pro edition) |
| API1:2023 Broken Object Level Authorization | AUTH.md, DATABASE-SECURITY.md, BACKEND-SECURITY.md | None | None in this document |
| API5:2023 Broken Function Level Authorization | AUTH.md | None | SEC-API-001 |
| API7:2023 Server Side Request Forgery | BACKEND-SECURITY.md | None | None in this document |
| Payments and entitlements | None | None | SEC-API-125, SEC-API-126, SEC-API-127, SEC-API-137 (more in Pro edition) |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-MOBILE | Is a mobile build shipped, in a store, or handed to testers in this release? | Check that no app.json, eas.json, ios or android folder, or expo or react-native dependency exists in any workspace, and that no store listing or TestFlight build exists. Record what was checked, or record the owner's written answer. A mobile scaffold counts as No only if it is not deployed and not reachable by real users at the audited commit; a release scope that leaves a live app out does not make the answer No. | SEC-API-132, SEC-API-133, SEC-API-134 (more in Pro edition) |
| GATE-PAYMENTS | Does the product take payments or grant paid entitlements through a payment provider or an app store? | Search package.json and the source for paystack, paddle, stripe, flutterwave, revenuecat, apple or google billing, and for a checkout or entitlement route. Any handler that changes a plan, credit, role or entitlement is a payment path, whatever the payment provider is called. Record the commands, the number of files searched and that nothing was found, or record the owner's written answer that no money is taken through the product. | SEC-API-125, SEC-API-126, SEC-API-127, SEC-API-128, SEC-API-132, SEC-API-133, SEC-API-134, SEC-API-135, SEC-API-137 (more in Pro edition) |
<!-- hullproof:gates:end -->

The OWASP API Security Top 10 2023 is the organising frame for the rows named with an API number. Each requirement is listed once, under the most specific row.

---

## API surface

### SEC-API-001: Authenticate every non public endpoint

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API, Backend, Serverless, SaaS |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, AUTOMATED TEST, STATIC ANALYSIS |

**Requirement.** Every endpoint that reads non public data or changes state, including every Server Action, Route Handler, edge function, cron route and internal service route, MUST reject a request that carries no valid user session, service credential or provider signature, before any data access or side effect.

**Why.** Server Actions and Route Handlers accept direct POST requests whether or not the UI links to them, and cron or internal routes are public URLs unless they check a secret. Escape found over 400 public state changing endpoints in AI built apps. An unauthenticated write or read endpoint is a direct path to data loss or disclosure.

**Implementation.**
- Make the authentication check the first statement in each handler, through one shared helper that returns the verified identity or throws.
- Routes called by machines (cron, queues, internal services) check a dedicated secret or signed token, compared in constant time, never a user agent or IP address.
- Keep a short, reviewed allowlist of intentionally public endpoints (health check, public catalog, signed webhooks); everything else is authenticated by default.
- Default stack: treat every `"use server"` function and every `route.ts` export as a public endpoint. Vercel Cron routes check `Authorization: Bearer` against a random `CRON_SECRET`. Job platforms (Vercel Cron, Inngest, QStash) are covered in detail by SEC-API-057 in BACKEND-SECURITY.md.

**Verify.**
1. Capture every API request the app makes (browser devtools or a proxy) and list every Server Action and Route Handler from the code.
2. Replay each one with no cookie, no `Authorization` header and no secret; every non allowlisted endpoint must return 401 or 403 with no data and no state change.
3. Run a Semgrep rule that flags `"use server"` functions and route handlers with no call to the shared auth helper before data access.
4. Call each cron and internal route without its secret and with a wrong secret; expect 401.

**Evidence.** Endpoint list with the public allowlist; passing unauthenticated replay test suite; Semgrep report with zero unresolved findings.

**Exceptions.** None. Scope clarifications: a data API table or RPC function exposed to client roles counts as an endpoint for this requirement, and its row level policy or function body is the authentication check. A finding may be rated below BLOCKER only with the evidence written in the finding, as STANDARD.md Severity describes.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1, v5.0.0-8.3.1 [SRC-010]; OWASP ASVS 5.0.0 v5.0.0-13.2.1 (L2, promoted to LAUNCH for machine called routes) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-02 [SRC-186]; OWASP API Security Top 10 2023 API2:2023, API5:2023 [SRC-021]; Next.js Data Security guide, Server Actions are public endpoints [SRC-078]; Next.js Authentication guide, Route Handlers [SRC-080]; Vercel Cron Jobs, CRON_SECRET [SRC-164]; Escape, State of Security of Vibe Coded Apps (over 400 public state changing endpoints) [SRC-007].

**AI Agent Instruction.** When you create or edit any Server Action, Route Handler, edge function, cron route or internal endpoint, call the shared auth helper before any read, write or external call. Never assume an endpoint is private because no page links to it. If an endpoint must be public, stop and ask for it to be added to the public allowlist with a reason. Never remove or bypass an existing auth check to make a feature work; report the blocker instead.

---

## Webhooks

### SEC-API-101: Verify the webhook sender before processing

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API, Backend, Serverless |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, AUTOMATED TEST, STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Every webhook route MUST authenticate each request with the provider's documented mechanism (HMAC signature over the raw request body, asymmetric JWS, or signed OIDC token) before it parses, stores or acts on the payload, and MUST reject the request with a 4xx and no side effect when verification fails or the signature header is missing. The verifier MUST fail closed when its secret or public key is missing, empty or equal to a documented placeholder: in a deployed environment the application MUST refuse to start, or the route MUST return 5xx for every request, including one signed with an empty key.

**Why.** A webhook route is a public URL. Without sender verification anyone can post a forged "payment succeeded" or "subscription active" event and receive value. Verifying a parsed and reserialized body instead of the raw bytes makes verification fail on real events, which tempts developers to switch it off.

**Implementation.**
- Read the raw request body as bytes or text before any JSON parsing, and pass those exact bytes to the verifier.
- Use the provider's official SDK verifier where one exists. Load the signing secret or key from a server only environment variable.
- Where a provider offers both a static shared token and a payload signature, use the signature. Default stack: Flutterwave v4 `flutterwave-signature` (HMAC SHA256) over the v3 `verif-hash` static token.
- Default stack: Next.js Route Handlers read the body with `await request.text()`; never call `request.json()` before verification.
- Never read the signing secret with an empty string fallback. Check at startup that it is present and is not a placeholder. In Node.js, `crypto.createHmac('sha256', '')` and an empty Buffer key both return a digest (checked on v22.23.2), while an undefined key throws, and the Node.js documentation does not say what an empty key does [SRC-370]. A fallback such as `process.env.SECRET ?? ''` therefore turns a missing variable into a key the attacker knows, so a blank variable accepts forged events.
- An IP allowlist MAY be added as a second layer. It never replaces signature verification.
- Default stack (checked 2026-10-03): the Stripe Node library requires the raw, unparsed body exactly as received. In a Next.js Route Handler: `const body = await request.text(); const event = stripe.webhooks.constructEvent(body, request.headers.get("stripe-signature")!, secret);`.

**Verify.**
1. Send an unsigned request, a request with a wrong signature, and a correctly signed request whose body has one byte changed. Each must return 4xx and create no database row, queue job or entitlement.
2. Send a valid signed event from the provider's test mode or CLI. It must be accepted.
3. Run Semgrep for `JSON.stringify(req.body)`, `request.json()` or framework body parsers inside webhook verification code.
4. Review every route registered with a provider and confirm verification runs as the first operation in each.
5. In a staging deploy, unset and then blank the verification secret. The application must refuse to start or the route must reject every request, including one signed with an empty key.

**Evidence.** Passing automated test file covering the four negative cases and one positive case per webhook route; Semgrep report with no findings on webhook code.

**Exceptions.** None. Fail closed clarification: reading the body into a parser before verification is not a finding when the parse uses a bounded schema (maximum size, strict types), any parse failure returns 4xx with no side effect, and no parsed value is stored or acted on until verification passes. A provider whose documented signature covers fields of the parsed payload instead of the raw bytes is verified with that provider's verifier on the bounded parse, under the same conditions. Not applicable when the product has no webhook route; record the search that shows it, for example a grep for `webhook` over route and function folders that returns no route, and an empty webhook endpoint list in each provider dashboard.

**References.** OWASP Top 10:2025 A08:2025 (CWE-345) [SRC-020]; OWASP API Security Top 10 2023 API10:2023 [SRC-021]; Stripe Webhooks: Signature verification [SRC-086]; Paystack Webhooks: Signature validation, Raw body [SRC-088]; Flutterwave Webhooks: v4 HMAC signature [SRC-089]; Paddle Verify webhook signatures: Signature scheme, Raw body [SRC-090]; Node.js crypto.createHmac [SRC-370].

**AI Agent Instruction.** When you create or change a webhook route, make signature verification over the raw body the first statement that touches the request, and write the negative tests in Verify step 1 alongside it. Never parse the body before verifying, never add a flag, environment switch or `try/catch` that lets an event with no valid signature through, and never remove or bypass an existing verification step to make a test pass. If you cannot find the provider's verification method, stop and report it instead of shipping a route with no signature check.

---

## Rate Limiting

### SEC-API-114: Fail closed when the limiter is unavailable on paid routes

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | API, Serverless, AI features |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW |

**Requirement.** Every route that calls a paid service (AI models, SMS, paid email or data APIs) or grants value MUST reject the request when the rate limiter or usage budget check cannot return an explicit allow, including on timeout, connection error or thrown error, and MUST NOT make the paid call in that case.

**Why.** Upstash Ratelimit allows requests when Redis does not answer within its timeout. On ordinary routes that keeps the app available, but on paid routes it removes the cost ceiling during exactly the conditions an attacker can create or exploit.

**Implementation.**
- Treat any limiter or budget result other than an explicit allow as a denial on paid routes.
- Default stack: check the `reason` field returned by Upstash and treat a timeout as a denial on paid routes, returning 503 with a retry message. Upstash allows the request after its timeout, 5 seconds by default.
- Do not wrap the limiter in a `try/catch` that continues to the paid call on error.
- Keep fail open behaviour only on routes with no paid call and no value grant, and record which ones.
- Alert when the limiter starts returning timeouts (see OBSERVABILITY.md).
- Default stack (checked 2026-10-03): `@upstash/ratelimit` lets the request through when the Redis call exceeds its `timeout` option (5 seconds by default) and returns `reason: "timeout"`. Code: `const { success, reason } = await ratelimit.limit(id); if (!success || reason === "timeout") return new Response(null, { status: 503 });`. Setting a shorter `timeout` shortens the window but does not close it.

**Verify.**
1. For each paid route, including every AI model route, mock the limiter to time out and then to throw, and call the route. The paid service must not be called and the route must return a non 2xx status.
2. Review each paid route for the timeout check and for any error path that continues to the paid call.
3. Repeat step 1 for the login, signup, password reset and OTP limiters. A limiter that allows the request on timeout removes the brute force ceiling on those routes. Report it as a finding under this requirement unless the decisions log records the sign in limiter exception described in a Pro edition requirement. SEC-LOG-019 in OBSERVABILITY.md owns authentication, validation and signature checks that fail open; a Pro edition requirement in BACKEND-SECURITY.md is the general rule for every other check.

**Evidence.** Passing fail closed test per paid route.

**Exceptions.** None by default. A paid route may fail open only with written risk acceptance that names an owner, a compensating control and an expiry date. Routes with no paid call and no value grant are out of scope.

**References.** OWASP ASVS 5.0.0 v5.0.0-16.5.3 (L2, promoted to LAUNCH: guards payment and paid service costs), v5.0.0-2.4.1 (L2, promoted) [SRC-010]; OWASP Top 10 for LLM Applications 2026 LLM06:2026 [SRC-025]; Upstash Ratelimit: Timeout fails open [SRC-127].

**AI Agent Instruction.** When you add a limiter or budget check to a route that spends money or grants value, including any AI model route, handle every timeout or error result as a denial and add a test for it. Flag existing code that continues on limiter failure as a finding. Never change a fail closed path to fail open to fix flaky tests or timeouts.

---

## Payments

### SEC-API-125: Set prices and plans from the server catalog

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Mobile |
| Automation | PARTIAL |
| Verification method | MANUAL TEST, STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Checkout and purchase code MUST take price, currency, plan, quantity limits and discount from the server's own catalog, keyed by a product or price identifier, and MUST ignore any amount, currency or discount value sent by the client.

**Why.** If the client sends the amount, an attacker edits the request and buys the top plan for a fraction of its price or for nothing.

**Implementation.**
- The client sends only a product or price ID and, where allowed, a quantity. The server looks up everything else.
- Validate the request with a schema that has no amount, currency or discount fields, so extra fields are rejected.
- Mobile in app purchases: the store sets the price, but the server still maps store product IDs to entitlements from its own catalog.
- Discount codes are validated on the server against stored rules.

**Verify.**
1. Using provider test keys only, tamper with price, plan, currency and discount in the checkout request. The created checkout must use catalog values.
2. Run Semgrep for checkout code reading `amount`, `price`, `currency` or `discount` from the request body.

**Evidence.** Manual test record with tampered requests; clean Semgrep report.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-2.2.2 (L1), v5.0.0-15.3.3 (L2, promoted) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-BUSL-02 [SRC-186]; OWASP Cheat Sheet Series: Mass Assignment [SRC-030]; Google Play Billing: Sensitive logic on backend [SRC-177].

**AI Agent Instruction.** When you build checkout, accept only an identifier from the client and look up price and currency on the server. Never pass a client supplied amount to a payment provider, even temporarily. If an existing flow does this, stop and report it as a BLOCKER.

---

### SEC-API-126: Grant entitlements only from verified server side signals

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Mobile |
| Automation | PARTIAL |
| Verification method | MANUAL TEST, STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Plans, credits and paid features MUST be granted only from a webhook that passed SEC-API-101 or from a server side call to the payment provider's API, and MUST NOT be granted from a client redirect, success page, query parameter or purchase result reported by the mobile app.

**Why.** Success URLs and client reported purchases can be visited or forged without paying. Granting from them hands out paid features for free.

**Implementation.**
- Write entitlement rows only from the webhook handler or a server verify function.
- Default stack: RevenueCat, call `GET /subscribers` after any webhook and store that state.
- Default stack: Google Play, after any RTDN or app report, call `purchases.subscriptionsv2.get` or `purchases.products.get` with the `purchaseToken` before granting; the notification itself carries no purchase state.
- Default stack: Apple, read state from the verified signed transaction (SEC-API-133) or the App Store Server API.
- Default stack: Supabase RLS on entitlement tables denies inserts and updates from client roles.
- Owned by SEC-DB-033 in DATABASE-SECURITY.md for this root cause (Client writable privileged columns); report one finding.

**Verify.**
1. Visit the checkout success URL without paying, and post a fake purchase result from the mobile client. Nothing must be granted.
2. Run Semgrep for writes to entitlement tables outside the webhook and verify paths.
3. Confirm client roles cannot write entitlement tables (RLS test).

**Evidence.** Manual test record; Semgrep report; RLS test output.

**Exceptions.** None.

**References.** OWASP Top 10:2025 A08:2025 [SRC-020]; OWASP WSTG 4.2 WSTG-v42-BUSL-06 [SRC-186]; Flutterwave Webhooks: Re-query before value [SRC-089]; RevenueCat Webhooks: Sync by re-query [SRC-173]; Google Play RTDN: Call the API after RTDN [SRC-176]; Google Play Billing: Verify before grant [SRC-177]; Apple App Store Server Notifications: Recovery [SRC-174].

**AI Agent Instruction.** When you implement a purchase flow, put the grant in the webhook handler or a server verify function and nowhere else. Never unlock features on the success page or from a client SDK callback without a server check. Refuse requests to "temporarily" grant from the client.

---

### SEC-API-127: Match provider payment details to the order before granting

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Mobile |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW |

**Requirement.** Before granting value, the server MUST confirm that the provider reports a completed (not pending) payment whose amount, currency and reference match the order it created, or for store purchases whose product ID, bundle or package name and environment match what it expects.

**Why.** A real but smaller payment, a payment in a cheaper currency, a pending payment, or a valid purchase for another product can otherwise unlock the full plan.

**Implementation.**
- Store the expected amount, currency and reference when creating the order, and compare on grant.
- Default stack: Flutterwave and Paystack, re-query the transaction by reference and compare.
- Default stack: Google Play, do not grant while the purchase state is PENDING.
- Default stack: Apple, compare bundle ID and environment from the verified payload.

**Verify.**
1. In tests, deliver verified events with a lower amount, a different currency, a pending state and a different product ID. None must grant.
2. Deliver a verified event whose state is completed and whose amount, currency and reference match the order. It must grant exactly once.
3. Deliver a verified event whose provider metadata or client reference names a different plan, user or amount than the stored order, and confirm the grant follows the stored order. Grep the grant code for reads of provider metadata or custom fields that decide what is granted.

**Evidence.** Passing mismatch tests.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-2.3.1 (L1) [SRC-010]; OWASP API Security Top 10 2023 API10:2023 [SRC-021]; Flutterwave Webhooks: Re-query before value [SRC-089]; Google Play Billing: Pending state [SRC-177]; Apple app-store-server-library-node: SignedDataVerifier [SRC-175].

**AI Agent Instruction.** When you write the grant step, compare every field listed in the requirement against the stored order and add a test per mismatch. Do not grant on "status success" alone.

---

### SEC-API-128: Grant each payment at most once, in one transaction

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | API, Backend, Database |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW |

**Requirement.** Each payment or purchase MUST grant value at most once, with the record of the payment's unique identifier and the grant written in the same database transaction under a uniqueness constraint.

**Why.** Retried webhooks, a webhook racing a server verify call, or a reused purchase token can otherwise grant credits or plans twice.

**Implementation.**
- Use a unique index on the provider's payment identifier and insert it in the same transaction as the credit or plan change; on conflict, grant nothing.
- Default stack: Google Play, store every `purchaseToken`, reject reuse, and never key on `orderId` because some purchases have none.
- Default stack: Supabase, run the grant in one Postgres function so the insert and grant commit together.

**Verify.**
1. Deliver the same verified payment twice, and concurrently through the webhook and the verify path. Exactly one grant must result.
2. Reuse a Google `purchaseToken` in a test. It must be refused.

**Evidence.** Passing duplicate and race tests; migration showing the unique index.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-2.3.3, v5.0.0-2.3.4 (L2, promoted to LAUNCH: guards payments) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-BUSL-04 [SRC-186]; Stripe Webhooks: Duplicate events [SRC-086]; Flutterwave Webhooks: Be idempotent [SRC-089]; Google Play Billing: Token uniqueness [SRC-177].

**AI Agent Instruction.** When you write a grant, put the dedupe insert and the grant in one transaction or one database function. Never check "already granted" with a separate read before writing, since two requests can both pass the read.

---

### SEC-API-132: Authenticate RevenueCat webhook requests

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API (RevenueCat), Mobile |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST, CODE REVIEW |

**Requirement.** Projects using RevenueCat webhooks MUST authenticate every webhook request, either by verifying the HMAC signature and timestamp RevenueCat sends, or by configuring an authorization header value in RevenueCat and rejecting any request whose `Authorization` header does not match it in a constant time comparison. The authentication MUST be configured before the webhook can act on its first event, in every environment where it can.

**Why.** RevenueCat treats the authorization header as optional. Without any authentication the webhook URL accepts any request, so anyone who finds it can post a fake purchase event, flood the endpoint or trigger state changes. The grant itself must still come from a RevenueCat API call (SEC-API-126), which is meant to stop a forged event from granting access. This is rated BLOCKER for two reasons. Payments is a protected class, so a failure here can never be accepted as a risk. And an open webhook leaves a single check between the internet and a free entitlement: any gap in that check, such as a lookup that trusts the event body, a missing amount match (SEC-API-127) or a replay (a Pro edition requirement), becomes a direct path to free paid access with nothing in front of it. Authentication removes forged events from the handler altogether and stops floods of fake events that cost lookups, writes and entitlement moves. Both checks are required. The same level applies to the matching Google Play rule in SEC-API-134.

**Implementation.**
- Prefer HMAC signature verification where your RevenueCat plan offers it: it covers the body and a timestamp, so it also supports the stale event rule in a Pro edition requirement. Check the current RevenueCat webhook documentation for how to enable it.
- Otherwise generate a long random value, store it in a server environment variable, and set it as the authorization header value in the RevenueCat dashboard.
- Grant only after `GET /subscribers` (SEC-API-126). Use the Supabase user UUID as the App User ID, never an email, because subscription status is reachable through RevenueCat's public API.
- Handle `TRANSFER` events so entitlements move to the right account (a Pro edition requirement).

**Verify.**
1. Send a webhook request with no authentication and with a wrong one (a wrong header value, or a body with an invalid or stale signature). Each must be rejected with no side effect.
2. Confirm the authentication is configured in the RevenueCat dashboard for every environment.
3. In staging, send a forged purchase event for a test user that carries the correct authentication but names a purchase that does not exist. Confirm no entitlement is granted, which shows SEC-API-126 holds.

**Evidence.** Passing negative tests; dashboard configuration record.

**Exceptions.** None when RevenueCat webhooks are used.

**References.** OWASP Top 10:2025 A08:2025 [SRC-020]; OWASP ASVS 5.0.0 v5.0.0-11.2.4 (promoted) [SRC-010]; RevenueCat Webhooks: Authorization header, HMAC signing, App User IDs [SRC-173].

**AI Agent Instruction.** When you add a RevenueCat webhook handler, authenticate the request first (signature check or a constant time compare of the authorization header) and add the negative tests. If neither is configured, stop and tell the developer; do not ship the handler without it.

---

### SEC-API-133: Verify Apple notifications with the full certificate chain

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API (Apple App Store), Mobile |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW |

**Requirement.** App Store Server Notifications MUST be received in version 2 format and each `signedPayload`, `signedTransactionInfo` and `signedRenewalInfo` MUST be verified as a JWS whose `x5c` chain validates to Apple's root certificate, with the expected bundle ID and environment, before any field is used.

**Why.** Decoding the JWS without validating its chain accepts payloads anyone can sign. Skipping the bundle ID or environment check lets a payload from another app or from sandbox be replayed into production.

**Implementation.**
- Default stack: use Apple's official library (`SignedDataVerifier` in app-store-server-library-node) with Apple root certificates from the Apple PKI site, the bundle ID, the environment and, for production, the App Apple ID.
- Do not hand write JWS verification. Do not use a generic JWT decode function.
- Version 1 notifications are deprecated; configure V2 in App Store Connect.

**Verify.**
1. Send a payload signed with a self generated certificate chain. It must be rejected.
2. Send a valid sandbox payload to the production handler. It must be rejected or ignored (SEC-API-135).
3. Review the verifier configuration for bundle ID and environment.

**Evidence.** Passing negative tests; code review note.

**Exceptions.** None when Apple notifications are consumed directly. Not applicable when only RevenueCat receives Apple events.

**References.** OWASP Top 10:2025 A08:2025 [SRC-020]; Apple App Store Server Notifications: signedPayload JWS, Certificate chain, Nested JWS, Use V2 [SRC-174]; Apple app-store-server-library-node: SignedDataVerifier [SRC-175].

**AI Agent Instruction.** When you consume Apple notifications, use the official verifier with bundle ID and environment set. Never decode the payload with a JWT library that skips chain validation, and never read fields before verification succeeds.

---

### SEC-API-134: Authenticate Google Play RTDN push requests

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API (Google Play), Cloud, Mobile |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST, CODE REVIEW |

**Requirement.** A Pub/Sub push endpoint for Google Play Real time Developer Notifications MUST have push authentication enabled and MUST reject requests whose Google signed OIDC token fails signature validation or whose `email` and `aud` claims do not equal the configured push service account and audience.

**Why.** Without push authentication the RTDN endpoint is an unauthenticated public URL. Attackers can flood it or trigger state changes if any handler logic trusts the message before calling the Play Developer API. This is rated BLOCKER for the same reasons as the RevenueCat rule in SEC-API-132. Payments is a protected class, so a failure can never be accepted as a risk. The Play Developer API call (SEC-API-126) is the second check, and with push authentication missing it is the only check between the internet and a free entitlement, so any gap in the handler becomes a direct path to free paid access. Push authentication removes forged messages and floods from the handler.

**Implementation.**
- Enable authentication on the push subscription and set a dedicated service account and audience.
- Validate the token with a Google library; the issuer is `https://accounts.google.com`.
- Grant only `google-play-developer-notifications@system.gserviceaccount.com` the Publisher role on the topic, and keep `iam.serviceAccounts.actAs` on the push service account narrow.
- The grant itself still comes from the Play Developer API (SEC-API-126).

**Verify.**
1. Post to the endpoint with no token, an expired token, and a valid Google token with a different audience. Each must be rejected.
2. Export the topic IAM policy and push subscription settings.

**Evidence.** Passing negative tests; IAM and subscription configuration export.

**Exceptions.** Pull subscriptions, which have no public endpoint. Record the subscription type.

**References.** OWASP Top 10:2025 A08:2025 [SRC-020]; Google Cloud Pub/Sub Authentication for push subscriptions: Enable push auth, Validate the JWT, actAs control [SRC-178]; Google Play RTDN: Publisher grant, Push or pull [SRC-176].

**AI Agent Instruction.** When you build an RTDN push handler, validate the OIDC token and its `email` and `aud` claims first, and then call the Play Developer API before changing any entitlement. Never treat the notification body as proof of purchase.

---

### SEC-API-135: Never grant production entitlements from sandbox events

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | API, Backend, Mobile |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW |

**Requirement.** Production entitlement code MUST check the environment of every purchase event or verified transaction and MUST NOT grant production access from sandbox or test events. Test and live keys, webhook endpoints and signing secrets MUST be separate per environment, so a sandbox event cannot be verified with a production key.

**Why.** RevenueCat and Apple can send sandbox and production events to the same URL, and one customer can hold both. Sandbox purchases cost nothing, so accepting them in production gives paid access away.

**Implementation.**
- Default stack: RevenueCat events carry `environment` (`SANDBOX` or `PRODUCTION`); filter integrations by environment where possible and check the field in code.
- Default stack: Apple, set the expected environment in the verifier (SEC-API-133).
- Web providers: keep test and live keys and webhook endpoints separate per environment (a Pro edition requirement).

**Verify.**
1. Deliver a verified sandbox event to the production handler. No production entitlement must be granted.
2. Grep the entitlement code for the environment check (for example the RevenueCat `environment` field or Stripe `livemode`) and confirm it runs before every grant path.

**Evidence.** Passing test.

**Exceptions.** Internal test accounts that are deliberately granted access; record them by user ID.

**References.** Hullproof original control, derived from RevenueCat Webhooks: Environment [SRC-173] and Apple App Store Server Notifications: Environments [SRC-174]; closest normative anchor OWASP ASVS 5.0.0 v5.0.0-2.2.2 (L1) [SRC-010].

**AI Agent Instruction.** When you write mobile purchase handling, read and check the environment field before granting. Never treat a missing environment value as production.

---

### SEC-API-137: Collect card data only through the provider's hosted checkout

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, Mobile, API |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, STATIC ANALYSIS |

**Requirement.** Card details MUST be entered only on the payment provider's hosted page, overlay or provider served iframe, or in the app store's purchase sheet, and the app's own pages, servers, databases and logs MUST NOT receive card numbers or security codes.

**Why.** Once card data passes through the app, the whole system falls into a much larger PCI DSS scope that a small team cannot meet. Fully outsourcing card handling is what makes the short SAQ A self assessment possible.

**Implementation.**
- Default stack: Stripe Checkout, Paystack, Flutterwave and Paddle hosted checkout or overlays; Apple and Google purchase sheets for in app purchases.
- Do not build custom card input fields that post to your own server.
- Ask the payment provider or acquirer which SAQ applies and record the answer (a Pro edition requirement).

**Verify.**
1. Search the code for form fields named like card number, CVC or expiry, and for request schemas containing them.
2. Review the checkout flow and confirm card entry happens on a provider domain or provider iframe.

**Evidence.** Code search output; checkout flow review note.

**Exceptions.** Teams that choose full PCI DSS validation must record the decision and the validated scope.

**References.** PCI SSC FAQ 1588 and SAQ A updates (PCI DSS v4.0.1 SAQ A r1): SAQ A scope [SRC-179]; OWASP ASVS 5.0.0 v5.0.0-16.2.5 (L2, promoted) [SRC-010].

**AI Agent Instruction.** When you build payment UI, use the provider's hosted checkout or provider iframe only. Refuse to build card input fields that reach the project's own server, and report any you find.
