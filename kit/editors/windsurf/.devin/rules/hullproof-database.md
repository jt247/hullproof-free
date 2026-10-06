---
trigger: glob
globs: **/*.sql, **/migrations/**, **/supabase/**, **/prisma/**, **/drizzle/**, **/db/**, **/schema.*
---
# Hullproof: databases, migrations and row level security

Advisory text for Windsurf and Devin, not enforced. Read DATABASE-SECURITY.md in docs/hullproof/ before editing these files. Start at the Coverage map and read only the requirement you need. The stage comes from docs/security/STAGE.md. Every BLOCKER applies from LAUNCH.

## Before you write code in this area

1. LAUNCH. Enable row level security on every exposed table in the migration that creates it (SEC-DB-001), with one explicit policy per allowed operation scoped to a role (SEC-DB-002).
2. LAUNCH. New tables and functions are not exposed by default privileges (SEC-DB-003). Policies never trust user editable claims (SEC-DB-006). Views, materialized views and foreign tables cannot bypass row level security (SEC-DB-007). Security definer functions are not callable by clients, except a policy helper in an unexposed schema (SEC-DB-008).
3. LAUNCH. Client roles cannot write billing, entitlement, role, verification or credential columns (SEC-DB-033). Credential and token tables have no client grants (SEC-DB-034).
4. LAUNCH, if the product has tenants. Tenant tables carry a tenant column and membership based policies (SEC-AUTHZ-014).
5. LAUNCH. Service role and admin connections run server side only, and every query they run is scoped (SEC-SECRETS-003, SEC-AUTHZ-007).
6. LAUNCH. Never run a reset style rollback against a remote database or real data (SEC-DB-016). A migration that drops, rewrites or exposes data needs a backup path and explicit approval from the owner.
7. GROWTH adds. Allow and deny tests for every policy, application connections subject to row level security, TLS and network restriction on direct connections.

## Refuse

- Disabling row level security, or adding a permissive policy to get a query working.
- Granting client roles write access to billing, role or credential columns.
- Building SQL from strings that contain input.

If a control blocks you, stop and report it with the ASSUMPTION, VERIFIED or SUSPECTED labels and a severity from docs/hullproof/STANDARD.md.
