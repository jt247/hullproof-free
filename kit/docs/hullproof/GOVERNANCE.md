# Governance and Secure Development

| Field | Value |
|-------|-------|
| Domain codes | SEC-GOV |
| Topics covered | Architecture, Threat Modeling, secure development process (NIST SSDF 1.1), Vulnerability Management |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document sets the process controls around the code: how the architecture is recorded, when and how threats are modeled, who owns which security duty, how changes are reviewed and released, which privacy records and regulator filings a product needs per market, and how vulnerabilities are received, triaged and fixed. Privacy governance lives in PRIVACY.md. Technical controls live in the domain documents: AUTH.md, API-SECURITY.md, BACKEND-SECURITY.md, FRONTEND-SECURITY.md, DATABASE-SECURITY.md, DATA-PROTECTION.md, PRIVACY.md, SECRETS.md, AI-SECURITY.md, AGENTIC-DEV-SECURITY.md, DEPENDENCIES.md, INFRASTRUCTURE-SECURITY.md, MOBILE-SECURITY.md, OBSERVABILITY.md and INCIDENT-RESPONSE.md. The process stages these requirements plug into are defined in HULLPROOF.md.

> Research based engineering guidance, not legal advice. Requirements that name a law and a market (NG, EU, ZA, KE, GH) are Hullproof's engineering reading of official legal texts. Meeting them does not by itself make a product compliant, and a qualified lawyer in each market has the final word.

Market codes: NG = Nigeria (NDPA 2023 with GAID 2025), EU = GDPR, ZA = South Africa (POPIA), KE = Kenya (DPA 2019 and 2021 Regulations), GH = Ghana (Act 843). A market specific requirement applies only when the product serves that market, and then at the stage the law sets.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 0 of the 34 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Architecture record: trust zones and data access pattern (SSDF PW.1.2) | DATABASE-SECURITY.md | None | SEC-GOV-001 |
| Authorization and validation decided on the server, never only in client code | AUTH.md, API-SECURITY.md | None | None in this document |
| One server only data access layer that authorizes each read | BACKEND-SECURITY.md | None | None in this document |
| Managed services for identity, access control and logging (SSDF PW.1.3) | AUTH.md | None | SEC-GOV-003 |
| Secure defaults that apply without manual steps (SSDF PW.9.1, PW.9.2) | INFRASTRUCTURE-SECURITY.md, DATABASE-SECURITY.md | None | SEC-GOV-004 |
| Two independent layers for sensitive data | None | None | SEC-GOV-005 |
| Inventory of external services and resource heavy functions | BACKEND-SECURITY.md, API-SECURITY.md, INFRASTRUCTURE-SECURITY.md | None | SEC-GOV-013 |
| Separate hostnames for separate applications | None | None | SEC-GOV-006 |
| Dangerous functionality register | BACKEND-SECURITY.md | None | SEC-GOV-014 |
| Security decisions log for trust boundary, auth, data access and secret changes | None | None | SEC-GOV-002 |
| Threat model triggers: FULL before merge and DELTA note (SSDF PW.1.1) | None | Missing threat model | SEC-GOV-007, SEC-GOV-008 |
| Threat model content: data flow diagram, STRIDE walk, one response per threat, exit check (SSDF PW.1.1) | None | None | SEC-GOV-009 |
| AI and coding agent threats in the threat model | AI-SECURITY.md, AGENTIC-DEV-SECURITY.md | None | SEC-GOV-010 |
| Accepted risk record with owner, review date and expiry (SSDF PW.1.2, RV.2.2) | None | None | SEC-GOV-011 |
| Business limits and automation abuse cases | None | None | SEC-GOV-012 |
| Independent design review for high risk designs (SSDF PW.2.1) | DEPENDENCIES.md | None | SEC-GOV-015 |
| Threat model refresh after new evidence and published threat summary | None | None | SEC-GOV-016, SEC-GOV-017 |
| Stage declaration and Hullproof baseline adoption (SSDF PO.1.1) | None | None | SEC-GOV-018 |
| Security requirements named before implementation (SSDF PO.1.2) | None | None | SEC-GOV-019 |
| Security requirements for third party software and suppliers (SSDF PO.1.3) | DEPENDENCIES.md, AGENTIC-DEV-SECURITY.md | None | None in this document |
| Security roles, owners and coding agent delegation (SSDF PO.2.1) | None | None | SEC-GOV-020 |
| Security training for people with merge or production access (SSDF PO.2.2) | None | None | SEC-GOV-021 |
| Supporting toolchains: required checks, pinned and least privilege CI, evidence (SSDF PO.3.1, PO.3.2, PO.3.3) | DEPENDENCIES.md, SECRETS.md, AGENTIC-DEV-SECURITY.md | None | None in this document |
| Release criteria and an audit report for each deployed commit (SSDF PO.4.1, PO.4.2) | DEPENDENCIES.md | None | SEC-GOV-023 |
| Secure development environments, separated and hardened (SSDF PO.5.1, PO.5.2) | INFRASTRUCTURE-SECURITY.md, AGENTIC-DEV-SECURITY.md, DEPENDENCIES.md | None | None in this document |
| Protect code from unauthorized access and tampering (SSDF PS.1.1) | DEPENDENCIES.md, AGENTIC-DEV-SECURITY.md | None | None in this document |
| Release integrity verification (SSDF PS.2.1) | DEPENDENCIES.md | None | None in this document |
| Archive each release and its component inventory (SSDF PS.3.1, PS.3.2) | DEPENDENCIES.md, INFRASTRUCTURE-SECURITY.md | None | None in this document |
| Secure coding practices (SSDF PW.5.1) | API-SECURITY.md, BACKEND-SECURITY.md, DEPENDENCIES.md | None | None in this document |
| Build and pipeline configuration reviewed (SSDF PW.6.1, PW.6.2) | DEPENDENCIES.md | None | None in this document |
| Security review of each sensitive change before merge (SSDF PW.7.1, PW.7.2) | DEPENDENCIES.md, AGENTIC-DEV-SECURITY.md | None | SEC-GOV-022 |
| Dynamic and executable code security testing (SSDF PW.8.1, PW.8.2) | AUTH.md, AI-SECURITY.md | None | SEC-GOV-044 |
| Published security contact and disclosure policy (SSDF RV.1.1, RV.1.3) | None | Vulnerability disclosure | SEC-GOV-038, SEC-GOV-039 |
| Ongoing vulnerability identification and scheduled scans (SSDF RV.1.1, RV.1.2) | DEPENDENCIES.md, INFRASTRUCTURE-SECURITY.md | None | SEC-GOV-042 |
| Vulnerability triage and tracking (SSDF RV.2.1) | None | None | SEC-GOV-040 |
| Fix deadlines by severity and recorded acceptance (SSDF RV.2.2) | None | None | SEC-GOV-041 |
| Variant search and process fix after a vulnerability (SSDF RV.3.1, RV.3.3, RV.3.4) | INCIDENT-RESPONSE.md | None | SEC-GOV-043 |
| Root cause weakness recorded for fixed flaws (SSDF RV.3.2) | None | None | SEC-GOV-047 |
| AI vulnerabilities in disclosure and triage | None | None | SEC-GOV-045 |
| Security maintenance schedule with owner and evidence | None | None | SEC-GOV-046 |
| Stated controls versus code | PRIVACY.md | Stated controls versus code | SEC-GOV-053 |
<!-- hullproof:coverage-map:end -->
