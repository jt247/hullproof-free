---
paths:
  - "**/storage/**"
  - "**/uploads/**"
  - "**/*upload*.*"
  - "**/*bucket*.*"
---
# File storage rules

Read `docs/hullproof/DATA-PROTECTION.md` and `docs/hullproof/BACKEND-SECURITY.md` before editing these files.

1. Buckets are private by default. Serve files through short lived signed URLs after an authorization check.
2. Validate file type by content as well as extension, and enforce size limits on the server.
3. Generate storage paths on the server. Never use a client supplied path or filename directly.
4. Scope access so a user can only read and write their own or their tenant's files.
