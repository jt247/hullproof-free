# Coding agent connector evidence

A hosted connector (an MCP server or integration that a coding agent reaches through the developer's own account) holds its credential at the provider, not in a file or an environment variable. A search of the repository and of the agent settings finds nothing, and the provider's audit log shows every call as the account owner. This page says what the owner exports for each kind of provider, and how to compare the exports with the agent side inventory using counts only. It backs a Pro edition requirement (MCP and connector inventory), SEC-AGENT-011 (production credentials reachable by an agent) and SEC-AGENT-014 (agents and production changes).

Everything here is run by the owner, in the owner's own session or terminal. The skills and agents cannot do it: the grants live behind the owner's login, and the read only hook allows no network command except a permitted live check. The result is an owner export, which settles a row only under the freshness rule in the standard (names the date, no more than 30 days old, taken after the newest migration).

Never put a token, a client secret, an authorization URL or a screenshot that shows one into a report or into an agent session. Export names, scopes, resources and dates.

## 1. What to export

Take one export per provider account that a coding agent can act through. Do this for every account type: a personal account, an organization, a project or workspace level token.

| Provider kind | Export from the provider | Fields to keep |
|---------------|--------------------------|----------------|
| Source host (repositories, pull requests, workflows) | The list of authorized OAuth applications and installed apps for the account and for the organization, the list of personal access tokens and fine grained tokens, and the third party access policy of the organization | Application name, who authorized it, repository selection (all or named), permissions (read, write, admin), last used, expiry |
| Hosting and deploy platform | The list of integrations, connected apps and access tokens for the team and for the account | Name, scope (team, project, environment), permission level, created, last used, expiry |
| Database platform | The list of access tokens and of applications authorized to manage projects, for the account and the organization | Name, organization or project scope, permission, last used |
| Payments and billing | The list of API keys and of connected apps, and the key's allowed operations | Name, mode (test or live), permissions (read or write), restricted or not |
| Email, analytics and error tracking | The list of API keys, OAuth grants and connected apps | Name, permissions, domain or project scope, last used |
| Workspace tools (documents, chat, tickets, design) | The list of connected apps for the account and the workspace admin view of installed apps | App name, who authorized it, workspace or folder scope, read or write |
| Cloud account (AWS, Google Cloud, Azure) | The identity and access list of users, roles, service accounts, access keys and federated trusts | Principal, attached permissions, last used, key age |
| The coding agent itself | The list of connectors and MCP servers the agent loads at account, project and user scope (the connectors page of the agent account, the MCP list command in a session, and the editor's MCP settings file) | Name, endpoint host, authorization type, account it acts as, enabled or not |

Menu names change between releases. Search the provider's current documentation for "authorized applications", "connected apps", "access tokens" or "OAuth grants". If a provider has no such list, record "no list offered" and treat every connector to that provider as unverified (a Pro edition requirement).

## 2. Build the two lists

Write two plain text files in the evidence folder, one line per grant, tab separated, with the same three fields: `provider`, `account or organization`, `application name`. Keep scope text in a fourth column that the comparison ignores.

1. `connectors-agent.txt`: what the agent side shows (the last row of the table above), plus every connector named in the MCP inventory.
2. `connectors-provider.txt`: what the providers show as authorized to act for those accounts (the other rows).

Use only names. A line must never hold a token or an authorization URL.

## 3. Compare with counts

```bash
cd docs/security/evidence/2026-01-31
cut -f1-3 connectors-agent.txt | sort -u > a.sorted
cut -f1-3 connectors-provider.txt | sort -u > p.sorted
printf 'agent side: %s\nprovider side: %s\n' "$(wc -l < a.sorted | tr -d ' ')" "$(wc -l < p.sorted | tr -d ' ')"
printf 'authorized at a provider, not in the agent inventory: %s\n' "$(comm -13 a.sorted p.sorted | wc -l | tr -d ' ')"
printf 'in the agent inventory, not authorized at a provider: %s\n' "$(comm -23 a.sorted p.sorted | wc -l | tr -d ' ')"
printf 'grants with write or admin scope: %s\n' "$(awk -F'\t' 'tolower($4) ~ /(write|admin|delete|owner|full)/' connectors-provider.txt | wc -l | tr -d ' ')"
```

How to read the numbers:

| Count | Meaning | Next step |
|-------|---------|-----------|
| Authorized at a provider, not in the inventory | A connector exists that nobody listed. An agent may already use it. | List the names (`comm -13 a.sorted p.sorted`). Add each to the inventory with its scope, or revoke it. a Pro edition requirement stays open until the count is 0. |
| In the inventory, not authorized at a provider | The inventory is stale, or the connector uses a different account than the one you exported. | Find which account it acts as. Remove the line or add the missing export. |
| Grants with write or admin scope | Each one lets an agent change the provider's data. | For every one on a production resource, record the reason, or reduce the scope to read only (SEC-AGENT-011, SEC-AGENT-014). Production write access reached through a connector is treated as an agent credential. |

## 4. Check that a connector can actually be cut off

For each connector that reaches production, once, in a staging account if the provider offers one:

1. Note the time. Revoke the grant at the provider (not in the agent).
2. In a new agent session, ask it to run one read only call through that connector. Expect a refusal or an authentication error.
3. Record the time, the connector name and the result. Do not reconnect it until the scope is decided.

## 5. Attribute provider events to agent sessions

The provider's audit log names the owner, not the agent. To see what agent sessions changed, take the audit log export for the period, keep the write events (create, update, delete, deploy, rotate) made by the owner's account, and count how many fall inside the time ranges of agent sessions (from the agent's session history). Treat any such write that is not explained by a recorded human action as an agent change (SEC-AGENT-014). Keep the counts and the event names, not the event bodies.

| Count to record | Where it goes |
|-----------------|---------------|
| Write events by the owner account in the period | Evidence folder, per provider |
| Of those, inside an agent session window | The report, under the agent requirements |
| Of those, without a recorded human action | A finding when above 0 |

## 6. What to put in the report

For each provider: the export date, the number of grants, the three counts from step 3, the result of step 4 for connectors that reach production, and the counts from step 5. Add the hashes of the exported files to the Evidence hashes table of the audit report (see Report provenance recipes in `recipes.md`). A row that depends on a connector the owner did not export stays NOT ASSESSED: NEEDS DASHBOARD.
