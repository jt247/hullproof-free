# Frontend Security

| Field | Value |
|-------|-------|
| Domain codes | SEC-WEB |
| Topics covered | Output Encoding, Frontend Security, Cookies, CORS, CSRF, XSS |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers controls that run in or for the browser: encoding output for its context, security headers and HSTS, framing, cookies, cross origin reads, forged cross site requests, and script injection, including how model output is rendered. Session lifetime, logout and token storage rules live in [AUTH.md](AUTH.md). Secrets in client bundles are owned by [SECRETS.md](SECRETS.md). File uploads, including SVG and download serving, are in [BACKEND-SECURITY.md](BACKEND-SECURITY.md). Other uses of model output are in [AI-SECURITY.md](AI-SECURITY.md). TLS is in [DATA-PROTECTION.md](DATA-PROTECTION.md), and WebViews in [MOBILE-SECURITY.md](MOBILE-SECURITY.md).

**Default stack cookie exception.** `@supabase/ssr` writes session cookies that browser code can read, so the default stack cannot meet the session cookie HttpOnly rule in SEC-AUTH-021 ([AUTH.md](AUTH.md)) as shipped. A project may record a stack exception at LAUNCH only when every compensating control listed in SEC-AUTH-021 is in place. The exception covers Supabase session cookies only; every other cookie follows SEC-WEB-016. The exception is recorded in the project's security decisions log and is revisited when Supabase supports HttpOnly session cookies.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 4 of the 39 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-WEB-022](#sec-web-022-choose-cors-origins-from-an-exact-allowlist) | Choose CORS origins from an exact allowlist | CRITICAL | LAUNCH | Web, API, Serverless |
| [SEC-WEB-026](#sec-web-026-protect-cookie-authenticated-state-changes-against-forgery) | Protect cookie authenticated state changes against forgery | CRITICAL | LAUNCH | Web, API, SaaS |
| [SEC-WEB-031](#sec-web-031-list-and-justify-every-raw-html-sink) | List and justify every raw HTML sink | CRITICAL | LAUNCH | Web, SaaS, AI features |
| [SEC-WEB-032](#sec-web-032-sanitize-user-supplied-html-with-a-maintained-library) | Sanitize user supplied HTML with a maintained library | CRITICAL | LAUNCH | Web, SaaS |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| XSS (reflected, stored, DOM) | AUTH.md | None | SEC-WEB-031, SEC-WEB-043 |
| Output encoding | None | None | SEC-WEB-003, SEC-WEB-004, SEC-WEB-005 |
| Content Security Policy | None | None | SEC-WEB-008, SEC-WEB-042 |
| CSRF | None | None | SEC-WEB-025, SEC-WEB-026, SEC-WEB-027, SEC-WEB-028, SEC-WEB-029, SEC-WEB-030 |
| CORS | None | None | SEC-WEB-022, SEC-WEB-023, SEC-WEB-040, SEC-WEB-041 |
| Cookies (all attributes) | AUTH.md | None | SEC-WEB-015, SEC-WEB-016, SEC-WEB-017, SEC-WEB-019, SEC-WEB-020, SEC-WEB-021 |
| Clickjacking and framing | None | None | SEC-WEB-038 |
| Security headers | DATA-PROTECTION.md, AUTH.md | None | SEC-WEB-009, SEC-WEB-010, SEC-WEB-011, SEC-WEB-036 |
| Third party scripts and Subresource Integrity | DEPENDENCIES.md | None | SEC-WEB-035 |
| Client side storage of tokens and personal data | AUTH.md | None | SEC-WEB-013 |
| Secrets in client bundles | SECRETS.md, AI-SECURITY.md | None | None in this document |
| Source maps in production | SECRETS.md, OBSERVABILITY.md | None | SEC-WEB-039 |
| Open redirects | AUTH.md | None | SEC-WEB-002 |
| Rendering model output | None | None | SEC-WEB-001, SEC-WEB-033, SEC-WEB-034 |
| postMessage and cross window messaging | None | None | SEC-WEB-014, SEC-WEB-037 |
| Dependency and framework versions in the browser | DEPENDENCIES.md | None | SEC-WEB-032 |
| WebSocket origin checks | None | None | SEC-WEB-024 |
<!-- hullproof:coverage-map:end -->

---

## CORS

### SEC-WEB-022: Choose CORS origins from an exact allowlist

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Web, API, Serverless |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, STATIC ANALYSIS, CONFIG REVIEW |

**Requirement.** `Access-Control-Allow-Origin` on any route that returns private data or accepts credentials MUST be a fixed origin or an origin selected by exact string match against a per environment allowlist of literal origins, and MUST NOT be copied from the request `Origin` without that match or set to `*`. The allowlist MUST NOT be built from a regular expression, wildcard, prefix, suffix or substring test, and MUST NOT contain an origin on a hosting domain where anyone can register a name.

**Why.** Reflecting any origin with `Access-Control-Allow-Credentials: true` lets every website a user visits read that user's private API responses. Suffix or substring checks let `app.example.evil.com` pass.

**Implementation.**
- Keep the allowlist in configuration per environment (production, preview, development) and compare full origin strings exactly.
- Never allow the literal origin `null`.
- Vercel preview deployments: add each preview origin the team needs explicitly, or use a single fixed preview alias; never allow a whole platform domain pattern. A preview API that must accept any preview origin serves no credentials. This rule is Hullproof original, since no researched source covers preview origins.
- Apply the same rule to Supabase Edge Functions and storage bucket CORS settings.

**Verify.**
1. For every API route, `curl -sI -H 'Origin: https://evil.example'`, `-H 'Origin: null'`, a suffix lookalike and a prefix lookalike of the real origin, and a host under each shared hosting domain the project uses (for example a name registered on the preview platform); fail if the origin is echoed or `*` is returned on a private route.
2. Run Semgrep for `Access-Control-Allow-Origin` set from `req.headers.origin` or `request.headers.get('origin')` without an exact allowlist lookup. Then search the CORS code for regular expressions and for prefix, suffix and substring tests (`startsWith`, `endsWith`, `includes`, `match`, `test`) applied to the origin; any hit fails unless it is an exact lookup in the allowlist.
3. For each route claimed as bearer only, send the request with a valid session cookie and no `Authorization` header; it must return 401 or 403.

**Evidence.** Saved probe output for each route; Semgrep report; the allowlist configuration per environment.

**Exceptions.** Fully public, unauthenticated, read only endpoints may use `*` without credentials; list each one. Any other exception needs an owner, a compensating control and an expiry date. Bearer only routes: a route that authenticates only with an `Authorization` bearer token, accepts no cookie or other ambient credential, and returns nothing that depends on the caller's network position may use `*` without `Access-Control-Allow-Credentials`, or an allowlist. Conditions: a request that carries a valid session cookie and no bearer token is rejected on that route, the route never sets a cookie, and the route list is recorded. Under these conditions a reflected or wildcard origin is a hygiene finding rated LOW. A route that fails any condition keeps the CRITICAL rating.

**References.** OWASP ASVS 5.0.0 v5.0.0-3.4.2 [SRC-010]; OWASP WSTG 4.2 WSTG-v42-CLNT-07 [SRC-186]; OWASP HTTP Headers Cheat Sheet, section Access-Control-Allow-Origin [SRC-041]; OWASP HTML5 Security Cheat Sheet, section Cross Origin Resource Sharing [SRC-030]; OWASP API Security Top 10 2023 API8:2023 (CWE-942) [SRC-021]; OWASP Top 10:2025 A02:2025 (CWE-942) [SRC-020].

**AI Agent Instruction.** Never reflect the request `Origin` or use `*` on a route with private data or credentials. When a CORS error blocks you, add the exact origin to the allowlist for that environment; never widen CORS to make it work.

---

## CSRF

### SEC-WEB-026: Protect cookie authenticated state changes against forgery

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Web, API, SaaS |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, CODE REVIEW |

**Requirement.** Every state changing request authenticated by a cookie MUST be rejected unless it passes one of: the framework's built in CSRF check, a synchronizer token, a signed double submit token, or a required custom request header or non simple content type that forces a CORS preflight and is checked on the server. A `SameSite` cookie attribute is defence in depth and is not one of these controls. This requirement is CRITICAL where a state changing route accepts a cookie session and the product holds money, personal data or administrator functions (Severity rule 9); a product with no cookie authenticated state changing route does not have this exposure.

**Why.** Browsers attach cookies to cross site requests, so without a check another site can submit actions as the signed in user. Requests that skip preflight (form posts with simple content types) reach handlers that only rely on CORS.

**Implementation.**
- Default stack: Next.js Server Actions accept only POST and compare `Origin` with the host; Route Handlers have no such check, so add one of the listed controls to every cookie authenticated Route Handler.
- For JSON APIs, require `Content-Type: application/json` or a custom header and reject requests without it.
- Do not use the naive (unsigned) double submit cookie pattern.
- Token based APIs that never read ambient cookies are out of scope, but still follow SEC-WEB-025.

**Verify.**
1. List every state changing route handler and exported Server Action from the framework route table (not from memory). From a page on another origin, submit each as a form post and as a `fetch` with `credentials: 'include'`, while signed in; every one must fail, and the same request from the app's own origin must succeed (positive control).
2. Send each request with `Content-Type: text/plain` and no custom header; it must be rejected.
3. Search server components and GET route handlers that perform a write with a cookie session against a bearer only API; none may exist.

**Evidence.** Cross origin test record or automated test results.

**Exceptions.** Does not apply to a route that authenticates only with an `Authorization` bearer token and never reads an ambient cookie. Webhook routes that verify a provider signature over the raw body (SEC-API-101; SEC-WEB-028 in FRONTEND-SECURITY.md) are exempt. No acceptance is available for any other case: a finding here is in the authentication class under Protected classes in STANDARD.md, and the fix is a CSRF token, an origin check or a SameSite setting that the route's tests confirm.

**References.** OWASP ASVS 5.0.0 v5.0.0-3.5.1, v5.0.0-3.5.2 [SRC-010]; OWASP WSTG 4.2 WSTG-v42-SESS-05 [SRC-186]; OWASP Cross-Site Request Forgery Prevention Cheat Sheet, sections Token-Based Mitigation and Employing Custom Request Headers for AJAX/API [SRC-040]; OWASP Top 10:2025 A01:2025 (CWE-352) [SRC-020]; Next.js Data Security guide, section CSRF [SRC-078].

**AI Agent Instruction.** When adding a cookie authenticated Route Handler or form endpoint that changes state, add a CSRF control from the list and a test for it. Never disable a CSRF check to make a request work; stop and report.

---

## XSS

### SEC-WEB-031: List and justify every raw HTML sink

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Web, SaaS, AI features |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Client and server code MUST render text through framework escaping or safe DOM APIs such as `textContent`, and every use of a raw HTML sink MUST be listed in an inventory with its data source and receive only sanitizer output (SEC-WEB-032) or constant markup. A raw HTML sink is any API that turns a string into markup or a document: `dangerouslySetInnerHTML`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `v-html`, iframe `srcdoc`, `createContextualFragment`, `setHTMLUnsafe`, `parseHTMLUnsafe`, DOM parser output inserted into the live document, jQuery `html`, `append` or `prepend` called with a string, a Markdown renderer with raw HTML enabled, and any wrapper component that forwards its prop to one of these. Untrusted or generated HTML (from users, models, third parties or staff) MUST pass the sanitizer or render in an iframe whose `sandbox` attribute omits `allow-same-origin` (a sandbox with both `allow-scripts` and `allow-same-origin` gives no isolation), or on a separate registrable domain. A data script block (for example structured data) whose content comes from the project's single registered encoder (SEC-WEB-001) and holds no HTML is constant markup: list it in the inventory and it needs no sanitizer. The sink definition also covers HTML that server code builds from template literals, string concatenation, library HTML generators and email templates, which SEC-API-147 in BACKEND-SECURITY.md owns.

**Why.** Raw HTML sinks bypass the framework's escaping; one fed with user or model content runs attacker script in the app's origin.

**Implementation.**
- Prefer components that render text. Remove raw HTML sinks where a component can do the job.
- Keep the inventory in the security decisions log or as a comment registry checked in review.
- Add a lint or Semgrep rule that fails CI on any raw HTML sink not on the inventory.
- `eval`, `new Function` and string timers in client code are also banned; server side rules are in BACKEND-SECURITY.md.
- Owned by SEC-API-147 in BACKEND-SECURITY.md for this root cause (HTML built by server code, including email); report one finding. Browser DOM sinks stay here.
- Severity tiers: a sink that receives user or model data without sanitizer output is CRITICAL. When every sink the scan finds is verified to receive only constant markup or sanitizer output and only the inventory is missing or stale, the finding is a documentation gap rated LOW.

**Verify.**
1. Run Semgrep for the sinks named in the Requirement and for `eval` and `new Function` in client code; compare results to the inventory. Search the whole source tree for each sink name as well, because a wrapper component hides the sink from a rule that matches the sink call only.
2. For each listed sink, trace the data source and confirm it is constant or sanitized. For every iframe that receives generated or untrusted HTML, run a browser test that the framed document cannot read the parent document or the app cookies.

**Evidence.** Semgrep report matching the inventory; CI rule configuration.

**Exceptions.** None for sinks fed by user or model data. A missing or stale inventory alone, with every sink traced and shown safe, is rated LOW. Sinks fed only by constant markup are listed but need no further exception.

**References.** OWASP ASVS 5.0.0 v5.0.0-3.2.2, v5.0.0-1.3.2 [SRC-010]; OWASP Cross Site Scripting Prevention Cheat Sheet, section Framework Security [SRC-039]; CISA Secure by Design, SbD Tactic: Web template frameworks [SRC-063]; OWASP Top 10:2025 A05:2025 (CWE-79) [SRC-020].

**AI Agent Instruction.** Do not add a raw HTML sink. If one seems necessary, use sanitizer output only, add it to the inventory, and say so in your summary. Never pass user or model content to a raw HTML sink directly.

---

### SEC-WEB-032: Sanitize user supplied HTML with a maintained library

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Web, SaaS |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW, DEPENDENCY SCAN |

**Requirement.** HTML from users, including rich text editor output and imported content, and HTML generated by a model or taken from a third party, MUST pass through a maintained HTML sanitizer library with an allowlist of tags and attributes immediately before it is rendered, unless it renders in a sandboxed iframe as SEC-WEB-031 allows.

**Why.** Rich text stored without sanitization becomes stored XSS that runs for every user who views it, including admins.

**Implementation.**
- Use a widely maintained sanitizer (for example DOMPurify) with an explicit tag and attribute allowlist; never write a regex based filter.
- Sanitize at render time, because sanitizers change and stored data may predate the current rules. Sanitizing before storage as well is allowed.
- Block event handler attributes, `style` where not needed, and URLs that fail SEC-WEB-002.
- Keep the sanitizer within its patch window; dependency rules are in DEPENDENCIES.md.

**Verify.**
1. Store payloads such as `<img src=x onerror=alert(1)>`, `<a href="javascript:alert(1)">x</a>` and `<svg><script>alert(1)</script></svg>` through every rich text input, render them in Playwright, and assert no script runs.
2. Run a dependency scan and confirm the sanitizer has no open advisory.

**Evidence.** Passing payload tests; dependency scan report.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.3.1 [SRC-010]; OWASP Cross Site Scripting Prevention Cheat Sheet, section HTML Sanitization [SRC-039]; OWASP Input Validation Cheat Sheet, section Validating Rich User Content [SRC-037]; OWASP Top 10:2025 A05:2025 (CWE-79) [SRC-020].

**AI Agent Instruction.** Render user HTML only through the project's sanitizer with its allowlist. Never write a custom HTML filter and never render user HTML unsanitized.
