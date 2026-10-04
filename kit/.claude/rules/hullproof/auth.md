---
paths:
  - "**/auth/**"
  - "**/*auth*.*"
  - "**/*session*.*"
  - "**/middleware.*"
  - "**/login/**"
  - "**/signup/**"
---
# Auth rules

Read `docs/hullproof/AUTH.md` before editing these files.

1. Check authentication and authorization on the server for every protected route, action, and query. Middleware alone is not enough when handlers can be reached another way.
2. Check ownership and tenant on every resource lookup. A valid session does not grant access to every record.
3. Use the platform's auth library for sessions, tokens, and password hashing. Do not hand roll them.
4. Treat any change to role logic, session lifetime, or token validation as a design change and log it.
