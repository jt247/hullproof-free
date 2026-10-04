# Privacy

| Field | Value |
|-------|-------|
| Domain codes | SEC-GOV, SEC-DATA |
| Topics covered | Privacy governance and consent, Personal data, Data Retention, Deletion |
| Part of | Hullproof Security Standard, see STANDARD.md |

Privacy governance (lawful basis, notices, DPIA, registration), personal data handling, retention, deletion, and consent. Law driven requirements name the market they apply to. Requirement IDs keep their SEC-GOV and SEC-DATA codes. Cryptography, TLS and storage are later in this document; breach notification is in INCIDENT-RESPONSE.md.

> Research based engineering guidance, not legal advice.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 3 of the 53 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-GOV-051](#sec-gov-051-no-ai-feature-performs-an-eu-prohibited-ai-practice) | No AI feature performs an EU prohibited AI practice | CRITICAL | LAUNCH where the law applies (EU); GROWTH otherwise | AI features |
| [SEC-DATA-024](#sec-data-024-no-endpoint-returns-personal-data-to-an-unauthenticated-caller) | No endpoint returns personal data to an unauthenticated caller | BLOCKER | LAUNCH | SaaS, Web, API, Database (Supabase), Serverless |
| [SEC-DATA-040](#sec-data-040-deletion-and-export-act-only-on-the-callers-own-data) | Deletion and export act only on the caller's own data | BLOCKER | LAUNCH | SaaS, API, Backend, Serverless |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Applicable law per market | None | None | SEC-GOV-024 |
| Lawful basis per processing purpose | None | None | SEC-GOV-049, SEC-DATA-051 |
| Privacy notices (web, and pre install for mobile) | MOBILE-SECURITY.md | None | SEC-GOV-026, SEC-GOV-027 |
| Consent and its withdrawal (cookies and trackers, email tracking, marketing) | MOBILE-SECURITY.md | None | SEC-DATA-046, SEC-DATA-056, SEC-DATA-057, SEC-DATA-052 |
| Data inventory and classification | AI-SECURITY.md | None | SEC-GOV-025 |
| Data minimisation | OBSERVABILITY.md, AI-SECURITY.md | None | SEC-DATA-025, SEC-DATA-027, SEC-DATA-047, SEC-DATA-035 |
| Purpose limitation | MOBILE-SECURITY.md | None | SEC-DATA-049 |
| Children's data | None | None | SEC-DATA-050 |
| Sensitive data categories | DATA-PROTECTION.md | None | SEC-DATA-026 |
| Data subject rights (access, correction, deletion, portability, objection) with deadlines per market | None | None | SEC-DATA-038, SEC-DATA-039, SEC-DATA-040, SEC-DATA-041, SEC-DATA-044, SEC-DATA-053, SEC-DATA-054, SEC-DATA-055 |
| Retention schedules and sector overrides | DATABASE-SECURITY.md, AI-SECURITY.md | None | SEC-DATA-031, SEC-DATA-032, SEC-DATA-033, SEC-DATA-034, SEC-DATA-037 |
| Deletion across all stores, including backups and processors | DATABASE-SECURITY.md, AI-SECURITY.md, AUTH.md | None | SEC-DATA-042, SEC-DATA-043, SEC-DATA-045 |
| Processors and vendor agreements | AI-SECURITY.md, INCIDENT-RESPONSE.md | None | SEC-GOV-048, SEC-DATA-036 |
| Cross border transfers per market | AI-SECURITY.md | None | SEC-GOV-030 |
| DPIA triggers and filing | None | None | SEC-GOV-028, SEC-GOV-029, SEC-GOV-036 |
| Regulator registration (NG NDPC tiers) and DPO | INCIDENT-RESPONSE.md | NG subject count | SEC-GOV-031, SEC-GOV-032, SEC-GOV-033, SEC-GOV-037 |
| Automated decision making and AI disclosures | AI-SECURITY.md | None | SEC-GOV-034, SEC-GOV-035 |
| EU AI Act role, prohibited practices and AI literacy | AI-SECURITY.md | None | SEC-GOV-050, SEC-GOV-051, SEC-GOV-052 |
| Privacy by design and by default | None | None | SEC-DATA-024, SEC-DATA-030, SEC-DATA-048 |
| Access logging for personal data | OBSERVABILITY.md | None | SEC-DATA-028 |
| Breach notification | INCIDENT-RESPONSE.md | None | None in this document |
| Encryption of personal data | DATA-PROTECTION.md, DATABASE-SECURITY.md | None | None in this document |
| EU representative (GDPR Article 27) | None | None | SEC-GOV-054 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-MOBILE | Is a mobile build shipped, in a store, or handed to testers in this release? | Check that no app.json, eas.json, ios or android folder, or expo or react-native dependency exists in any workspace, and that no store listing or TestFlight build exists. Record what was checked, or record the owner's written answer. A mobile scaffold counts as No only if it is not deployed and not reachable by real users at the audited commit; a release scope that leaves a live app out does not make the answer No. | SEC-GOV-027, SEC-DATA-039 |
| GATE-MARKET-NG | Does the product process personal data of people in Nigeria? | STAGE.md Markets served and Markets excluded name the market, and a check of signup country, billing country or analytics geography shows no Nigerian data subjects, or the owner's written answer says so. A market is excluded only by a technical control that blocks it (a country block at signup and billing) or by a recorded count of zero data subjects from the user table by country. Where the product collects no country, Global applies. | SEC-GOV-027, SEC-GOV-029, SEC-GOV-031, SEC-GOV-036, SEC-GOV-037, SEC-DATA-032 |
| GATE-MARKET-EU | Does the product process personal data of people in the EU, or place an AI feature on the EU market? | STAGE.md Markets served and Markets excluded name the market, and a check of signup country, billing country or analytics geography shows no EU data subjects, or the owner's written answer says so. A market is excluded only by a technical control that blocks it (a country block at signup and billing) or by a recorded count of zero data subjects from the user table by country. Where the product collects no country, Global applies. | SEC-GOV-050, SEC-GOV-051, SEC-GOV-054, SEC-DATA-056 |
| GATE-MARKET-KE | Does the product process personal data of people in Kenya? | STAGE.md Markets served and Markets excluded name the market, and a check of signup country, billing country or analytics geography shows no Kenyan data subjects, or the owner's written answer says so. A market is excluded only by a technical control that blocks it (a country block at signup and billing) or by a recorded count of zero data subjects from the user table by country. Where the product collects no country, Global applies. | SEC-GOV-029 |
| GATE-MARKET-UK | Does the product process personal data of people in the United Kingdom? | STAGE.md Markets served and Markets excluded name the market, and a check of signup country, billing country or analytics geography shows no United Kingdom data subjects, or the owner's written answer says so. A market is excluded only by a technical control that blocks it (a country block at signup and billing) or by a recorded count of zero data subjects from the user table by country. Where the product collects no country, Global applies. | SEC-GOV-054 |
<!-- hullproof:gates:end -->

Scope: SEC-DATA-032 covers Nigeria only, and sector retention minimums elsewhere are not covered. EU member state laws implementing the ePrivacy Directive are not covered; the controls follow the directive, EU case law and EDPB positions. EU AI Act high risk duties (Annex III systems from 2 December 2027) are not covered.

---

## Privacy governance

### SEC-GOV-051: No AI feature performs an EU prohibited AI practice

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH where the law applies (EU); GROWTH otherwise |
| Applies To | AI features |
| Automation | MANUAL |
| Verification method | DOCUMENT REVIEW, CODE REVIEW |

**Requirement.** Before an AI feature reaches EU users, a named owner MUST record a screen against each Article 5(1) prohibited practice, and the product MUST NOT ship a feature that infers emotions of people at work or in education (other than for medical or safety reasons), categorises people by biometric data to infer race, political opinions, union membership, beliefs, sex life or sexual orientation, scores people on social behaviour or personal traits leading to unrelated or disproportionate detrimental treatment, or uses manipulative techniques or exploits age, disability or economic situation in a way likely to cause significant harm.

**Why.** These practices have been banned in the EU since 2 February 2025. Small SaaS products drift into them through ordinary features: an HR tool that scores staff mood from video calls, an edtech feature that reads student emotions, or a growth feature that targets financially vulnerable users with pressure tactics.

**Implementation.**
- Keep the screen as a short checklist in the threat model entry (SEC-AI-001), one line per Article 5(1) point with "not applicable" and the reason, and link it from the SEC-GOV-050 record.
- Rerun the screen when a feature gains a new purpose, a new user group (employees, students, children) or a new input type (camera, microphone, biometric data).
- Image, video and audio generation features are also screened against the points added by the Digital Omnibus that apply from 2 December 2026; the technical safeguards are SEC-AI-060.
- If any point is uncertain, treat the feature as blocked for the EU until legal review is recorded.

**Verify.**
1. Open the threat model entry of every AI feature reaching EU users and confirm the Article 5(1) screen is complete, dated and signed by the owner.
2. Search the code and prompts for emotion, sentiment of staff or students, biometric attributes and vulnerability targeting (for example `rg -i "emotion|mood|biometric|vulnerab" src prompts`), and confirm each hit is covered by the screen.

**Evidence.** Completed screen per feature; search output with dispositions.

**Exceptions.** Rule 8 of STANDARD.md Severity applies: when the Article 5(1) screen is missing and no feature does any of the listed practices, rate the finding MEDIUM. When a feature does one of them, the CRITICAL label stands. Products with no EU users and no output used in the EU. A waiver for a feature that matches a prohibited practice is not available while it serves the EU.

**References.** Law driven (EU): Regulation (EU) 2024/1689 Art 5(1)(a), (b), (c), (f), (g) and Art 113 point (a) [SRC-214]; Regulation (EU) 2026/1744 amending Art 5(1) and Art 113 point (a) [SRC-215]; AI Act Service Desk explorer, Article 5 [SRC-216].

**AI Agent Instruction.** Refuse to build emotion inference on employees or students, biometric inference of sensitive traits, or social scoring for a product that serves the EU, and say why. When a request touches these areas, ask for the recorded Article 5 screen first.

---

## Personal data

### SEC-DATA-024: No endpoint returns personal data to an unauthenticated caller

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Database (Supabase), Serverless |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, CONFIG REVIEW |

**Requirement.** A REST endpoint, server action, RPC, view or storage path MUST NOT return personal data to a caller holding only the public client key or no credential at all.

**Why.** Missing access control on tables and routes is the most common real exposure in AI built apps; one scan of vibe coded apps found 175 PII exposures, including bank details and plaintext passwords returned without authentication.

**Implementation.**
- Enforce access on the server. On Supabase, RLS on every exposed table is set out in DATABASE-SECURITY.md; this requirement is the end to end check that nothing still leaks.
- Treat the publishable or anon key as public. Anything it can read is public.

**Verify.**
1. With only the publishable key, call every PostgREST table and view, every RPC, every API route and server action, and every storage path.
2. Scan response bodies for email, phone, date of birth, IBAN or bank number, and national ID patterns, and fail on any match.
3. Confirm the Supabase advisor reports zero for lints 0002, 0013 and 0023.
4. For server rendered public pages, read each public route that fetches user data and confirm no personal data field is passed as a prop to a client component, because props passed across the server and client boundary are serialized into the page HTML. View the source of one such page as an anonymous visitor and apply the step 2 patterns to it.

**Evidence.** Dynamic test report listing every endpoint called and the result, plus advisor output.

**Exceptions.** Personal data that a user chose to make public (for example a profile set to public) may be returned to anonymous callers when the exposed fields are listed in the data inventory (SEC-GOV-025 in PRIVACY.md, or a list in the repository) and the query honours the stored choice. A public flag counts only when an affirmative user action sets it and it defaults to private.

**References.** Law driven for NG, EU, ZA and KE: GDPR Art 25(2), Art 32(4) [SRC-103]; Kenya DPA 2019 s41(3)(d) [SRC-106]; POPIA s19(1) [SRC-104]; NDPA 2023 s39(1) (Derived) [SRC-100]. OWASP ASVS 5.0.0 v5.0.0-8.2.2 (L1) [SRC-010]; Supabase Advisors lints 0002, 0013, 0023 [SRC-076]; Escape, The State of Security of Vibe Coded Apps (evidence) [SRC-007].

**AI Agent Instruction.** Before finishing any change that adds a table, view, route or bucket holding personal data, run the anonymous replay against it. Never make personal data readable with the public key. If you find an exposure, stop and report it as a BLOCKER.

---

## Deletion

### SEC-DATA-040: Deletion and export act only on the caller's own data

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | SaaS, API, Backend, Serverless |
| Automation | FULL |
| Verification method | AUTOMATED TEST, DYNAMIC TEST |

**Requirement.** Account deletion, data export and correction endpoints MUST take the subject's identity from the authenticated session on the server, and MUST NOT act on a user identifier supplied in the request unless the caller is an authorized administrator. Where the product holds personal data of its users, each of these endpoints MUST exist.

**Why.** A deletion or export endpoint that trusts a user ID from the request lets any user erase or download another user's data with one request.

**Implementation.**
- Derive the user ID from the verified session (`auth.getUser()` on the server), never from the body, query or path.
- Admin deletion runs through a separate admin route with its own authorization and audit log.

**Verify.**
1. Automated test: user B calls delete, export and correction with user A's identifier in the body, query and path, and every call is refused or acts only on user B.
2. Test the same endpoints with no session and expect 401.
3. Search the route, server action and RPC definitions for account deletion, export and correction handlers. Where the product holds personal data and one of them is missing, the result is FAIL (see SEC-DATA-038), not PASS.

**Evidence.** Passing negative tests.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1, v5.0.0-8.2.2 (L1) [SRC-010]; OWASP API Security Top 10 2023 API1:2023 [SRC-021]; OWASP WSTG 4.2 WSTG-v42-ATHZ-04 [SRC-186]; law driven, Derived for ZA, GH and EU: POPIA s23(1) [SRC-104]; Ghana Act 843 s32(1), s35(3) [SRC-109]; GDPR Art 12(6) [SRC-103]. Severity raised from the taxonomy's CRITICAL to BLOCKER because this is missing server side authorization on user data.

**AI Agent Instruction.** In any delete, export or correction handler, read the user ID only from the server verified session. Never accept a `userId` parameter for self service actions. Report any existing handler that does as a BLOCKER.
