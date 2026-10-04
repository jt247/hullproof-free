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

Before editing these files, open the Coverage map in `docs/hullproof/API-SECURITY.md` and `docs/hullproof/BACKEND-SECURITY.md`, find the rows for your change, then read only those requirement blocks (list them with `grep -n '^### SEC-' docs/hullproof/API-SECURITY.md`, then Read with an offset). Do not load a whole document.

1. Validate every request body, query, and header against a server side schema. Reject unknown fields.
2. Every endpoint and server action authorizes the caller itself. Never trust user IDs, roles, or prices sent by the client.
3. Verify webhook signatures before parsing the payload, and make handlers idempotent.
4. Return generic errors to clients. Log detail on the server without secrets or tokens.
5. Add rate limits to authentication, expensive, and AI endpoints.
6. When a check cannot run (a limiter, a bot challenge, a policy lookup), deny the request instead of letting it through (a Pro edition requirement).
