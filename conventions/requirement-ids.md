# Requirement ID Convention

## Format

`SEC-[DOMAIN]-[NUMBER]`

For example: `SEC-AUTH-001`, `SEC-API-020`, `SEC-DB-008`, `SEC-AI-015`.

## Domain codes

| Code | Domain | Document |
|------|--------|----------|
| GOV | Governance and secure development process | docs/hullproof/GOVERNANCE.md, PRIVACY.md (privacy governance) |
| AUTH | Authentication, identity, sessions | docs/hullproof/AUTH.md |
| AUTHZ | Authorization, access control, tenancy | docs/hullproof/AUTH.md |
| API | APIs, backend services, webhooks, uploads | docs/hullproof/API-SECURITY.md, BACKEND-SECURITY.md |
| WEB | Browser side controls | docs/hullproof/FRONTEND-SECURITY.md |
| DB | Databases | docs/hullproof/DATABASE-SECURITY.md |
| DATA | Data protection, privacy, encryption, storage | docs/hullproof/DATA-PROTECTION.md, PRIVACY.md |
| SECRETS | Secrets management | docs/hullproof/SECRETS.md |
| AI | AI features inside the product | docs/hullproof/AI-SECURITY.md |
| AGENT | AI assisted and agentic development workflow | docs/hullproof/AGENTIC-DEV-SECURITY.md |
| SUPPLY | Dependencies, CI/CD, build integrity | docs/hullproof/DEPENDENCIES.md |
| CLOUD | Cloud, serverless, infrastructure | docs/hullproof/INFRASTRUCTURE-SECURITY.md |
| MOBILE | Mobile applications | docs/hullproof/MOBILE-SECURITY.md |
| LOG | Logging, monitoring, incident response | docs/hullproof/OBSERVABILITY.md, INCIDENT-RESPONSE.md |

Adding a code requires a CHANGELOG entry. Codes are never renamed. A code describes the domain, not the file: a document may hold more than one code, and a code may span documents.

## Numbering rules

1. Numbers are three digits and zero padded. They may be allocated in blocks per topic area (for example SEC-API-001 to 099 for core API controls, SEC-API-101 onward for abuse and payments), so gaps between blocks are expected.
2. IDs are issued once, in a single Hullproof registry. Both editions use the same ID for the same requirement. The free edition publishes a subset of IDs.
3. An ID is never reused or renumbered. A retired requirement keeps its ID with status `deprecated` and a pointer to its replacement, if one exists.
4. Gaps in the free edition are expected, because it publishes a subset.
5. A change of meaning needs a new ID. Wording fixes keep the existing ID.
