---
paths:
  - "**/api/**"
  - "**/routes/**"
  - "**/actions/**"
  - "**/*action*.*"
  - "**/server/**"
  - "**/webhooks/**"
  - "**/functions/**"
---
# API and backend rules

Read `docs/hullproof/API-SECURITY.md` and `docs/hullproof/BACKEND-SECURITY.md` before editing these files.

1. Validate every request body, query, and header against a server side schema. Reject unknown fields.
2. Every endpoint and server action authorizes the caller itself. Never trust user IDs, roles, or prices sent by the client.
3. Verify webhook signatures before parsing the payload, and make handlers idempotent.
4. Return generic errors to clients. Log detail on the server without secrets or tokens.
5. Add rate limits to authentication, expensive, and AI endpoints.
