# Infrastructure Security

| Field | Value |
|-------|-------|
| Domain codes | SEC-CLOUD |
| Topics covered | Infrastructure, Disaster Recovery, Containers, Cloud IAM, Production Deployment |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers the hosting layer under the application: environment separation and platform settings, recovery targets and drills, container images, the human and machine identities that control the platforms, and how a change reaches production and gets reverted. At LAUNCH it targets managed platforms (Vercel, Supabase, Render, Expo); self managed hosts and container runtime hardening start at SCALE. TLS on endpoints is in DATA-PROTECTION.md, database network restrictions and backups are in DATABASE-SECURITY.md, secret storage and rotation are in SECRETS.md, coding agent credentials are in AGENTIC-DEV-SECURITY.md, debug and test routes in production builds are in BACKEND-SECURITY.md, and CI, repository and dependency controls are in DEPENDENCIES.md.

> Research based engineering guidance, not legal advice.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 2 of the 42 requirements in this domain: every BLOCKER and every CRITICAL requirement that applies at LAUNCH. Requirement IDs mentioned here but not listed are part of Hullproof Pro.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-CLOUD-012](#sec-cloud-012-mfa-on-every-privileged-platform-account) | MFA on every privileged platform account | CRITICAL | LAUNCH | SaaS, Web, API, Database, Serverless, Cloud, Mobile, AI features |
| [SEC-CLOUD-016](#sec-cloud-016-no-secrets-in-container-images) | No secrets in container images | BLOCKER | LAUNCH | Containers |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Environment separation (development, preview, staging, production) | SECRETS.md | None | SEC-CLOUD-001, SEC-CLOUD-002, SEC-CLOUD-026 |
| Preview and non production access control | None | None | SEC-CLOUD-003 |
| Cloud and platform IAM (roles, least privilege, console MFA, access reviews, offboarding) | DEPENDENCIES.md, AGENTIC-DEV-SECURITY.md | None | SEC-CLOUD-012, SEC-CLOUD-013, SEC-CLOUD-014, SEC-CLOUD-035, SEC-CLOUD-036 |
| CI and deploy credentials (OIDC where supported) | SECRETS.md, DEPENDENCIES.md | None | SEC-CLOUD-015, SEC-CLOUD-022, SEC-CLOUD-032 |
| Network exposure (public endpoints, admin ports, database network restrictions) | DATABASE-SECURITY.md, API-SECURITY.md, BACKEND-SECURITY.md | None | SEC-CLOUD-006, SEC-CLOUD-007, SEC-CLOUD-037 |
| DNS and domains (subdomain takeover, registrar lock, DNS change and certificate monitoring, DNSSEC) | GOVERNANCE.md, FRONTEND-SECURITY.md | None | SEC-CLOUD-004, SEC-CLOUD-038, SEC-CLOUD-039, SEC-CLOUD-044, SEC-CLOUD-045 |
| TLS termination and certificates | DATA-PROTECTION.md, DATABASE-SECURITY.md | None | None in this document |
| Serverless function configuration (timeouts, memory, concurrency, environment variables) | GOVERNANCE.md, SECRETS.md | None | SEC-CLOUD-040 |
| Containers (image provenance, base images, non root, scanning) | None | None | SEC-CLOUD-016, SEC-CLOUD-017, SEC-CLOUD-018, SEC-CLOUD-019, SEC-CLOUD-020, SEC-CLOUD-021, SEC-CLOUD-023, SEC-CLOUD-024, SEC-CLOUD-025, SEC-CLOUD-043 |
| Infrastructure as code review | DEPENDENCIES.md, DATABASE-SECURITY.md | None | SEC-CLOUD-005, SEC-CLOUD-008 |
| Production deployment process and rollback | DEPENDENCIES.md, DATABASE-SECURITY.md, SECRETS.md, GOVERNANCE.md | None | SEC-CLOUD-027, SEC-CLOUD-028, SEC-CLOUD-033, SEC-CLOUD-034 |
| Disaster recovery (RTO, RPO, drills) | DATABASE-SECURITY.md | None | SEC-CLOUD-009, SEC-CLOUD-010, SEC-CLOUD-011 |
| Platform cost and budget alerts | AI-SECURITY.md, OBSERVABILITY.md, GOVERNANCE.md | None | SEC-CLOUD-041 |
| Logging of platform and admin actions | OBSERVABILITY.md | None | SEC-CLOUD-042 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-MOBILE | Is a mobile build shipped, in a store, or handed to testers in this release? | Check that no app.json, eas.json, ios or android folder, or expo or react-native dependency exists in any workspace, and that no store listing or TestFlight build exists. Record what was checked, or record the owner's written answer. A mobile scaffold counts as No only if it is not deployed and not reachable by real users at the audited commit; a release scope that leaves a live app out does not make the answer No. | SEC-CLOUD-034 |
| GATE-CONTAINERS | Does the project build container images? | Find no Dockerfile, Containerfile or compose file in the repository, and no image build or registry push in the CI workflows. Record the find command and the workflow files read, or record the owner's written answer. Platforms that deploy from source (for example Vercel) do not build images you own. | SEC-CLOUD-016 (BLOCKER), SEC-CLOUD-017, SEC-CLOUD-018, SEC-CLOUD-019, SEC-CLOUD-020, SEC-CLOUD-021, SEC-CLOUD-022, SEC-CLOUD-023, SEC-CLOUD-024, SEC-CLOUD-025, SEC-CLOUD-043 |
<!-- hullproof:gates:end -->

---

## Cloud IAM

### SEC-CLOUD-012: MFA on every privileged platform account

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | SaaS, Web, API, Database, Serverless, Cloud, Mobile, AI features |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW |

**Requirement.** Every account that holds a privileged capability on the platforms that run or control production (database, hosting, source control, DNS, domain registrar, AI provider, payment provider dashboard and app stores) MUST have MFA enabled, and MFA MUST be enforced for all members where the platform offers an enforcement setting. Privileged means capability, not role name: every member who can read a production key, deploy to production, or change production data, DNS or billing counts as privileged whatever the role is called, and MFA is enforced for each or the access is removed.

**Why.** One phished owner password can hand over the database, deployments, secrets and domain in a single step, and can be used to delete the project and its backups.

**Implementation.**
- Default stack: Supabase organization MFA enforcement, Vercel team 2FA requirement, Render workspace 2FA enforcement, GitHub organization 2FA requirement, plus MFA on the domain registrar and DNS provider.
- Prefer authenticator apps or passkeys to SMS.
- Repository member 2FA is also covered in SEC-SUPPLY-023.
- Default list of privileged account types: database platform owner and admin, hosting owner and admin, source control organization owner and repository admin, CI settings admin, DNS provider, domain registrar, AI provider organization owner, payment provider dashboard owner and admin, email sending provider owner, and the Apple and Google Play developer accounts. Add any other platform that can change production data or secrets.

**Verify.**
1. For each platform, read the enforcement setting or list every member with their capabilities (read production keys, deploy, change data, DNS or billing) and their MFA status, including members whose role is named developer, contractor or similar.
2. Confirm the registrar and DNS accounts have MFA by checking their security settings.

**Evidence.** Per platform export or screenshot of MFA status and enforcement settings, dated.

**Exceptions.** A platform that offers no MFA is recorded with the compensating control (for example a unique long password in a password manager and login alerts) and an expiry date for review.

**References.** NIST SP 800-53 IA-2(1) [SRC-062]; CISA Secure by Design, SbD Tactic: Mandate MFA for privileged users [SRC-063]; Supabase Production Checklist, Account MFA [SRC-075]; Render Login Settings, Secure login enforcement [SRC-153]; NIST SSDF 1.1 PO.5.2 [SRC-050].

**AI Agent Instruction.** When auditing, check MFA status on every production platform you can query and report each account without it as CRITICAL. Never create a platform account or token for an account that lacks MFA.

---

## Containers

### SEC-CLOUD-016: No secrets in container images

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Containers |
| Automation | FULL |
| Verification method | SECRET SCAN, STATIC ANALYSIS |

**Requirement.** Container images MUST NOT contain secrets in any layer, build argument, or environment variable baked into the image; secrets MUST be injected at run time by the platform.

**Why.** Anyone who can pull an image can read every layer and its build history, so a secret copied in and deleted in a later layer is still there.

**Implementation.**
- Pass secrets as runtime environment variables or secret files from the platform, not `ENV` or `ARG` in the Dockerfile.
- Use build secret mounts for build time credentials so they never land in a layer.
- Add `.env*` and credential files to `.dockerignore`.

**Verify.**
1. Run a secret scanner such as Trivy or Gitleaks against the built image.
2. Inspect `docker history --no-trunc` output and the Dockerfile for secret values in `ENV`, `ARG` or `COPY`.

**Evidence.** Clean image scan report and the Dockerfile review.

**Exceptions.** Not applicable when the repository builds and deploys no container images; record the search (Dockerfiles, container build configuration, platform image settings) that shows it.

**References.** OWASP ASVS 5.0.0 v5.0.0-13.3.1 (Level 2, promoted to LAUNCH) [SRC-010]; NIST SP 800-190 section 4.1.4 [SRC-155]; OWASP Cheat Sheet Series, Docker Security, Rule 12 [SRC-030].

**AI Agent Instruction.** Never put a secret in a Dockerfile, build argument or image environment. If you find one, stop and report it as a BLOCKER and treat the secret as leaked.
