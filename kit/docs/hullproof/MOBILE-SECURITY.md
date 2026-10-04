# Mobile Security

| Field | Value |
|-------|-------|
| Domain codes | SEC-MOBILE |
| Topics covered | Mobile Security |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers the client side of iOS and Android apps, written for React Native with Expo: what ships in the bundle, on device storage, transport, deep links, WebViews, release build hygiene, over the air (OTA) updates and in app privacy. The backend the app calls is covered by the other domain documents, because the server, not the app, is the trust boundary. Related controls live elsewhere: OAuth redirects and PKCE for mobile sign in in AUTH.md, in app account deletion in PRIVACY.md, dependency scanning in DEPENDENCIES.md, MFA on the Expo account and forced minimum app versions in INFRASTRUCTURE-SECURITY.md, device attestation for high value requests in API-SECURITY.md, and server side logging in OBSERVABILITY.md.

Stages follow the Hullproof mobile mapping: OWASP MAS profiles L1 and P at LAUNCH, L2 at GROWTH, R at SCALE, with MASWE-0063 (debug features left on) moved to LAUNCH. Weakness IDs are from MASWE v1.0.0; beta IDs are not used.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 2 of the 26 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-MOBILE-001](#sec-mobile-001-the-app-bundle-contains-no-secrets) | The app bundle contains no secrets | BLOCKER | LAUNCH | Mobile |
| [SEC-MOBILE-002](#sec-mobile-002-tokens-are-stored-only-in-keystore-backed-storage) | Tokens are stored only in keystore backed storage | CRITICAL | LAUNCH | Mobile |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Sensitive data storage on device (MASVS-STORAGE-1) | SECRETS.md | None | SEC-MOBILE-020 |
| Prevent leakage of sensitive data (MASVS-STORAGE-2) | PRIVACY.md | None | SEC-MOBILE-003, SEC-MOBILE-008 |
| Strong cryptography following best practice (MASVS-CRYPTO-1) | DATA-PROTECTION.md | None | None in this document |
| Key management (MASVS-CRYPTO-2) | DATA-PROTECTION.md | None | SEC-MOBILE-002 |
| Secure authentication and authorization protocols (MASVS-AUTH-1) | AUTH.md | None | None in this document |
| Secure local authentication and biometrics (MASVS-AUTH-2) | None | None | SEC-MOBILE-016 |
| Additional authentication for sensitive operations (MASVS-AUTH-3) | AUTH.md, PRIVACY.md | None | None in this document |
| Secure network traffic and no cleartext (MASVS-NETWORK-1) | DATA-PROTECTION.md | None | SEC-MOBILE-004 |
| Certificate pinning decision (MASVS-NETWORK-2) | None | None | SEC-MOBILE-013 |
| IPC, exported components and deep links (MASVS-PLATFORM-1) | AUTH.md | None | SEC-MOBILE-019 |
| WebViews (MASVS-PLATFORM-2) | None | None | SEC-MOBILE-007 |
| User interface and app switcher exposure (MASVS-PLATFORM-3) | None | None | SEC-MOBILE-017, SEC-MOBILE-023 |
| Up to date platform version (MASVS-CODE-1) | None | None | SEC-MOBILE-021 |
| Forced update and minimum app version (MASVS-CODE-2) | INFRASTRUCTURE-SECURITY.md | None | None in this document |
| Third party components free of known vulnerabilities (MASVS-CODE-3) | DEPENDENCIES.md | None | None in this document |
| Platform integrity and app attestation (MASVS-RESILIENCE-1) | API-SECURITY.md | None | SEC-MOBILE-018 |
| Anti tampering and update integrity (MASVS-RESILIENCE-2) | None | None | SEC-MOBILE-012 |
| Anti dynamic analysis and debug features in release builds (MASVS-RESILIENCE-4) | None | None | SEC-MOBILE-009 |
| Data minimization and permissions (MASVS-PRIVACY-1) | None | None | SEC-MOBILE-014 |
| Tracking and identification (MASVS-PRIVACY-2) | PRIVACY.md | None | SEC-MOBILE-022 |
| Transparency and store privacy declarations (MASVS-PRIVACY-3) | PRIVACY.md | None | SEC-MOBILE-015 |
| User control over data (MASVS-PRIVACY-4) | PRIVACY.md | None | None in this document |
| Secrets in Expo app config and `EXPO_PUBLIC_` variables | SECRETS.md | None | SEC-MOBILE-001 |
| Expo account, EAS and OTA publish path | INFRASTRUCTURE-SECURITY.md, DEPENDENCIES.md | None | SEC-MOBILE-010, SEC-MOBILE-011 |
| Deep links and mobile auth callbacks | AUTH.md | None | SEC-MOBILE-005, SEC-MOBILE-006 |
| Store account deletion (in app and Google Play web page) | PRIVACY.md | None | None in this document |
| In app purchases with RevenueCat and store notifications | API-SECURITY.md | None | None in this document |
| Push notifications (push tokens, payload content) | DATABASE-SECURITY.md, SECRETS.md | None | SEC-MOBILE-024, SEC-MOBILE-025 |
| Outbound links opened by native code | FRONTEND-SECURITY.md | None | SEC-MOBILE-026 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-MOBILE | Is a mobile build shipped, in a store, or handed to testers in this release? | Check that no app.json, eas.json, ios or android folder, or expo or react-native dependency exists in any workspace, and that no store listing or TestFlight build exists. Record what was checked, or record the owner's written answer. A mobile scaffold counts as No only if it is not deployed and not reachable by real users at the audited commit; a release scope that leaves a live app out does not make the answer No. | SEC-MOBILE-001 (BLOCKER), SEC-MOBILE-002, SEC-MOBILE-003, SEC-MOBILE-004, SEC-MOBILE-005, SEC-MOBILE-006, SEC-MOBILE-007, SEC-MOBILE-008, SEC-MOBILE-009, SEC-MOBILE-010, SEC-MOBILE-011, SEC-MOBILE-012, SEC-MOBILE-013, SEC-MOBILE-014, SEC-MOBILE-015, SEC-MOBILE-016, SEC-MOBILE-017, SEC-MOBILE-018, SEC-MOBILE-019, SEC-MOBILE-020, SEC-MOBILE-021, SEC-MOBILE-022, SEC-MOBILE-023, SEC-MOBILE-024, SEC-MOBILE-025 |
<!-- hullproof:gates:end -->

---

## Mobile Security

### SEC-MOBILE-001: The app bundle contains no secrets

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Mobile |
| Automation | FULL |
| Verification method | SECRET SCAN, CONFIG REVIEW |

**Requirement.** The app bundle, the app config and every public build variable (for example every `EXPO_PUBLIC_` variable) MUST contain only values that are safe to publish, and every paid or privileged API key MUST be used only from a backend or server function.

**Why.** Everything shipped in a mobile app can be extracted from the package by anyone who downloads it. A paid AI key, payment secret key or database service role key in the bundle gives direct access to money, data or production. Escape found leaked OpenAI keys in AI built apps (SRC-007).

**Implementation.**
- Treat every value in the bundle as public. Obfuscation and Hermes bytecode do not hide it.
- Call paid AI, payment, email and other secret keyed APIs through your backend or an Edge Function that holds the key.
- Only publishable values belong in the app, for example the Supabase anon or publishable key, which is safe only because RLS protects the data (DATABASE-SECURITY.md).
- Default stack: `EXPO_PUBLIC_` variables and app config `extra` values are inlined into the bundle. Never put a secret in either. OAuth client secrets also cannot be kept safe in the app (AUTH.md).

**Verify.**
1. Run Gitleaks on the repository, including `.env*`, `app.json`, `app.config.*` and `eas.json`.
2. Build the production bundle with `npx expo export`, then search the output for provider key patterns such as `sk_live`, `sk-ant-` and `sk-`, and run Gitleaks with no git mode over the output folder. Expect zero findings.
3. Review every `EXPO_PUBLIC_` variable and `extra` field and confirm each is safe to publish.

**Evidence.** Gitleaks reports for the repository and the exported bundle with zero findings, and the reviewed list of public variables.

**Exceptions.** None.

**References.** OWASP MASVS v2.1.0 MASVS-STORAGE-1 [SRC-011]; OWASP MASWE v1.0.0 MASWE-0004 [SRC-014]; OWASP ASVS 5.0.0 v5.0.0-13.3.1 [SRC-010]; Expo, Environment variables in Expo (`EXPO_PUBLIC_` exposure) [SRC-084]; Expo AuthSession (`clientSecret` security considerations) [SRC-182]; React Native Security [SRC-120]; Escape, The State of Security of Vibe Coded Apps [SRC-007] (evidence).

**AI Agent Instruction.** Never put a secret key in an `EXPO_PUBLIC_` variable, app config `extra`, a constant or any file that ships in the app. If a feature needs a secret keyed API, build a backend or Edge Function route for it. If you find a secret already in the app, stop, report it as a BLOCKER, and treat the key as leaked under SECRETS.md.

---

### SEC-MOBILE-002: Tokens are stored only in keystore backed storage

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Mobile |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW |

**Requirement.** The app MUST store access tokens, refresh tokens and other credentials only in keystore backed storage (iOS Keychain, Android Keystore) or encrypted with a key held in that storage, and MUST NOT store them unencrypted in AsyncStorage, MMKV, SQLite or plain files.

**Why.** Plain key value stores and files can be read from a compromised or backed up device, and a stolen refresh token gives long lived access to the account.

**Implementation.**
- Use Expo SecureStore, or, when values are too large for SecureStore (values above about 2048 bytes can be rejected, and a Supabase session can exceed that), encrypt the value with an AES key held in SecureStore and keep only the ciphertext in AsyncStorage.
- Handle SecureStore errors for oversized values instead of falling back to plain storage.
- Default stack: pass a SecureStore based storage adapter as `auth.storage` when creating the Supabase client, and do not copy examples that pass AsyncStorage. The client's flow type and redirect handling are in AUTH.md.
- iOS keychain items can survive uninstall and reinstall; clear stale tokens on first launch if the app must start signed out.
- Default stack (checked 2026-10-03): Supabase's Expo tutorial shows a `LargeSecureStore` adapter that keeps an AES 256 key in SecureStore and the ciphertext in AsyncStorage, and notes SecureStore does not support values above 2048 bytes. Its quickstarts pass `AsyncStorage` or an SQLite `localStorage` polyfill as `auth.storage`; those variants store the session unencrypted and fail this requirement.

**Verify.**
1. Run Semgrep rules that flag AsyncStorage, MMKV without an encryption key, SQLite or file writes receiving token or session values that were not first encrypted with a SecureStore held key, and a Supabase client created without a SecureStore based `auth.storage` adapter.
2. Review the auth storage adapter code.
3. On a test device or emulator, inspect app storage after sign in and confirm no token appears in readable form outside SecureStore.

**Evidence.** Semgrep output, the adapter source, and the device inspection record.

**Exceptions.** CRITICAL exception only: in writing, with a named owner, a compensating control and an expiry date.

**References.** OWASP MASVS v2.1.0 MASVS-STORAGE-1 [SRC-011]; OWASP MASWE v1.0.0 MASWE-0003, MASWE-0001 (L2) [SRC-014]; Expo SecureStore [SRC-085]; Supabase Expo React Native tutorial (`LargeSecureStore` pattern) [SRC-123]; React Native Security [SRC-120].

**AI Agent Instruction.** Store tokens and credentials only through the project's SecureStore adapter, or the encrypted adapter whose key is in SecureStore. Never write anything token like to AsyncStorage, MMKV, SQLite or files unencrypted, and never add a fallback to plain storage when SecureStore fails. Report it if the size limit blocks you.
