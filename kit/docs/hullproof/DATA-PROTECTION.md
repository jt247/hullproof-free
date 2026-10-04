# Data Protection

| Field | Value |
|-------|-------|
| Domain codes | SEC-DATA |
| Topics covered | Cryptography, TLS, Object Storage |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers how the product protects data: the cryptography it chooses, keys, encryption in transit and at rest, and files in object storage. Personal data handling, retention, deletion, consent and privacy governance live in PRIVACY.md. Row level security lives in DATABASE-SECURITY.md, sessions in AUTH.md, uploads in BACKEND-SECURITY.md, webhooks in API-SECURITY.md, log content in OBSERVABILITY.md, on device storage in MOBILE-SECURITY.md, and AI context and retrieval indexes in AI-SECURITY.md.

> Research based engineering guidance, not legal advice. Requirements that name a law and a market (NG Nigeria NDPA 2023 and GAID 2025, EU GDPR, ZA POPIA, KE Kenya DPA 2019 and its 2021 Regulations, GH Ghana Act 843) are Hullproof's engineering reading of the official texts. Where a source marks a duty as Derived, it is our interpretation of a general legal duty. A law driven requirement applies only when the product serves that market. Meeting these requirements does not by itself make a product compliant, and a qualified lawyer in each market has the final word.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 6 of the 24 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-DATA-001](#sec-data-001-unguessable-values-come-from-a-csprng) | Unguessable values come from a CSPRNG | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Mobile, Serverless |
| [SEC-DATA-005](#sec-data-005-passwords-stored-under-an-sec-auth-001-exception-use-an-approved-slow-hash) | Passwords stored under an SEC-AUTH-001 exception use an approved slow hash | CRITICAL | LAUNCH | SaaS, Web, API, Backend, Database |
| [SEC-DATA-011](#sec-data-011-external-endpoints-use-tls-12-or-13-with-trusted-certificates) | External endpoints use TLS 1.2 or 1.3 with trusted certificates | CRITICAL | LAUNCH | SaaS, Web, API, Serverless, Cloud |
| [SEC-DATA-019](#sec-data-019-buckets-holding-user-data-have-no-public-access-path) | Buckets holding user data have no public access path | BLOCKER | LAUNCH | SaaS, Web, Mobile, Cloud |
| [SEC-DATA-020](#sec-data-020-object-access-is-limited-to-the-owning-user-or-tenant) | Object access is limited to the owning user or tenant | BLOCKER | LAUNCH | SaaS, API, Backend, Cloud |
| [SEC-DATA-059](#sec-data-059-storage-keys-presented-by-the-client-resolve-to-a-record-issued-to-the-callers-tenant) | Storage keys presented by the client resolve to a record issued to the caller's tenant | CRITICAL | LAUNCH | SaaS, API, Backend, Cloud |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Secure random values (ASVS V11.5) | AUTH.md, API-SECURITY.md | None | SEC-DATA-001 |
| Vetted crypto libraries and no custom cryptography (ASVS V11.2) | AUTH.md | None | SEC-DATA-002 |
| Encryption algorithms and modes (ASVS V11.3) | None | None | SEC-DATA-003 |
| Hashing and hash based functions (ASVS V11.4) | API-SECURITY.md | None | SEC-DATA-004 |
| Password hashing | AUTH.md | None | SEC-DATA-005 |
| Key storage apart from data and platform keystore on devices | DATABASE-SECURITY.md, MOBILE-SECURITY.md | None | SEC-DATA-007 |
| Field level encryption of sensitive category data | PRIVACY.md, AUTH.md | None | SEC-DATA-008 |
| Constant time comparison of secrets | API-SECURITY.md | None | SEC-DATA-009 |
| Crypto inventory and key lifecycle (ASVS V11.1) | SECRETS.md | None | SEC-DATA-010 |
| In use data cryptography (ASVS V11.7) | None | None | None in this document |
| TLS versions and certificates on external endpoints (ASVS V12.1, V12.2) | INFRASTRUCTURE-SECURITY.md | None | SEC-DATA-011 |
| Plain HTTP redirects to HTTPS with no plaintext fallback (ASVS V12.2) | None | None | SEC-DATA-012 |
| HSTS | None | None | SEC-DATA-013, SEC-DATA-014 |
| WebSocket encryption | FRONTEND-SECURITY.md | None | SEC-DATA-015 |
| Mobile app traffic over HTTPS | MOBILE-SECURITY.md | None | None in this document |
| TLS certificate validation never disabled (ASVS V12.3) | None | None | SEC-DATA-016 |
| Internal, database and outbound connections encrypted (ASVS V12.3) | DATABASE-SECURITY.md, API-SECURITY.md | None | SEC-DATA-017 |
| Certificate pinning decision for the mobile app | MOBILE-SECURITY.md | None | None in this document |
| Private buckets for user data (ASVS V5.3) | None | None | SEC-DATA-019 |
| Object access limited to the owning user or tenant | AUTH.md | None | SEC-DATA-020 |
| No listing of public buckets | None | None | SEC-DATA-021 |
| Short lived signed URLs | None | None | SEC-DATA-022 |
| Storage keys generated on the server (ASVS V5.3) | BACKEND-SECURITY.md | None | None in this document |
| Storage credentials least privilege and server only | SECRETS.md | None | SEC-DATA-023 |
| Upload handling (ASVS V5.2) | BACKEND-SECURITY.md | None | None in this document |
| Backups of uploaded files | DATABASE-SECURITY.md | None | None in this document |
| Data classification and protection documentation (ASVS V14.1) | PRIVACY.md | None | None in this document |
| Sensitive data kept out of URLs (ASVS V14.2) | PRIVACY.md, SECRETS.md | None | None in this document |
| Minimal personal data in responses (ASVS V14.2) | PRIVACY.md, API-SECURITY.md | None | None in this document |
| Caching of sensitive responses (ASVS V14.2) | AUTH.md | None | None in this document |
| Personal data sent to processors, logs and analytics (ASVS V14.2) | PRIVACY.md, OBSERVABILITY.md | None | None in this document |
| Retention and deletion (ASVS V14.2) | PRIVACY.md | None | None in this document |
| Production data in lower environments | PRIVACY.md, DATABASE-SECURITY.md | None | None in this document |
| Metadata removal from user submitted files (ASVS V14.2) | BACKEND-SECURITY.md | None | SEC-DATA-058 |
| Client side data protection (ASVS V14.3) | FRONTEND-SECURITY.md, AUTH.md, MOBILE-SECURITY.md | None | None in this document |
| Privacy law controls (lawful basis, notices, consent, data subject rights) | PRIVACY.md | None | None in this document |
| Client presented storage keys and public bucket uploads | None | None | SEC-DATA-059, SEC-DATA-060 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-UPLOADS | Does the product accept user uploaded files from any source (browser, client SDK, mobile picker, base64 or data URL body, inbound email attachment, avatar or file import), or keep user data in object storage buckets? | Search the source and storage configuration for multipart or formData file handling, signed upload URLs, upload libraries, client SDK uploads, base64 and data URL bodies, mobile pickers, inbound email attachments and avatar import. Cover stores other than S3 compatible ones (managed storage products, database large objects, file fields in a CMS), a storage bucket, putObject or getSignedUrl, and list the buckets on the storage provider. Record the commands, the number of files searched and that nothing was found, or record the owner's written answer. | SEC-DATA-019 (BLOCKER), SEC-DATA-020 (BLOCKER), SEC-DATA-021, SEC-DATA-022, SEC-DATA-058 |
<!-- hullproof:gates:end -->

---

## Cryptography

### SEC-DATA-001: Unguessable values come from a CSPRNG

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Mobile, Serverless |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Every value whose security depends on it being unguessable (session or API tokens, password reset and invite codes, share links, verification codes, secret identifiers) MUST be generated by a cryptographically secure random number generator with at least 128 bits of entropy. A version 4 UUID from a CSPRNG (`crypto.randomUUID()`, 122 random bits) is also accepted for a single use token that is bound to one user or resource and expires, and for identifiers that only need to be unguessable. Long lived bearer secrets such as session tokens and API keys use 16 or more random bytes.

**Why.** Values from `Math.random()`, timestamps or counters can be predicted, so an attacker can forge a reset link, guess an invite, or enumerate shared files.

**Implementation.**
- Server and Node: `crypto.randomBytes(16)` or more, or `crypto.randomUUID()` for identifiers that only need to be unguessable.
- Browser and edge runtimes: `crypto.getRandomValues()` on a typed array of at least 16 bytes.
- Short human readable codes (for example six digit OTPs) are allowed only where another control limits guessing, such as attempt limits and short expiry in AUTH.md. They do not count as unguessable values under this requirement.
- Default stack: Expo apps use `expo-crypto` random bytes, never `Math.random()`.
- `crypto.randomUUID()` returns a version 4 UUID from the runtime CSPRNG, so it meets this requirement for the single use bound case above. It does not meet it for a long lived bearer secret. Time based UUIDs (versions 1, 6 and 7) are not accepted for security values.

**Verify.**
1. Run a Semgrep rule that flags `Math.random`, `Date.now` or counters used inside functions or variables named like token, code, secret, invite, reset, share or id.
2. Review every generator of security values and confirm the source call and byte length (16 bytes or more, or `crypto.randomUUID()` in the accepted single use bound or identifier cases).
3. Generate 1,000 values in a test and assert no duplicates and the expected length.

**Evidence.** Semgrep report with zero findings for the rule, and the review note listing each generator with its source and length.

**Exceptions.** Values that are not security relevant (UI keys, sample data). Record each excluded generator and why it is not security relevant. A version 4 UUID used as a long lived bearer secret, or any value from a non CSPRNG source, stays a finding under this requirement.

**References.** OWASP ASVS 5.0.0 v5.0.0-11.5.1 (L2, promoted to LAUNCH) [SRC-010]; OWASP ASVS 5.0.0 Appendix C, Random values (tag v5.0.0_release) [SRC-010]; OWASP Top 10 2025 A04:2025 [SRC-020].

**AI Agent Instruction.** When you write code that creates any token, code, link or identifier meant to be secret, use the platform CSPRNG with at least 16 bytes. Never use `Math.random()`, timestamps or incrementing IDs for these values. If you find an existing generator that does, report it as a finding before changing anything else in that file.

---

### SEC-DATA-005: Passwords stored under an SEC-AUTH-001 exception use an approved slow hash

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Backend, Database |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, DOCUMENT REVIEW |

**Requirement.** This requirement applies only where an exception to SEC-AUTH-001 is recorded that lets the application store passwords itself. In that case, passwords MUST be hashed with argon2id, scrypt, bcrypt or PBKDF2 at or above the minimum parameters in ASVS 5.0.0 Appendix C at tag `v5.0.0_release`.

**Why.** A fast or unsalted hash lets an attacker who steals the user table recover most passwords offline in hours.

**Implementation.**
- Preferred: argon2id with one of t = 1 and m ≥ 46 MiB, t = 2 and m ≥ 19 MiB, or t ≥ 3 and m ≥ 12 MiB, with p = 1.
- Other approved minimums: scrypt N ≥ 2^17 with r = 8 and p = 1 (or the other tabled rows); bcrypt cost ≥ 10; PBKDF2 HMAC-SHA-512 ≥ 210,000 iterations or HMAC-SHA-256 ≥ 600,000 iterations.
- Take parameters from the tag, never from ASVS master or the `latest` snapshot.
- Without a recorded SEC-AUTH-001 exception, application code must not hash passwords at all, and this requirement does not apply.
- Default stack: Supabase Auth owns password storage when the app uses it, so no exception exists and this requirement does not apply. ASSUMPTION: the algorithm Supabase Auth uses was not verified in Hullproof research.

**Verify.**
1. Check the security decisions log for a recorded SEC-AUTH-001 exception. If none exists, confirm under SEC-AUTH-001 that no password write path exists and stop here.
2. Search for password write paths (`hash(`, `bcrypt`, `argon2`, `pbkdf2`, `scrypt`, `createHash` near `password`) and confirm the function and parameters against the Appendix C table.
3. Fail any plain SHA family hash of a password, salted or not.

**Evidence.** The recorded SEC-AUTH-001 exception and a code review note with the function and parameters.

**Exceptions.** Legacy hashes may remain until the user next signs in and is rehashed, with the migration plan and end date recorded and an owner named.

**References.** OWASP ASVS 5.0.0 v5.0.0-11.4.2 (L2, promoted to LAUNCH) [SRC-010]; OWASP ASVS 5.0.0 Appendix C, Password storage (tag v5.0.0_release) [SRC-010]; NIST SP 800-63B-4 §3.1.1.2 [SRC-060]; OWASP Password Storage Cheat Sheet [SRC-032].

**AI Agent Instruction.** Never store a password with SHA-256, MD5 or any fast hash. Do not hash passwords in application code unless an exception to SEC-AUTH-001 is recorded; if none is, apply SEC-AUTH-001 and stop. Where the exception exists, use argon2id with tag listed parameters and cite them in a code comment. Report any existing fast hash as a CRITICAL finding.

---

## TLS

### SEC-DATA-011: External endpoints use TLS 1.2 or 1.3 with trusted certificates

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Serverless, Cloud |
| Automation | FULL |
| Verification method | DYNAMIC TEST, CONFIG REVIEW |

**Requirement.** Every public hostname the product serves MUST offer only TLS 1.2 or TLS 1.3 with a publicly trusted, unexpired certificate that matches the hostname.

**Why.** Older TLS versions and invalid certificates let attackers on the network read or change traffic, including session tokens and personal data.

**Implementation.**
- Default stack: Vercel, Render and Supabase terminate TLS. ASSUMPTION: that their TLS settings meet this requirement is not verified in Hullproof research, so test each host rather than assume it.
- Cloudflare R2 custom domains: set the minimum TLS version on the domain (available through the API).
- Monitor certificate expiry for any certificate the team manages itself. HSTS makes certificate errors fatal for users (RFC 6797 §12.1).

**Verify.**
1. Run testssl.sh or SSL Labs against every public hostname, including API, app, marketing, storage custom domains and webhook receivers.
2. Fail if TLS 1.0, TLS 1.1 or SSL is offered, or the certificate is untrusted, expired or mismatched.

**Evidence.** Scan output per hostname, dated within the release cycle.

**Exceptions.** None for hosts that carry user data or credentials. A purely static public host may record a waiver with an owner and expiry.

**References.** OWASP ASVS 5.0.0 v5.0.0-12.1.1, v5.0.0-12.2.2 (L1) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-CRYP-01 [SRC-186]; Cloudflare R2 docs, minimum TLS on custom domains [SRC-125]; NIST SP 800-53 Rev 5 SC-8(1) (ADVISORY) [SRC-062]; law driven, Derived for NG, EU and KE: GDPR Art 32(1)(a) [SRC-103], NDPA 2023 s39(2)(b) [SRC-100], Kenya DPA 2019 s41(4)(c) [SRC-106].

**AI Agent Instruction.** Never add a public endpoint, custom domain or callback URL that uses `http://`. When you add a hostname, add it to the TLS scan list. Do not claim a platform's TLS is compliant without a scan result.

---

## Object storage

### SEC-DATA-019: Buckets holding user data have no public access path

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, Mobile, Cloud |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST |

**Requirement.** Every bucket that holds user or tenant files MUST be private with no public access path enabled, and public buckets MUST hold only files intended for anyone.

**Why.** A public bucket serves every file to anyone with the URL, with no authentication or ownership check.

**Implementation.**
- Default stack: Supabase Storage buckets are private by default. A public bucket skips access control for reads.
- Default stack: Cloudflare R2 buckets are private until a public path is enabled. Disable `r2.dev` access on every production bucket, and confirm each enabled custom domain is intended. Disabling one path does not close the others.
- Keep user files and public assets in separate buckets.

**Verify.**
1. Export the bucket list with public flags (Supabase dashboard or API; R2 bucket settings, listing `r2.dev` and every custom domain per bucket).
2. For each bucket holding user files, request a known object URL without a token and confirm 400, 401, 403 or 404.

**Evidence.** Bucket configuration export and the failed anonymous request results.

**Exceptions.** None.

**References.** Supabase Storage Access Control (Private buckets, Public buckets) [SRC-074]; Cloudflare R2 docs, Public buckets [SRC-125]; OWASP ASVS 5.0.0 v5.0.0-8.2.2 (L1) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-CONF-11 [SRC-186].

**AI Agent Instruction.** Store user files only in private buckets. Never make a bucket public, enable `r2.dev`, or add a public custom domain to a bucket holding user files, even to fix a broken image. Stop and report instead.

---

### SEC-DATA-020: Object access is limited to the owning user or tenant

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Cloud |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, DYNAMIC TEST, CODE REVIEW |

**Requirement.** Every read, write and delete of a stored object MUST be authorized on the server against the requesting user's ownership or tenant membership before access is granted or a signed URL is issued.

**Why.** Without an ownership check, any signed in user can fetch or overwrite other users' files by changing an object path.

**Implementation.**
- Default stack, Supabase Storage: write a policy per operation that checks role, bucket ID and the owner's folder (for example the first path segment equals `auth.uid()`), and for tenants, membership of the tenant folder.
- Default stack, Cloudflare R2: R2 has no per user policy engine. The app looks up the object record, checks the caller owns it or belongs to its tenant, and only then signs a URL for that exact key. The server picks the key, never the client.
- Uploads, file types and size limits are in BACKEND-SECURITY.md.

**Verify.**
1. Automated test: user B requests a download URL, upload URL and delete for user A's object, and every request is refused.
2. Automated test per Supabase storage policy for anonymous, owner, second user and second tenant.
3. Review the signing function and confirm the ownership query runs before signing.
4. Client presented keys: run the Verify steps of SEC-DATA-059. For a public bucket written through presigned uploads, run the Verify steps of SEC-DATA-060.

**Evidence.** Passing authorization tests and the review note.

**Exceptions.** None. Scope clarification: a storage key or object ID presented by the client MUST be accepted only after the server resolves it to an object record in the caller's tenant; a bucket or key prefix bound to the issuing tenant, checked by the server on every use, meets this requirement. Public buckets written through presigned uploads are covered by the same check on the upload route.

**References.** Supabase Storage Access Control (Scope policies) [SRC-074]; Cloudflare R2 docs, Presigned URLs [SRC-125]; OWASP ASVS 5.0.0 v5.0.0-8.2.2 (L1), v5.0.0-8.4.1 (L2, promoted to LAUNCH) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-04 [SRC-186].

**AI Agent Instruction.** Before generating any signed URL or touching any object, check on the server that the caller owns the object or belongs to its tenant. Never sign a key supplied by the client. Never write a storage policy that grants access to all authenticated users.

---

### SEC-DATA-059: Storage keys presented by the client resolve to a record issued to the caller's tenant

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Cloud |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, CODE REVIEW |

**Requirement.** When a route accepts a storage key, object path or file identifier from the client to confirm an upload, attach a file to a record, read, replace or delete an object, the server MUST resolve it to a record that the server created when it issued the key (key, tenant, user, purpose, expiry, state), or MUST check on every use that the key sits under a prefix bound to the caller's tenant. The route MUST refuse a key with no record, a record that belongs to another tenant, a purpose that differs from the route's, an expired record, or one already consumed. Keys MUST be generated by the server from internal identifiers and MUST NOT contain user supplied names. A client supplied key string MUST NOT be used to build a path or a storage call without that resolution.

**Why.** An upload flow often ends with the client telling the server which key it just wrote. A server that trusts the string lets a user name another tenant's key and attach it to their own record (and so read it), delete it, or confirm an object they never uploaded. Presigned URLs bind one operation to one key and fail if the key is changed [SRC-125], but that protects the upload step only. The confirm, attach and delete steps are ordinary routes, and each one needs its own check. SEC-DATA-020 requires an ownership check before access. This requirement says what the check resolves against when the key comes from the client.

**Implementation.**
- Keep an upload record when the server issues a URL: random server generated key, tenant id, user id, purpose (avatar, document, import), expiry and state (issued, confirmed, consumed).
- In every confirm, attach, read and delete route, load the record by key and tenant in one query. Refuse when no row is returned. Set the state to consumed in the same transaction as the attach.
- Build keys as `<tenant id>/<purpose>/<random id>`, with a random id from a CSPRNG (SEC-DATA-001). Do not add the client file name; store it as a separate column and encode it when served (ASVS 5.3.2).
- Where a prefix bound to the tenant is the design, check the prefix against the session tenant on every use, not only when issuing.
- Related: SEC-DATA-020 (ownership check before any access), SEC-DATA-022 (signed URL lifetime).

**Verify.**
1. List every route that takes a key, path, file id or URL from the request body, query or path (search for `key`, `path`, `objectKey`, `fileId`, `storagePath`) and open each handler. Confirm a lookup by key and tenant runs before any storage call.
2. Two tenant test. As tenant B, send the confirm, attach, read and delete requests naming tenant A's real key, then a key that does not exist, then a key issued for another purpose (an avatar key sent to the document attach route). Expect a refusal each time, and confirm with an admin tool that tenant A's object is unchanged.
3. Replay test. Send a confirm for the same key twice and for an expired record. Expect the second and the expired request to be refused.

**Evidence.** The route list with the lookup location per route, the saved two tenant and replay test results, and the object check after the delete attempt.

**Exceptions.** Public assets that every visitor may read by design and that no route attaches or deletes by client key. Record the bucket. A key prefix bound to the tenant and checked on every use meets the requirement in place of an issuance record.

**References.** OWASP ASVS 5.0.0 v5.0.0-5.3.2 (L1), v5.0.0-8.2.2 (L1) [SRC-010]; OWASP API Security Top 10 2023 API1:2023 [SRC-021]; Cloudflare R2 docs, Presigned URLs [SRC-125]; Supabase Storage Access Control [SRC-074]; OWASP WSTG 4.2 WSTG-v42-ATHZ-04 [SRC-186].

**AI Agent Instruction.** Never pass a key from the request to a storage call. Look it up in the upload record by key and tenant first, and refuse when it is missing or belongs to another tenant or purpose. Generate keys on the server and keep user file names out of them. When you add a confirm, attach or delete route, add the two tenant test above.
