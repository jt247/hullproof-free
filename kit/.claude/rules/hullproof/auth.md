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

Before editing these files, open the Coverage map in `docs/hullproof/AUTH.md`, find the rows for your change, then read only those requirement blocks (list them with `grep -n '^### SEC-' docs/hullproof/AUTH.md`, then Read with an offset). Do not load a whole document.

1. Check authentication and authorization on the server for every protected route, action, and query. Middleware alone is not enough when handlers can be reached another way (SEC-AUTHZ-002, SEC-API-027).
2. Check ownership and tenant on every resource lookup. A valid session does not grant access to every record (SEC-AUTHZ-003, SEC-AUTHZ-013).
3. Use the platform's auth library for sessions, tokens, and password hashing. Do not hand roll them (SEC-AUTH-001).
4. Revoke every session and refresh token of a user when the password is reset or changed (a Pro edition requirement). Ask for a fresh sign in before an email, phone, MFA or API key change (a Pro edition requirement).
5. Offer MFA to every user and require it for admin accounts (a Pro edition requirement, SEC-AUTHZ-021). From GROWTH, a product that holds payments or personal data requires it for users, and a consumer app records its exception (a Pro edition requirement).
6. Treat any change to role logic, session lifetime, or token validation as a design change and log it.
