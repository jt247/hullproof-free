---
paths:
  - "**/billing/**"
  - "**/payments/**"
  - "**/checkout/**"
  - "**/subscriptions/**"
  - "**/*paddle*.*"
  - "**/*stripe*.*"
  - "**/*paystack*.*"
  - "**/*revenuecat*.*"
---
# Payments rules

Read `docs/hullproof/API-SECURITY.md` before editing these files.

1. Prices, plans, and entitlements come from the server or the payment provider, never from the client.
2. Grant entitlements only from a verified webhook or a server side provider lookup, never from a client redirect.
3. Verify webhook signatures and handle duplicate deliveries.
4. Never log or store card data. Let the provider handle it.
