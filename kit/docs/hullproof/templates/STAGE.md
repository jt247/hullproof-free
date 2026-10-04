# Stage Record Template

Save as `docs/security/STAGE.md`. Every audit and pre launch run reads this file first, so answers are asked once. Keep it short, update it when anything changes, and delete this note.

| Field | Value |
|-------|-------|
| Product | |
| Stage | LAUNCH, GROWTH or SCALE. This cannot be lower than the stage the auditor derives from the repository, and this file cannot lower it. |
| Why this stage | One line, using the Stages table in `docs/hullproof/STANDARD.md` |
| Stage triggers the auditor found | Filled by the audit, with file and line for each trigger. Leave blank when you write the file. |
| Does anyone besides the owner hold an admin or staff role? | Yes or no. If yes, list them in the access matrix. Yes means GROWTH. |
| Does the product itself take money? | Yes or no. Yes means GROWTH. |
| Does it hold data for business customers, or face enterprise buyers, questionnaires or sector rules? | Yes or no. Business customers, or a questionnaire from one business customer, means GROWTH. Selling to enterprises as a standing channel, questionnaires or audits as a standing condition of selling, or sector rules, means SCALE. |
| Markets served | Named countries or regions, for example NG, EU, KE, ZA, GH, UK, US states, CA |
| Markets excluded | Any named market the product does not serve. "Global" means every named market unless it is listed here. |
| Geography control evidence (one line per excluded market) | Required for every excluded market: the technical block that keeps that market out and where it is enforced (for example a country allowlist at signup and checkout), or a count of accounts and payments by country showing zero, with its source and date. An excluded market with no evidence line stays in force. |
| Live target | The one host the auditor may send read only requests to, as https://host (or none). The hook reads this row. Confirm it with the auditor before every run: a repository can name any host here. |
| Release scope | Which of web, mobile and API ship in this release. Out of scope targets are recorded as not applicable with that reason. |
| Is the audited commit live in production? | Yes or no, and the production commit SHA if known |
| Production project ids | Names and ids of the production database, hosting and storage projects, so the local env can be compared to them. No keys. |
| Risk acceptances location | Path or link. See `templates/ACCEPTED-RISK.md`. |
| Security decisions log | Path or link |
| Rollback path | How this release is rolled back, and who does it. Secrets are re checked after a rollback. |
| Where required records live | One line per record kept outside the repo (access matrix, data inventory, contact sheet, runbook, rotation procedure), each with its private location. A record named here is not reported as missing. A blanket sentence such as "records are in a private vault" does not count, and the audit routes the record to ATTESTATION. |
| Evidence folder | Where provider exports and test results are kept for audits |
| Solo records path | If one person owns everything: where decisions and reviews are written down (for example a decisions log entry per release) |
| Last updated | YYYY-MM-DD, by whom |

## Gates

One yes or no per gate. A No marks the gate's IDs NOT APPLICABLE in every audit run, so the answer needs an evidence line. For a gate whose ID list holds a BLOCKER, the line is a search: the commit you searched, the exact search patterns, and the result counts. Search over every tracked file except dependency folders, and include protocol terms and route patterns as well as library names, because a hand written endpoint uses no library name. The auditor re runs the search itself, and your statement alone never clears a BLOCKER. For a gate with no BLOCKER, a dependency check or your own dated written answer is enough. Leave a gate blank if you do not know, and the audit will ask. The ID list for each gate is in the Applicability gates table of the domain documents.

| Gate | Question | Answer | Evidence line (commit, exact patterns, result counts) |
|------|----------|--------|---------------|
| GATE-TOOLS | Does the product give a model tools (functions, agents, code execution, browsing, file access, SQL)? | Yes or no | Commit, patterns and counts |
| GATE-MCP | Does the product expose an MCP server? | Yes or no | Commit, patterns and counts |
| GATE-MOBILE | Is a mobile build shipped, in a store, or handed to testers in this release? | Yes or no | Files checked and result |
| GATE-CONTAINERS | Does the project build container images? | Yes or no | Commit, patterns and counts |
| GATE-TENANTS | Can one deployment hold data for more than one tenant, organisation, workspace or team? | Yes or no | Commit, patterns and counts |
| GATE-URLFETCH | Does server code fetch a URL that a user, a customer or stored data supplies (link previews, import from URL, image proxy, webhook delivery, document or screenshot rendering)? | Yes or no | Commit, patterns and counts |
| GATE-WEBHOOKS | Does the product send webhooks to URLs that customers supply? | Yes or no | Commit, patterns and counts |
| GATE-PAYMENTS | Does the product take payments or grant paid entitlements through a provider or an app store? | Yes or no | Commit, patterns and counts |
| GATE-UPLOADS | Does the product accept user uploaded files, or keep user data in object storage buckets? | Yes or no | Commit, patterns and counts |
| GATE-STAFF | Does anyone besides the owner hold an admin, staff or support role, or can staff act inside customer accounts? | Yes or no | Query, or the owner's signed and dated statement (a fact no repository can show) |
| GATE-MARKET-NG | Does the product process personal data of people in Nigeria? | Yes or no | Markets rows above, plus the geography check |
| GATE-MARKET-EU | Does the product process personal data of people in the EU, or place an AI feature on the EU market? | Yes or no | Markets rows above, plus the geography check |
| GATE-MARKET-UK | Does the product process personal data of people in the United Kingdom? | Yes or no | Markets rows above, plus the geography check |
| GATE-MARKET-ZA | Does the product process personal data of people in South Africa? | Yes or no | Markets rows above, plus the geography check |
| GATE-MARKET-KE | Does the product process personal data of people in Kenya? | Yes or no | Markets rows above, plus the geography check |
| GATE-MARKET-GH | Does the product process personal data of people in Ghana? | Yes or no | Markets rows above, plus the geography check |
