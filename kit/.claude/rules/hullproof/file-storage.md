---
paths:
  - "**/storage/**"
  - "**/uploads/**"
  - "**/*upload*.*"
  - "**/*bucket*.*"
---
# File storage rules

Before editing these files, open the Coverage map in `docs/hullproof/DATA-PROTECTION.md` and `docs/hullproof/BACKEND-SECURITY.md`, find the rows for your change, then read only those requirement blocks (list them with `grep -n '^### SEC-' docs/hullproof/DATA-PROTECTION.md`, then Read with an offset). Do not load a whole document.

1. Buckets are private by default. Serve files through short lived signed URLs after an authorization check (SEC-DATA-019, a Pro edition requirement).
2. Validate file type by content as well as extension, and enforce size limits on the server.
3. Generate storage paths on the server. Never use a client supplied path or filename directly, and resolve a key sent by the client to a record issued to the caller (SEC-DATA-059).
4. Scope access so a user can only read and write their own or their tenant's files (SEC-DATA-020).
5. Never serve an upload as active content from the app origin (SEC-API-045).
