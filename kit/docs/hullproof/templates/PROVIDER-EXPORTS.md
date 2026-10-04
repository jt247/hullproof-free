# Provider Exports

What to export from each default stack provider so an audit can settle items a repo cannot show. Save the exports in the evidence folder named in `docs/security/STAGE.md`, dated, with the commit or environment they describe. Delete this note when you copy it.

## Redaction rules (apply to every export)

1. Export names, scopes and settings. Never export key values, tokens, passwords or webhook secrets. If a screen shows a value, crop or blur it before saving.
2. Replace personal emails and customer names with a role (for example "member 1, owner"). Keep role, 2FA state and last active date.
3. Keep timestamps, project ids and resource names. Those are what an audit compares.
4. One file per provider and per environment. Write the date, who exported, and the commit or environment it describes on the first line. An export with neither a date nor a commit is not evidence.

## Freshness (Hullproof policy)

An export settles a NOT ASSESSED item only if it is dated no more than 30 days before the audit, and it was taken after the newest migration in the audited commit (a database export older than that migration does not count). The 30 day number is Hullproof policy with no external source. An older or earlier export is repeated, not argued. For the public exposure items (storage buckets, row level security, exposed tables), save the raw query text and its output, not a summary, and also run an anonymous or low privilege request against the named target.

## What an export can and cannot close

An export, screenshot or test log never moves a public exposure BLOCKER to PASS. The BLOCKER classes affected are public buckets and storage (SEC-DATA-019), anonymous data API access (SEC-DB-001, SEC-DB-033, SEC-DB-034, SEC-DB-035), exposed keys and open endpoints. For these rows the checker must run the anonymous request itself against a target you permit, in the same session. If no live target is permitted, the row stays `NOT ASSESSED: NEEDS DYNAMIC TEST` and your export is kept as owner evidence for the human reviewer. An export can close settings rows such as team roles, 2FA, retention and backup plans.

## Exports

| Provider | What to export | How | Requirements it settles |
|----------|----------------|-----|-------------------------|
| Supabase | Security advisor report. List of RLS policies (`select schemaname, tablename, policyname, roles, cmd, qual, with_check from pg_policies`). Column privileges for client roles (`information_schema.column_privileges`). Functions with `security definer` and their execute grants. Buckets with public flags. Auth settings: email confirmation, MFA, leaked password protection, JWT expiry, redirect URLs. Network restrictions. Backup and point in time recovery plan. Log retention. Member list with roles and 2FA. | Dashboard: Advisors, Authentication, Storage, Database. SQL editor for the read only queries. Save query results as CSV. | SEC-AUTH-008, SEC-AUTH-030, SEC-AI-035, SEC-API-056, SEC-CLOUD-012, SEC-DB-016, SEC-DB-017. Owner evidence only: SEC-DB-001, SEC-DB-033, SEC-DB-034, SEC-DB-035 |
| Vercel | Environment variable names and scopes per environment (no values). Team members and roles. Deployment protection and preview access. Domains. Firewall rules. Log drain and log retention. Git integration. | Dashboard: Settings. Environment variable list shows names only if you do not reveal values. | SEC-API-057, SEC-CLOUD-012 |
| Render or Railway | Environment variable names per service. Members and roles. Public versus private services. Database backups and access rules. | Dashboard: service settings and team settings. | SEC-API-057, SEC-CLOUD-012 |
| Cloudflare (R2 and DNS) | Per bucket: public access, `r2.dev` setting, custom domains, CORS. API token scopes. DNS records. Registrar lock and 2FA. | Dashboard: R2 bucket settings, API tokens, DNS. | SEC-CLOUD-012. Owner evidence only: SEC-DATA-019 |
| Resend | Domain records (SPF, DKIM, DMARC) and verification status. API keys with permission and domain scope (no values). Webhook signing setup. | Dashboard: Domains, API Keys, Webhooks. | SEC-CLOUD-012 |
| PostHog | Autocapture and masking settings. Data retention. Members and roles. Which properties carry personal data. | Dashboard: Project settings. | SEC-CLOUD-012 |
| Sentry | Data scrubbing and IP storage settings. Retention. Members and roles. Which projects send user context. | Dashboard: project and organisation settings. | SEC-CLOUD-012 |
| Paystack | Webhook URL and the signature check in use. Key mode (test or live) per environment. Team roles and 2FA. | Dashboard: Settings. | SEC-CLOUD-012 |
| Paddle | Notification destinations and which events they receive. Sandbox versus live separation. Roles and 2FA. | Dashboard: Developer tools, Notifications. | SEC-CLOUD-012 |
| RevenueCat | Webhook authorization header set for every environment (the value stays hidden). API key scopes. Members. | Dashboard: Integrations, Webhooks. | SEC-CLOUD-012 |
| GitHub | Branch protection or rulesets on the default branch. Secret scanning and push protection state. Dependabot or equivalent. Actions permissions and secrets list (names). Members, roles and 2FA. Deploy keys. | Repository settings and organisation settings. `gh api` with a read only token works for the same data. | SEC-AGENT-014, SEC-CLOUD-012, SEC-SECRETS-004, SEC-SUPPLY-016 |
| Expo (EAS) | Secret names, access tokens by name, members and roles. | Dashboard: project settings and access tokens. | SEC-CLOUD-012 |
| AI providers | Keys by name, project and scope (no values). Spend limits. Data retention and training setting. Members and roles. | Provider console: API keys, limits, data controls. | SEC-AI-006, SEC-CLOUD-012 |
| Domain registrar | Registrar lock, 2FA on the account, nameservers, expiry date. | Registrar account settings. | SEC-CLOUD-012 |
| Developer machine and coding agent settings | The names (never values) of environment variables in the agent's shell, and the project ids of local environment files, compared with the production project ids in `STAGE.md`. | Your terminal: `env` names only, and the local env file key names. | SEC-AGENT-011 |

## Plan unknown

If you do not know which plan a provider account is on, export the billing page and the feature page for the setting in question. A setting that the plan does not offer is recorded as "not available on this plan", which is a finding or an accepted risk, not a blank.
