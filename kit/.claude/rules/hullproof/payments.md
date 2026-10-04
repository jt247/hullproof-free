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

Before editing these files, open the Coverage map in `docs/hullproof/API-SECURITY.md`, find the rows for your change, then read only those requirement blocks (list them with `grep -n '^### SEC-' docs/hullproof/API-SECURITY.md`, then Read with an offset). Do not load a whole document.

1. Prices, plans, and entitlements come from the server or the payment provider, never from the client (SEC-API-125).
2. Grant entitlements only from a verified webhook or a server side provider lookup, never from a client redirect (SEC-API-126).
3. Verify webhook signatures and handle duplicate deliveries (SEC-API-101, SEC-API-128). Authenticate RevenueCat webhooks and Google Play push messages too (SEC-API-132, SEC-API-134).
4. Never log or store card data. Let the provider handle it (SEC-API-137).
