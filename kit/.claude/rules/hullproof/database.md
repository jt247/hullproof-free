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

Read `docs/hullproof/DATABASE-SECURITY.md` before editing these files.

1. Enable row level security on every new table in the same migration that creates it, with explicit policies.
2. Never disable row level security or add a permissive policy to get a query working. Report the blocker instead.
3. Use parameterized queries or the query builder. Never build SQL from strings containing input.
4. Service role and admin connections run server side only and bypass policies, so scope every query they run.
5. Migrations that drop, rewrite, or expose data need a backup path and explicit approval.
