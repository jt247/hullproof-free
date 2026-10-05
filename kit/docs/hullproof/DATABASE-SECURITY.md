# Database Security

| Field | Value |
|-------|-------|
| Domain codes | SEC-DB |
| Topics covered | Database Security, Backups |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers access control, privileges, schema change safety and connection security for the application database, plus taking, protecting and test restoring backups. PostgreSQL on Supabase is the primary stack. Query parameterization and other injection controls live in BACKEND-SECURITY.md, privileged key handling in SECRETS.md, Storage bucket policies in DATA-PROTECTION.md, pgvector and embedding store controls in AI-SECURITY.md, and recovery targets, runbooks and migration deploy pipelines in INFRASTRUCTURE-SECURITY.md.

> Research based engineering guidance, not legal advice. A requirement that names a market applies from LAUNCH where that law applies and from GROWTH otherwise, unless its own Applies To or Exceptions field says it is market only.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 11 of the 38 requirements in this domain: every BLOCKER and every CRITICAL requirement in it. Hullproof Pro holds the other 27. Pro covers the database beyond the first exposure checks, including grants, functions, connections, backups, restore tests and how data leaves production.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-DB-001](#sec-db-001-row-level-security-enabled-on-every-exposed-table) | Row level security enabled on every exposed table | BLOCKER | LAUNCH | Database, SaaS, Web, Mobile, API |
| [SEC-DB-002](#sec-db-002-one-explicit-policy-per-allowed-operation-scoped-to-a-role) | One explicit policy per allowed operation, scoped to a role | CRITICAL | LAUNCH | Database, SaaS, Web, Mobile, API |
| [SEC-DB-003](#sec-db-003-new-tables-and-functions-are-not-exposed-by-default-privileges) | New tables and functions are not exposed by default privileges | CRITICAL | LAUNCH | Database (Supabase) |
| [SEC-DB-006](#sec-db-006-rls-policies-never-trust-user-editable-claims) | RLS policies never trust user editable claims | CRITICAL | LAUNCH | Database (Supabase), SaaS |
| [SEC-DB-007](#sec-db-007-views-materialized-views-and-foreign-tables-cannot-bypass-row-level-security) | Views, materialized views and foreign tables cannot bypass row level security | CRITICAL | LAUNCH | Database (Supabase) |
| [SEC-DB-008](#sec-db-008-security-definer-functions-are-not-callable-by-clients) | Security definer functions are not callable by clients | CRITICAL | LAUNCH | Database (Supabase) |
| [SEC-DB-033](#sec-db-033-client-roles-cannot-write-billing-entitlement-verification-role-or-credential-columns) | Client roles cannot write billing, entitlement, verification, role or credential columns | BLOCKER | LAUNCH | Database, SaaS, Web, Mobile, API |
| [SEC-DB-034](#sec-db-034-credential-and-token-tables-have-no-client-grants-and-are-not-reachable-through-the-data-api) | Credential and token tables have no client grants and are not reachable through the Data API | BLOCKER | LAUNCH | Database, SaaS, API |
| [SEC-DB-035](#sec-db-035-content-shown-to-more-than-one-user-without-author-attribution-is-written-only-by-server-code) | Content shown to more than one user without author attribution is written only by server code | BLOCKER | LAUNCH | Database, SaaS, Web, Mobile, API, AI features |
| [SEC-DB-016](#sec-db-016-no-reset-style-rollback-against-remote-databases-or-real-data) | No reset style rollback against remote databases or real data | CRITICAL | LAUNCH | Database (Supabase), Agentic workflow |
| [SEC-DB-017](#sec-db-017-automated-production-database-backups) | Automated production database backups | CRITICAL | LAUNCH | Database |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Row level security on every exposed table | AI-SECURITY.md | None | SEC-DB-001 (more in Pro edition) |
| Policy correctness and testing, including two user tests | AUTH.md | None | SEC-DB-002, SEC-DB-006 (more in Pro edition) |
| Security definer functions and views | BACKEND-SECURITY.md | None | SEC-DB-007, SEC-DB-008 (more in Pro edition) |
| Exposed schemas and the Data API surface | PRIVACY.md, API-SECURITY.md, BACKEND-SECURITY.md | None | SEC-DB-003 (more in Pro edition) |
| Injection | BACKEND-SECURITY.md | None | None in this document |
| Migrations and schema change safety | INFRASTRUCTURE-SECURITY.md, AGENTIC-DEV-SECURITY.md | Migration process | SEC-DB-016 (more in Pro edition) |
| Backups, PITR, restore testing, off provider copies | INFRASTRUCTURE-SECURITY.md, INCIDENT-RESPONSE.md | None | SEC-DB-017 (more in Pro edition) |
| Client writable privileged columns | AUTH.md | Client writable privileged columns | SEC-DB-033 |
| Credential and token tables | None | Credential tables writable through the data API | SEC-DB-034 |
| Shared content integrity | AI-SECURITY.md | Shared content integrity | SEC-DB-035 |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
<!-- hullproof:gates:end -->

---

## Row level security and privileges

### SEC-DB-001: Row level security enabled on every exposed table

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Database, SaaS, Web, Mobile, API |
| Automation | FULL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST |

**Requirement.** Every table in a schema that a client key can reach (on Supabase, every schema exposed through the Data API, `public` by default) MUST have row level security enabled, so that rows are reachable only through explicit policies.

**Why.** A table in an exposed schema with RLS off can be read, changed and deleted by anyone holding the public project key, which ships in every web page and mobile app. Escape found missing or wrong Supabase RLS to be the most common root cause of exposed data in AI built apps, including CVE-2025-48757.

**Implementation.**
- Enable RLS in the same migration that creates the table: `alter table <schema>.<table> enable row level security;`.
- With RLS on and no policy the table is default deny. Grant access only by adding policies (SEC-DB-002).
- Keep tables that no client should ever touch in a schema that is not exposed, rather than relying on RLS alone.
- Default stack: add the Supabase event trigger that enables RLS on every newly created table, so a table an agent or teammate creates is never exposed without it.

**Verify.**
1. Run the Supabase security advisor (`get_advisors` with type security, or Studio Advisors) and confirm zero findings for lint `0013_rls_disabled_in_public` and `0007_policy_exists_rls_disabled`.
2. Run `select schemaname, tablename from pg_tables where schemaname in (<exposed schemas>) and rowsecurity = false;` and expect no rows.
3. For every exposed table, send `GET /rest/v1/<table>?select=*` and an insert with only the publishable key and no user token (curl), and expect an empty result or a permission error.

**Evidence.** Advisor export with no 0013 or 0007 findings, the query output above, and the saved unauthenticated replay results dated before release.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2 [SRC-010]; OWASP ASVS 5.0.0 v5.0.0-8.4.1 (L2, Promoted) [SRC-010]; NIST SSDF 1.1 PW.9.1 [SRC-050]; Supabase Row Level Security [SRC-070]; Supabase Advisors lint 0013 [SRC-076]; Supabase Production Checklist [SRC-075]; Escape State of Vibe Coded Apps [SRC-007] (evidence).

**AI Agent Instruction.** When you create a table in an exposed schema, enable RLS in the same migration and add the policies the feature needs. Never disable RLS, drop a policy, or move a table into an exposed schema to make a query work. If RLS blocks a feature, stop and report which policy is missing. Before marking database work complete, run the security advisor and report any 0013 or 0007 finding as BLOCKER.

---

### SEC-DB-002: One explicit policy per allowed operation, scoped to a role

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database, SaaS, Web, Mobile, API |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, CONFIG REVIEW, DYNAMIC TEST |

**Requirement.** Each operation a client role may perform on an exposed table MUST be allowed by its own policy (select, insert, update, delete) that names its target role with a `TO` clause and restricts rows to the caller's own records or tenant, and every update policy MUST have a `USING` expression and a `WITH CHECK` expression that together keep each updated row owned by the caller and inside the caller's tenant. Two tiers apply to update policies. A policy whose effective check lets a user move a row to another owner or tenant, or write a privilege, status or billing column, is CRITICAL. A policy that omits `WITH CHECK` while its `USING` expression already pins the owner and tenant columns is a hygiene finding rated LOW, because PostgreSQL applies `USING` to the new row when `WITH CHECK` is absent. A policy whose condition is always true MUST NOT apply to user or tenant owned data.

**Why.** RLS that is on but paired with a catch all or `using (true)` policy exposes every row just as RLS off does. An update policy lets a user move a row to another owner or tenant when neither its `WITH CHECK` nor its `USING` expression pins the owner column. PostgreSQL applies `USING` to the new row when `WITH CHECK` is absent, so the omission alone is not exploitable and is rated as hygiene.

**Implementation.**
- Write select, insert, update and delete policies separately, each with `TO authenticated` (or the specific role) instead of the default `PUBLIC`.
- Filter rows on an owner or tenant column compared to `(select auth.uid())` or a tenant claim taken from `app_metadata` (see SEC-DB-006).
- Index every column a policy filters on, so slow policies do not become a denial of service path.
- Use restrictive policies as an extra tenant guard where several permissive policies exist, since permissive policies combine with OR.
- Use random identifiers (for example `gen_random_uuid()`) instead of sequential integers as primary keys for rows whose ID appears in a URL or an API response. This is defense in depth only: the policies are the control, and an unguessable ID never replaces them.
- Owned by SEC-DB-033 in DATABASE-SECURITY.md for this root cause (Client writable privileged columns); report one finding.
- Owned by SEC-DB-035 in DATABASE-SECURITY.md for this root cause (Shared content integrity); report one finding. A client writable table of shared content is rated under that requirement.
- Write `WITH CHECK` explicitly on every update policy, so a reviewer does not have to reason about the implied check. Hygiene findings under this requirement (an omitted `WITH CHECK` where `USING` already pins ownership) are rated LOW. A check that lets the owner or tenant column change is CRITICAL.

**Verify.**
1. Run the security advisor and confirm zero findings for lint `0024_permissive_rls_policy`.
2. Review `pg_policies` for every exposed table: each allowed operation has a policy, each policy has a role other than `public`, no policy on user data has `qual` or `with_check` equal to `true`, and every update policy's `qual` and `with_check` together pin the owner and tenant columns. An update policy with no `with_check` whose `qual` already pins them is a LOW hygiene finding, not CRITICAL.
3. Sign in as user A and attempt to read, update and delete user B's rows through the Data API, and attempt an update that changes the owner column to user B. Expect empty results or errors.

**Evidence.** `pg_policies` export reviewed and signed off in the PR (or the decisions log entry or commit trailer under the Solo builder path in STANDARD.md), advisor export, and the cross user test results.

**Exceptions.** Tables holding data intended to be public to all visitors (for example a published catalogue) may use an always true select policy. Record the table, the reason, and confirm no private column exists on it.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2 [SRC-010]; OWASP ASVS 5.0.0 v5.0.0-8.4.1 (L2, Promoted) [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-04 [SRC-186]; Supabase Row Level Security [SRC-070]; Supabase Advisors lint 0024 [SRC-076]; PostgreSQL 18 Row Security Policies [SRC-077].

**AI Agent Instruction.** Write one policy per operation with a `TO` role and an ownership or tenant condition. Never write `using (true)` or `with check (true)` on a table holding user or tenant data. Always add `WITH CHECK` to update policies. If you cannot express the ownership rule, stop and ask rather than widening the policy.

---

### SEC-DB-003: New tables and functions are not exposed by default privileges

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database (Supabase) |
| Automation | FULL |
| Verification method | CONFIG REVIEW, STATIC ANALYSIS |

**Requirement.** Default privileges in every exposed schema MUST NOT grant table, sequence or function privileges to `anon` or `authenticated` automatically, so each new object is reachable only after an explicit grant in a migration.

**Why.** On existing Supabase projects a new table in `public` receives `select`, `insert`, `update` and `delete` for `anon`, `authenticated` and `service_role` the moment it is created, and a new function receives `execute` [SRC-072]. Plain Postgres differs: a new table is usable only by its owner until privileges are granted [SRC-362], so the exposure comes from the platform's default privilege entries. A table an AI agent creates without a policy is exposed before anyone reviews it.

**Implementation.**
- Add a migration that runs `alter default privileges in schema public revoke all on tables from anon, authenticated;` and the same for sequences and functions, for the roles that create objects (for example `postgres`).
- Grant access explicitly per table in the migration that creates it (a Pro edition requirement).
- Postgres also grants `execute` on new functions to `public` by default [SRC-362], so revoke that too: `alter default privileges for role postgres in schema public revoke execute on functions from public;` [SRC-072].
- Default stack: Supabase documents that it is changing the platform default so that exposure becomes opt in, and its Row Level Security guide says not every project grants these automatically [SRC-072, SRC-070]. Neither page gives dates or says which projects are on the new default, so check `pg_default_acl` on the project rather than assuming.

**Verify.**
1. Query `pg_default_acl` for each exposed schema and confirm no entry grants privileges to `anon` or `authenticated`.
2. In a branch or local database, create a test table without grants and confirm `GET /rest/v1/<table>` with the publishable key returns a permission error.
3. Semgrep or a grep rule in CI fails when no migration contains the default privilege revoke.

**Evidence.** `pg_default_acl` output and the test result from step 2, stored with the release record.

**Exceptions.** Projects where the Data API is disabled (a Pro edition requirement) may skip this. Record that the Data API is off.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2 [SRC-010]; NIST SSDF 1.1 PW.9.1 [SRC-050]; NIST SP 800-53 Rev. 5 AC-6 (ADVISORY) [SRC-062]; Supabase Securing your API [SRC-072]; Supabase Row Level Security [SRC-070]; PostgreSQL 18 Privileges [SRC-362].

**AI Agent Instruction.** Before adding tables to a Supabase project, check `pg_default_acl`. If default privileges still grant to `anon` or `authenticated`, report it and propose the revoke migration. Never rely on default grants for access a feature needs; grant it explicitly.

---

### SEC-DB-006: RLS policies never trust user editable claims

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database (Supabase), SaaS |
| Automation | FULL |
| Verification method | CONFIG REVIEW, STATIC ANALYSIS |

**Requirement.** RLS policies and the functions they call MUST NOT base any access decision on `user_metadata` (`raw_user_meta_data`) or any other value the end user can set; roles and tenant membership MUST come from `app_metadata` or a table the user cannot write. This requirement covers the SQL policy check only; the rule for all authorization code is owned by SEC-AUTHZ-005 in AUTH.md.

**Why.** Users can edit their own `user_metadata` through the auth API. A policy that reads a role or tenant from it lets any user grant themselves admin or another tenant's data.

**Implementation.**
- Store roles and tenant IDs in `app_metadata` (set only by server code) or in a membership table protected by its own RLS.
- Remember that JWT claims stay stale until the token refreshes; revoke access through the membership table when changes must apply at once.

**Verify.**
1. Run the security advisor and confirm zero findings for lint `0015_rls_references_user_metadata`.
2. Grep migrations and `pg_policies` for `user_metadata` and `raw_user_meta_data`.
3. As a signed in user, call `auth.updateUser({ data: { role: 'admin' } })` and confirm no new rows or functions become reachable.

**Evidence.** Advisor export, grep output, and the step 3 test result.

**Exceptions.** None expected. Display only use of `user_metadata` outside policies is out of scope.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1 [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-03 [SRC-186]; Supabase Row Level Security, `auth.jwt()` caution [SRC-070]; Supabase Advisors lint 0015 [SRC-076]. See SEC-AUTHZ-005 for authorization outside SQL.

**AI Agent Instruction.** Never read `user_metadata` in an RLS policy or a function a policy calls; apply SEC-AUTHZ-005 to server authorization code. If an existing policy does, report it as CRITICAL and propose moving the claim to `app_metadata` or a membership table.

---

### SEC-DB-007: Views, materialized views and foreign tables cannot bypass row level security

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database (Supabase) |
| Automation | FULL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST |

**Requirement.** Every view in an exposed schema MUST be created with `security_invoker = true`, a view in an exposed schema MUST NOT expose `auth.users` or other auth schema tables, and a materialized view or foreign table MUST NOT sit in an exposed schema or hold any privilege for `anon` or `authenticated`, because neither kind of object supports row level security.

**Why.** Views created by the `postgres` role run as their owner and skip RLS on the tables they read, so one convenience view can publish every row of a protected table. A materialized view stores a copy of the rows and is never subject to row level security, and the same holds for a foreign table. If either sits in an exposed schema and a client role can select from it, the Data API serves every row to anyone with the publishable key, even when the source tables are locked down.

**Implementation.**
- Create views with `create view ... with (security_invoker = true)` on Postgres 15 and later.
- Keep views that must run as owner in a schema that is not exposed and reach them only from server code.
- Create every materialized view and foreign table in a schema that is not exposed, and run `revoke all on <object> from anon, authenticated;`. Read it from server code with a server only role, and filter by the caller in that code.
- If a client needs a slice of materialized data, serve it from an ordinary table with its own RLS policies (refresh the table from the materialized view in a server side job) or through server code.
- Copy user profile fields into a `profiles` table with its own RLS instead of viewing `auth.users`.

**Verify.**
1. Run the security advisor and confirm zero findings for lints `0002_auth_users_exposed`, `0010_security_definer_view`, `0016` (materialized view in the API) and `0017` (foreign table in the API).
2. Query `pg_class` for views in exposed schemas whose `reloptions` lack `security_invoker=true`.
3. Run `select n.nspname, c.relname, c.relkind from pg_class c join pg_namespace n on n.oid = c.relnamespace where c.relkind in ('m', 'f') and n.nspname in (<exposed schemas>);` and expect no rows. Then run the same query without the schema filter, adding `and (has_table_privilege('anon', c.oid, 'select') or has_table_privilege('authenticated', c.oid, 'select'))`, and expect no rows other than objects recorded under Exceptions.
4. For each materialized view and foreign table the product has, request it through the Data API (`GET /rest/v1/<name>?select=*`, with the `Accept-Profile` header set when it is not in `public`) with the publishable key and again with a signed in user's token. Expect a not found or permission error each time.

**Evidence.** Advisor export, both query outputs, and the saved request results dated before release.

**Exceptions.** A materialized view or foreign table that holds only data public to every visitor may stay readable by `anon` when it is recorded with its reason and a statement that it holds no private column. A view in an exposed schema has no exception.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2 [SRC-010]; Supabase Row Level Security, views [SRC-070]; Supabase Advisors lints 0002, 0010, 0016 and 0017 [SRC-076]; PostgreSQL 18 Row Security Policies [SRC-077].

**AI Agent Instruction.** Always add `with (security_invoker = true)` when creating a view in an exposed schema. Never create a materialized view or foreign table in an exposed schema, and revoke client role privileges on each one you create. Never create a view over `auth.users` in an exposed schema. Report any existing definer view, and any materialized view or foreign table in an exposed schema, as CRITICAL.

---

### SEC-DB-008: Security definer functions are not callable by clients

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database (Supabase) |
| Automation | FULL |
| Verification method | CONFIG REVIEW, STATIC ANALYSIS, DYNAMIC TEST |

**Requirement.** A `security definer` function MUST NOT be reachable by a client through the Data API, and `anon` MUST NOT hold `EXECUTE` on it, except in two cases. First, a policy helper: it lives in a schema that is not exposed through the Data API, `authenticated` holds `USAGE` on that schema and `EXECUTE` on the function so that policies can call it, it derives the caller from `auth.uid()` inside its body, and any tenant or row identifier it takes as a parameter is used only to test what `auth.uid()` may do with it. Second, a client callable function that derives the caller's identity inside its own body from `auth.uid()` or the token claims and takes no user id, tenant id or role as a parameter. A function that trusts an identity, tenant or role passed in by the caller stays CRITICAL. The `search_path` rule in a Pro edition requirement applies to every function in both cases.

**Why.** A security definer function runs with its owner's rights, usually bypassing RLS. Placed in `public`, it becomes an RPC endpoint any client can call. The risk is reachability and trust in caller supplied identity. A membership helper that policies call must be executable by the querying role, so a rule that bans every grant would push builders to move the helper into `public`, which is worse. Supabase's own RBAC example puts such a function in `public`; do not copy that pattern.

**Implementation.**
- Create security definer functions in a private schema (for example `private`) that is not in the Data API exposed schema list.
- Run `revoke execute on function <fn> from public, anon, authenticated;` and grant back only what a case above needs.
- Policy helper pattern: `grant usage on schema private to authenticated;`, then create `private.is_member(target_tenant uuid)` as `language sql stable security definer set search_path = ''` returning `exists (select 1 from private.memberships m where m.tenant_id = target_tenant and m.user_id = (select auth.uid()) and m.status = 'active')`, then `revoke execute on function private.is_member(uuid) from public, anon;` and `grant execute on function private.is_member(uuid) to authenticated;`. Policies call it as `(select private.is_member(tenant_id))`. It passes this requirement because the caller comes from `auth.uid()`, the parameter only names the tenant being tested, and the schema is not exposed.
- Prefer `security invoker` functions unless elevated rights are required, and record why when they are.

**Verify.**
1. Run the security advisor and confirm zero findings for lints `0028` and `0029` (security definer function executable by `anon` or `authenticated`), other than functions recorded in the inventory under Exceptions.
2. Query `pg_proc` joined to `pg_namespace` for `prosecdef = true` in exposed schemas and expect only functions in the recorded inventory of identity deriving functions, each reviewed for caller supplied identity parameters.
3. Query `pg_proc` for `prosecdef = true` where `has_function_privilege('anon', oid, 'execute')` is true and expect no rows other than extension owned functions you record. Read the exposed schema list (Data API settings, or `select rolconfig from pg_roles where rolname = 'authenticator'`) and confirm no schema that holds a policy helper is on it.
4. Call each RPC endpoint with only the publishable key and expect a permission or not found error. Call each policy helper as `POST /rest/v1/rpc/<name>` with a signed in user's token and expect not found.
5. For each function in the inventory, call it as user A with user B's id or tenant id in any parameter, and expect refusal or no effect on B's data. For each policy helper, as user A read and write a tenant B row through the Data API and expect denial.

**Evidence.** Advisor export, query output, the exposed schema list, and the RPC call results.

**Exceptions.** Client callable functions that derive the caller's identity internally, as the second case describes, and policy helpers as the first case describes. Record each one in a function inventory with its reason, its schema and its grantee roles. Advisor lints `0028` and `0029` still list the client callable functions, and each listed function must appear in the inventory.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1 [SRC-010]; NIST SP 800-53 Rev. 5 AC-6(10) (ADVISORY) [SRC-062]; Supabase Row Level Security, security definer functions [SRC-070]; Supabase Advisors lints 0028 and 0029 [SRC-076].

**AI Agent Instruction.** Never create a `security definer` function in `public` or any exposed schema, even when a vendor example does. Put it in a private schema, revoke execute from `public` and `anon`, and grant `authenticated` execute only for a policy helper that takes the tenant id and checks `auth.uid()`. Report the change. If a feature seems to need a client callable definer function that takes a user id, stop and explain the risk.

---

### SEC-DB-033: Client roles cannot write billing, entitlement, verification, role or credential columns

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Database, SaaS, Web, Mobile, API |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST, STATIC ANALYSIS |

**Requirement.** On every table in a schema that a client key can reach, `anon` and `authenticated` MUST NOT hold `INSERT` or `UPDATE`, at table level or column level, on any column that holds billing, entitlement (plan, tier, credits, balance, quota), verification, role, admin flag or credential state. Where one table mixes user editable columns with those columns, client `INSERT` and `UPDATE` grants MUST be limited to a column list of the editable columns, or the privileged columns MUST move to a table that no client role can write. Every table with a client write policy MUST have a recorded answer to two questions: which columns can a user change, and which server decision reads each privileged column. The editable column list is written by hand: a list generated from the table type does not count on a table that holds a privilege, ownership, tenant, plan, balance, status or verification column. Owner and tenant columns stay under the `WITH CHECK` rule of SEC-DB-002.

**Why.** A row level policy limits which rows a user may write, not which columns. A table level `UPDATE` grant lets a user change every column of a row the policy allows, so one `PATCH` to the Data API with the publishable key and the user's own token can set `plan`, `role` or `email_verified` on the user's own row. PostgreSQL allows a column write when the privilege is held on the column or on the whole table, and a column level revoke does not undo a table level grant [SRC-300]. Anything the server later reads from that column as fact (a paid feature check, an admin check, a verified badge) then trusts a value the user chose.

**Implementation.**
- Revoke the table level grant, then grant back by column list in the same migration: `revoke insert, update on <table> from anon, authenticated;` then `grant update (display_name, avatar_url) on <table> to authenticated;`. Do the same for `insert`, because omitted columns take defaults and a listed column can be set by the client.
- Prefer moving billing, entitlement, verification, role and credential state to a table with no client write grant, written only by server code. Supabase calls column level privileges an advanced feature and recommends row level policies plus a dedicated table for user roles [SRC-302].
- Read the privileged value from that server written table or from `app_metadata` (SEC-AUTHZ-005), never from a column the client can update.
- For each table with a client write policy, add a short record to the migration comment or the security decisions log: columns a user can change, privileged columns, and the server code that reads each privileged column.
- Owns the root cause Client writable privileged columns. SEC-AUTHZ-004 (request body allowlists), SEC-AUTHZ-005, SEC-API-126 (entitlement writes), SEC-DB-002 and Pro edition requirements point here; report one finding.
- Default stack: rebuild the final grant and policy set by reading `supabase/migrations` in order (the Hullproof helper `tools/hullproof/helpers/policy_set.py` does this and flags client writable sensitive columns by name, where it is installed). The rebuilt set is a map to check against the live catalog, not proof.

**Verify.**
1. On the live database, list client write grants on the privileged columns: `select table_schema, table_name, column_name, grantee, privilege_type from information_schema.column_privileges where grantee in ('anon', 'authenticated', 'PUBLIC') and privilege_type in ('INSERT', 'UPDATE') and table_schema in (<exposed schemas>);`. A table level grant appears as one row per column [SRC-301]. Compare the rows with the list of privileged columns per table and expect none. The view lists only privileges granted to or by a currently enabled role, so run it as the owner role, or check each privileged column with `has_column_privilege('authenticated', '<schema>.<table>', '<column>', 'UPDATE')`, which also answers true for a table level grant [SRC-301].
2. Read `supabase/migrations` in order and rebuild the final grants and policies for every table with a client write policy (or run the Hullproof helper `tools/hullproof/helpers/policy_set.py` where installed), and confirm no client writable column that holds billing, entitlement, verification, role or credential state remains.
3. Two user negative test. Sign in as user A, then send `PATCH /rest/v1/<table>?id=eq.<A row>` and a `POST` insert through the Data API, each setting every privileged column (`plan`, `role`, `credits`, `verified`, or the project's names). Expect a permission error or an unchanged row. Repeat as user B against user A's row. Also send every column of the table that is not on the editable list, taken from the live column list. Read the rows back with a server credential and confirm no privileged value changed.
4. For every table with a client write policy, confirm the record from Implementation exists. A missing record while the grants are already limited to the editable columns is MEDIUM under the missing record rule in STANDARD.md. A missing record on a table whose client grants cover privileged columns is this requirement's severity.
5. Derive the record instead of accepting it. List the writable columns of every client writable table from the column privileges catalog. For every json or text column that a client role can write, search the code for key reads that feed authorization, billing or verification; any hit moves that column to privileged, whatever the record says.

**Evidence.** The step 1 query output with its date, the rebuilt grant and policy set, the saved negative test requests and responses, the per table record, and the step 5 search results.

**Exceptions.** A column that a user may set and that no authorization, billing or verification decision reads (display name, locale, theme) is out of scope, and the record names it as such. Admin tools and jobs that write these columns run with server credentials, not client roles. A BLOCKER finding cannot be accepted or waived.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.3 (L2), v5.0.0-15.3.3 (L2, Promoted) [SRC-010]; OWASP API Security Top 10 2023 API3:2023 [SRC-021]; OWASP Mass Assignment Cheat Sheet [SRC-030]; PostgreSQL 18 GRANT [SRC-300]; PostgreSQL 18 `column_privileges` and `has_column_privilege` [SRC-301]; Supabase Column Level Security [SRC-302]; Supabase Row Level Security [SRC-070]. Stage LAUNCH because v5.0.0-8.2.3 is not on the promotion list, and Hullproof sets the BLOCKER because a single authenticated request changes money, access or trust state.

**AI Agent Instruction.** When you add a table with a client write policy, revoke table level `insert` and `update` from `anon` and `authenticated` and grant back only the editable columns in the same migration. Put plan, role, credits, verification and credential state in a table that client roles cannot write. Never grant `all` or a table level `update` on a table that holds those columns. Run the two user test before reporting the table done. If a feature seems to need the client to change one of those columns, stop and ask how the server should derive it.

---

### SEC-DB-034: Credential and token tables have no client grants and are not reachable through the Data API

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Database, SaaS, API |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST |

**Requirement.** A table that holds credential hashes, API keys, access or refresh tokens, invite codes, recovery codes, one time codes or signing material MUST sit in a schema that the Data API does not expose, or MUST give `anon` and `authenticated` no `SELECT`, `INSERT`, `UPDATE` or `DELETE` privilege. Credentials MUST be created, read and revoked only by server code. This requirement covers the whole table. Individual privileged columns on a table that users otherwise write are SEC-DB-033.

**Why.** A client `INSERT` on a credential table lets any signed in user write a hash or key they chose, then present the matching secret to the product as a working credential, with no call to the issuance route and none of its checks. A client `SELECT` lets the user read other users' hashes or tokens. Row level policies do not help when the policy itself allows the insert. The result is account takeover or service access with a single request to the Data API.

**Implementation.**
- Create credential tables in a schema that is not in the exposed schema list, or revoke all privileges from `anon` and `authenticated` in the migration that creates the table.
- Issue, verify and revoke credentials in a server route that uses a server credential (SEC-SECRETS-003). Keep the issuance route as the only writer.
- Do not build views over credential tables or over `auth.users` in an exposed schema (SEC-DB-007).
- Store hashes of API keys and codes, not the values (a Pro edition requirement), so a read through any path does not yield a usable secret.
- Related: SEC-AUTH-010 covers bypass routes and flags. A client write path to a credential table is reported once, here.

**Verify.**
1. List tables with credential like columns in the exposed schemas: search `supabase/migrations` and `information_schema.columns` for names containing `hash`, `token`, `secret`, `api_key`, `code`, `invite`, `recovery` or `refresh`, and mark each table that holds a credential.
2. For each marked table, check each client role with `select has_table_privilege('<role>', '<schema>.<table>', 'SELECT, INSERT, UPDATE, DELETE')` for `anon` and `authenticated`, or query `information_schema.role_table_grants`. Expect false or no rows, or confirm the table is in a schema outside the exposed list.
3. As a signed in user, send `GET`, `POST` (with a credential hash you chose), `PATCH` and `DELETE` for each table through the Data API with the publishable key. Expect a permission error or a not found response for every call. Then try to authenticate with the secret that matches the hash you tried to insert and expect refusal.

**Evidence.** The marked table list, the privilege query output, and the saved Data API requests with responses and the failed authentication attempt.

**Exceptions.** None. A user managed credential feature (for example a list of the user's own API keys) shows the user key metadata through a server route or a view that omits the hash, and still gives client roles no write on the credential table. A BLOCKER finding cannot be accepted or waived.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.2, v5.0.0-8.3.1 [SRC-010]; OWASP WSTG 4.2 WSTG-v42-ATHZ-04 [SRC-186]; PostgreSQL 18 GRANT [SRC-300]; Supabase Securing your API [SRC-072]; Supabase Row Level Security [SRC-070]. Stage LAUNCH because a client write mints working credentials.

**AI Agent Instruction.** When you create a table for passwords, hashes, API keys, tokens or codes, put it in a schema that is not exposed, or revoke all client privileges in the same migration. Never add a client insert or select policy on it. Create credentials in a server route only. If a client seems to need a credential row, stop and ask how the server should issue it.

---

### SEC-DB-035: Content shown to more than one user without author attribution is written only by server code

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Database, SaaS, Web, Mobile, API, AI features |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST, CODE REVIEW |

**Requirement.** Content that the product presents to more than one user as its own output, or places in pages and emails that it sends or renders for other users, MUST be written only by server code. That covers cached summaries, shared plans and reports, content on public pages, content placed in emails, and stored model output. `anon` and `authenticated` MUST hold no `INSERT`, `UPDATE` or `DELETE` privilege and no write policy on the tables and columns that hold it. Content written by one member and shown to others under that member's name (comments, messages, a member's own profile text) is outside this requirement and is covered by SEC-DB-002 and the output encoding requirements.

**Why.** Content that every reader sees without attribution carries the product's authority. A client that can write it can plant a phishing link, a fake instruction or a script in what every other reader and every email recipient sees, from one account. Stored model output is the same case, because a user who can write the row can make the product appear to say anything. Stored content shown to every reader gives an attacker control of what other users see and act on, which is why this requirement is BLOCKER. Output that reaches pages and emails without server side validation is the improper output handling risk in the OWASP LLM list [SRC-025].

**Implementation.**
- Split unpublished content from published content. Members write unpublished items to their own table under SEC-DB-002 policies. A server route validates the item, then writes the shared row.
- Revoke `insert`, `update` and `delete` on the shared tables from `anon` and `authenticated`, and keep only `select` policies for readers.
- Generate model output in a server route. Validate it against a schema (a Pro edition requirement) before the server stores it for other readers, and keep raw HTML sinks out of the render path (SEC-WEB-031).
- Build email bodies from server stored content only. Never interpolate a client writable column into a template.
- Owns the root cause Shared content integrity. SEC-DB-002 and SEC-AUTHZ-004 point here.

**Verify.**
1. List every table and column whose content is read by someone other than the writer and is not shown under the writer's name: cached summaries, shared plans and reports, public page content, content used in emails, stored model output. Use the data inventory and trace each reader.
2. For each, query `pg_policies` for `insert`, `update`, `delete` and `all` policies that name `anon`, `authenticated` or `public`, and check `has_table_privilege` for those roles. Expect no write policy and no write grant.
3. Two user test. As user A, `POST` and `PATCH` a marker string into each shared table through the Data API. Expect a permission error. Read as user B and as the server and confirm the marker is absent.
4. For content that members author for other readers, confirm the write goes through a server route that validates it, and trace one value from the database to the page and to an email to confirm it is encoded on output.

**Evidence.** The list from step 1, the `pg_policies` and privilege output, and the saved negative test results.

**Exceptions.** Scope clarification: member authored content shown under the member's name, with the author column pinned by the SEC-DB-002 policy and encoded on render, is outside this requirement. Content written by one member that feeds another member's email, a public page presented as the product's own output, or any summary or model output remains inside it. Record each shared table and which side of that line it falls on. A BLOCKER finding cannot be accepted or waived.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.3 (L2), v5.0.0-15.3.3 (L2, Promoted) [SRC-010]; OWASP API Security Top 10 2023 API3:2023 [SRC-021]; OWASP Top 10 for LLM Applications 2026 LLM10:2026 [SRC-025]; Supabase Row Level Security [SRC-070]. Stage LAUNCH because the impact is stored phishing delivered to every reader, with one request to write it.

**AI Agent Instruction.** When you add a table that stores summaries, plans, reports, public page content, email content or model output, create it with no client write grant and no write policy, and write it from a server route after validation. Never let a client insert or update a row that other users or emails will show as the product's own content. If a feature asks the client to write such a row, stop and ask for a server route design.

---

## Schema changes and migrations

### SEC-DB-016: No reset style rollback against remote databases or real data

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database (Supabase), Agentic workflow |
| Automation | MANUAL |
| Verification method | DOCUMENT REVIEW, CODE REVIEW |

**Requirement.** `supabase migration down`, `supabase db reset` and any equivalent command that drops schemas MUST NOT be run against any remote or linked database, including production, staging and preview projects, or against any database holding real data, except a disposable project recorded under Exceptions. A bad migration MUST be undone with a new forward migration or a backup or PITR restore.

**Why.** `supabase migration down` does not run reverse SQL. It drops all user schemas, re-applies migrations and runs seed files, so pointed at a linked project with `--linked` or `--db-url` it wipes every row. One command can erase a whole remote database with no undo, which is why this is CRITICAL and covers every remote project, not only production.

**Implementation.**
- State the undo route (forward fix or restore) in the PR description of every migration that drops, renames or rewrites data, or in the decisions log entry or commit trailer under the Solo builder path in STANDARD.md.
- Remove production connection strings and linked project refs from scripts and agent environments that run reset commands.
- Write and test the reversing forward migration on a branch or local database before applying it.

**Verify.**
1. Search scripts, CI workflows, package scripts and agent configuration at every scope (project, local, user and parent folder) for `migration down`, `db reset`, `--linked` and `--db-url` and confirm none target a remote, linked or real data database other than a recorded disposable project.
2. Confirm the deployment runbook names forward fix or restore as the only database rollback routes.
3. For each migration that drops, renames or rewrites data, confirm the PR description, or the decisions log entry or commit trailer under the Solo builder path in STANDARD.md, states the undo route.

**Evidence.** Search results, the runbook section, and the undo route record for each destructive migration (PR description, or the decisions log entry or commit trailer under the Solo builder path in STANDARD.md).

**Exceptions.** Out of scope: local databases, and disposable remote projects or branches holding seed data only, each recorded by name. Any other deviation is a CRITICAL exception: written risk acceptance with a named owner, a compensating control and an expiry date.

**References.** NIST SP 800-53 Rev. 5 CP-10 (ADVISORY) [SRC-062]; NIST SSDF 1.2 PS.4.3 (comment version) [SRC-052]; Supabase CLI `migration down` [SRC-135]; Supabase Database Migrations [SRC-133]; Supabase Database Backups, PITR [SRC-131].

**AI Agent Instruction.** Never run `supabase migration down`, `supabase db reset`, or a schema drop against a linked or remote database unless it is a recorded disposable project. To undo a migration, write a new forward migration and test it locally. If a human asks you to roll back production, explain the data loss and propose the forward fix or a restore.

---

## Backups

### SEC-DB-017: Automated production database backups

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DOCUMENT REVIEW |

**Requirement.** The production database MUST be backed up automatically at least daily on a documented schedule, using either provider backups that can be restored on demand or a scheduled self managed dump, and each backup MUST be kept for at least 7 days (Hullproof policy; no external source). A backup that has never been restored is not shown to exist: one backup MUST have been restored into a scratch environment before release, with the date, the backup used and per table row counts recorded. This requirement is CRITICAL wherever the database holds real user data that users cannot recreate.

**Why.** Without automatic backups, a bad migration, a compromised account or a mistaken delete means permanent loss of customer data.

**Implementation.**
- Default stack: Supabase Pro, Team and Enterprise take daily backups. Free projects need a Pro edition requirement.
- Write the schedule, the retention window and where copies live in the project's operations notes.
- Alert when a scheduled backup job fails.

**Verify.**
1. Check the provider backup page or the scheduled job history and confirm a successful backup in the last 24 hours.
2. Confirm the schedule is documented and the retention is at least 7 days for every backup location.
3. Read the restore record: date, backup used and per table row counts, from a restore into a scratch environment (a Pro edition requirement in DATABASE-SECURITY.md sets the recurring test).

**Evidence.** Backup listing or job history, the documented schedule and retention, and the restore record.

**Exceptions.** None at LAUNCH for databases holding real user data. A project whose database holds only seed or rebuildable data records that, with the search that shows it.

**References.** NIST SP 800-53 Rev. 5 CP-9 (ADVISORY) [SRC-062]; NIST SP 800-34 Rev. 1 3.4.2 (ADVISORY) [SRC-053]; Supabase Database Backups [SRC-131]; Supabase Production Checklist, backups and PITR [SRC-075]. Hullproof sets the daily minimum.

**AI Agent Instruction.** Before releasing to production, check that automated backups exist and report the last successful backup time. If none exist, report it as HIGH and do not mark the release ready.
