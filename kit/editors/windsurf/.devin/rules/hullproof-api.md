---
trigger: glob
globs: **/api/**, **/routes/**, **/actions/**, **/*action*.*, **/server/**, **/webhooks/**, **/functions/**, **/billing/**, **/payments/**, **/checkout/**, **/uploads/**, **/storage/**
---
# Hullproof: APIs, backend code, webhooks, payments and uploads

Advisory text for Windsurf and Devin, not enforced. Read API-SECURITY.md and BACKEND-SECURITY.md (uploads: DATA-PROTECTION.md) in docs/hullproof/ before editing these files. Start at the Coverage map and read only the requirement you need. The stage comes from docs/security/STAGE.md. Every BLOCKER applies from LAUNCH.

## Before you write code in this area

1. LAUNCH. Authenticate every non public endpoint and server action, and authorize inside the handler (SEC-API-001, SEC-AUTHZ-002).
2. LAUNCH. Validate body, query and headers against a server side schema before other logic, and reject unknown fields (SEC-AUTHZ-004).
3. LAUNCH. Parameterize every query, build no shell command from untrusted data, and never evaluate untrusted data or model output as code (SEC-API-017, SEC-API-020, SEC-API-021).
4. LAUNCH. Webhooks: verify the sender before parsing the payload (SEC-API-101), reject stale deliveries and process each event once.
5. LAUNCH. Payments: prices and plans come from the server catalog (SEC-API-125), entitlements only from verified server side signals (SEC-API-126), each payment is granted once in one transaction (SEC-API-128), no production grants from sandbox events (SEC-API-135), card data only through the provider hosted checkout (SEC-API-137).
6. LAUNCH. Guard user and model supplied URLs before the server connects (SEC-API-035). Uploads: private buckets, signed URLs after an authorization check, and never served as active content from the app origin (SEC-DATA-019, SEC-DATA-020, SEC-API-045).
7. LAUNCH. Rate limit authentication endpoints and every public or paid route, and fail closed when the limiter is down on paid routes (SEC-API-114).
8. GROWTH adds. Sign outbound webhooks with a secret per endpoint, give each integration its own scoped credential, make jobs safe to run twice.
9. Return generic errors to clients and log detail on the server without secrets or tokens.

## Refuse

- Parsing a webhook body before the signature check.
- Granting an entitlement from a client redirect.
- Trusting a price, plan, user ID or role sent by the client.
- Building SQL or shell commands from strings that contain input.

If a control blocks you, stop and report it with the ASSUMPTION, VERIFIED or SUSPECTED labels and a severity from docs/hullproof/STANDARD.md.
