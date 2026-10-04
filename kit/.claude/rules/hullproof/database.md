---
paths:
  - "**/*.sql"
  - "**/migrations/**"
  - "**/supabase/**"
  - "**/prisma/**"
  - "**/drizzle/**"
  - "**/db/**"
  - "**/schema.*"
---
# Database rules

Before editing these files, open the Coverage map in `docs/hullproof/DATABASE-SECURITY.md`, find the rows for your change, then read only those requirement blocks (list them with `grep -n '^### SEC-' docs/hullproof/DATABASE-SECURITY.md`, then Read with an offset). Do not load a whole document.

1. Enable row level security on every new table in the same migration that creates it, with explicit policies (SEC-DB-001, SEC-DB-002).
2. Never disable row level security or add a permissive policy to get a query working. Report the blocker instead.
3. Use parameterized queries or the query builder. Never build SQL from strings containing input.
4. Service role and admin connections run server side only and bypass policies, so scope every query they run.
5. Do not give client roles write access to billing, entitlement, role or credential columns, and keep credential and token tables off the Data API (SEC-DB-033, SEC-DB-034). Content shown to several users is written by server code only (SEC-DB-035).
6. Migrations that drop, rewrite, or expose data need a backup path and explicit approval. Never run a reset style rollback against a remote database (SEC-DB-016).
