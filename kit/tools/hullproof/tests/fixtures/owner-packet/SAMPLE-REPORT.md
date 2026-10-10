# Security Audit: Sample

Fixture for the owner packet tests. The ids are real requirement ids, the text is invented.

## UNVERIFIED CONTROLS

| Requirement | Severity | State | Why it could not be settled | Owner action |
|-------------|----------|-------|-----------------------------|--------------|
| SEC-DB-016 | HIGH | NOT ASSESSED: NEEDS DASHBOARD | Backup plan lives in the provider | Export the backup plan |
| SEC-DB-001 | BLOCKER | NOT ASSESSED: NEEDS DASHBOARD | Policies are not in the migrations | Export the policy list |
| SEC-SUPPLY-016 | CRITICAL | NEEDS DASHBOARD | Pipeline secrets list is in the host | Export the Actions secret names |
| SEC-API-057 | HIGH | NEEDS DASHBOARD | Job platform verification is a setting | Export the environment variable names |
| SEC-API-001 | BLOCKER | NEEDS DYNAMIC TEST | No staging target was permitted | Run Part 1 of the staging window |
| SEC-AUTHZ-003 | BLOCKER | NEEDS DYNAMIC TEST | Two user test was not permitted | Run Part 2 of the staging window |
| SEC-DATA-901 | HIGH | NEEDS DYNAMIC TEST | Invented requirement with no prepared check | Test it by hand |
| SEC-SECRETS-001 | CRITICAL | NEEDS BUILD | No build from this commit | Build the commit and scan the output |
| SEC-AI-017 | HIGH | ASK OWNER | Delivery of the outbox is not in the repo | State whether mail is delivered |
| A Pro edition requirement | MEDIUM | ATTESTATION | Needs a signed statement | Sign the stage declaration |
| SEC-LOG-099 | LOW | UNKNOWN | Tool not installed | Install the tool and run it |

## RECOMMENDED NEXT ACTIONS

| Requirement | Severity | State | Why | Owner action |
|-------------|----------|-------|-----|--------------|
| SEC-NOPE-001 | HIGH | NEEDS DASHBOARD | A row outside the section is ignored | none |
