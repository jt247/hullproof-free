# Severity Levels

Severity describes the impact if a requirement is not met. The same scale is used for audit findings.

| Level | Meaning | Release impact | Exception allowed |
|-------|---------|----------------|-------------------|
| BLOCKER | Direct path to compromise of data, accounts, or systems with little effort. For example: exposed secrets, missing authorization on sensitive data, auth bypass. | Release is not permitted. | No |
| CRITICAL | Serious compromise is likely, or a core control is missing. | Release is not permitted while open. | Yes, in writing, with a named owner, a compensating control and an expiry date |
| HIGH | Significant weakness that needs another condition to be exploited. | Fix before release, or record the acceptance with an owner and a fix date. | Yes, with an owner and a fix date |
| MEDIUM | Defense in depth gap with limited direct impact. | Fix in the next planned cycle. | Yes |
| LOW | Hardening and best practice. | Backlog. | Yes |

## Rating rules

The ordered rating procedure lives in the Severity section of `docs/hullproof/STANDARD.md` and is the only copy that counts. In short: start at the highest severity among the matching requirements, lower it only with code evidence written in the finding, never lower it because an identifier is hard to guess, and list every finding rated below a BLOCKER requirement in the lowered BLOCKER table that the release gate reviews. A BLOCKER cannot be accepted as an exception, but a finding under a BLOCKER requirement can be rated lower with evidence.

## Severity and stage

Severity says how bad a gap is. Stage says when a requirement starts to apply (see `requirement-template.md`). An audit only fails a project on requirements at or below its current stage. BLOCKER requirements apply from LAUNCH, with no exceptions.
