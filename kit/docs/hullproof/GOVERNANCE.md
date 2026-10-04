# Governance and Secure Development

| Field | Value |
|-------|-------|
| Domain codes | SEC-GOV |
| Topics covered | Architecture, Threat Modeling, secure development process (NIST SSDF 1.1), Vulnerability Management |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document sets the process controls around the code: how the architecture is recorded, when and how threats are modeled, who owns which security duty, how changes are reviewed and released, which privacy records and regulator filings a product needs per market, and how vulnerabilities are received, triaged and fixed. Privacy governance lives in PRIVACY.md. Technical controls live in the domain documents: AUTH.md, API-SECURITY.md, BACKEND-SECURITY.md, FRONTEND-SECURITY.md, DATABASE-SECURITY.md, DATA-PROTECTION.md, PRIVACY.md, SECRETS.md, AI-SECURITY.md, AGENTIC-DEV-SECURITY.md, DEPENDENCIES.md, INFRASTRUCTURE-SECURITY.md, MOBILE-SECURITY.md, OBSERVABILITY.md and INCIDENT-RESPONSE.md. The process stages these requirements plug into are defined in HULLPROOF.md.

> Research based engineering guidance, not legal advice. Requirements that name a law and a market (NG, EU, ZA, KE, GH) are Hullproof's engineering reading of official legal texts. Meeting them does not by itself make a product compliant, and a qualified lawyer in each market has the final word.

Market codes: NG = Nigeria (NDPA 2023 with GAID 2025), EU = GDPR, ZA = South Africa (POPIA), KE = Kenya (DPA 2019 and 2021 Regulations), GH = Ghana (Act 843). A requirement that names a market applies from LAUNCH where that law applies and from GROWTH otherwise, as the security standard sets out under Stages, unless its own Applies To or Exceptions field says it is market only (for example a Pro edition requirement). A No answer to a market gate marks NOT APPLICABLE only the requirements that depend on that market alone.

<!-- hullproof:index:start -->

> **Free edition.** All 37 requirements in this domain are in Hullproof Pro, because none of them is a BLOCKER or a CRITICAL requirement. Pro covers how security decisions are made and recorded, including design review, threat models, risk records, release criteria and how vulnerability reports are triaged.

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
| Authorization and validation decided on the server, never only in client code | AUTH.md, API-SECURITY.md | None | None in this document |
| One server only data access layer that authorizes each read | BACKEND-SECURITY.md | None | None in this document |
| Supporting toolchains: required checks, pinned and least privilege CI, evidence (SSDF PO.3.1, PO.3.2, PO.3.3) | DEPENDENCIES.md, SECRETS.md, AGENTIC-DEV-SECURITY.md | None | None in this document |
| Secure development environments, separated and hardened (SSDF PO.5.1, PO.5.2) | INFRASTRUCTURE-SECURITY.md, AGENTIC-DEV-SECURITY.md, DEPENDENCIES.md | None | None in this document |
| Protect code from unauthorized access and tampering (SSDF PS.1.1) | DEPENDENCIES.md, AGENTIC-DEV-SECURITY.md | None | None in this document |
| Release integrity verification (SSDF PS.2.1) | DEPENDENCIES.md | None | None in this document |
| Archive each release and its component inventory (SSDF PS.3.1, PS.3.2) | DEPENDENCIES.md, INFRASTRUCTURE-SECURITY.md | None | None in this document |
| Secure coding practices (SSDF PW.5.1) | API-SECURITY.md, BACKEND-SECURITY.md, DEPENDENCIES.md | None | None in this document |
| Build and pipeline configuration reviewed (SSDF PW.6.1, PW.6.2) | DEPENDENCIES.md | None | None in this document |
<!-- hullproof:coverage-map:end -->
