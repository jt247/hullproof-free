---
paths:
  - "**/components/**"
  - "**/app/**/page.*"
  - "**/app/**/layout.*"
  - "**/pages/**"
  - "**/screens/**"
  - "**/hooks/**"
  - "**/*.tsx"
  - "**/*.jsx"
---
# Client code rules

Read `docs/hullproof/SECRETS.md` and `docs/hullproof/FRONTEND-SECURITY.md` when handling secrets or rendering untrusted content.

1. Client code ships to the user. Nothing here is secret and nothing here enforces access.
2. Only values safe for public exposure may use public prefixes such as `NEXT_PUBLIC_` or `EXPO_PUBLIC_`. Service role keys and API secrets never do.
3. Do not render untrusted HTML. When it cannot be avoided, sanitize it with an established library.
4. Store tokens with the platform's secure storage, never in plain local storage on mobile.
