# Accepted Risk Record Template

Save each acceptance in the place named in `docs/security/STAGE.md`, one record per finding. Rules from `docs/hullproof/STANDARD.md` (the numbers below are Hullproof policy with no external source):

1. A BLOCKER cannot be accepted. Fix it. A finding lowered from a BLOCKER requirement cannot be accepted either.
2. A CRITICAL can be accepted only outside the protected classes (rule 7), and only in writing, with a named owner, a named approver, a compensating control and an expiry date. An expired record counts as an open finding. An unsettled CRITICAL requirement (not verified) can be accepted the same way, and the record says what would settle it.
3. Limits on a CRITICAL acceptance: at most 90 days from the day it takes effect; one renewal only (a new record with a new written review and evidence that the control was tested after the previous expiry; any later record for the same requirement and finding is a renewal); no more than 3 open CRITICAL acceptances for one release.
4. The approver is a person other than the author of the code and other than the owner of the risk, whenever a second person exists.
5. Solo builder, no second person: the acceptance takes effect no earlier than 24 hours after it is written, and an AI assisted review from a fresh agent session that has not seen your notes is attached.
6. A HIGH can be accepted with an owner and a fix date. The acceptance lasts at most 180 days from the day it takes effect (Hullproof policy), a later record for the same finding does not restart the 180 days, and an expired one counts as an open finding.
7. Protected classes: no record is written for a CRITICAL or BLOCKER finding, or an unsettled CRITICAL or BLOCKER requirement, in credentials and secrets exposure, authentication, tenant isolation or payments. Fix it. A record written anyway does not count, and the release is NOT READY. Example that may be accepted: CRITICAL, no backup restore test yet, a dated manual export as the control. Example that may not: CRITICAL, a live payment key in the repository.
8. Recording that a requirement does not apply is a different record (not applicable) and is not an acceptance.

Delete this note after you copy the template.

| Field | Value |
|-------|-------|
| Record id | AR-NNN |
| Finding id and audit report | F-NN, report file and commit SHA. For an unsettled requirement, the requirement and the report row instead. |
| Requirement | SEC-[DOMAIN]-[NUMBER] |
| Severity | CRITICAL or HIGH |
| Protected class check | Confirm the finding is not in credentials and secrets exposure, authentication, tenant isolation or payments. If it is, stop: no record. |
| What is not met | One or two sentences, or "not verified" for an unsettled CRITICAL, with the owner action that would settle it |
| Who could exploit it and what they gain | |
| Why it cannot be fixed now | |
| Compensating control | What is in place instead, with where to see it (file, setting, alert) |
| Control tested on | YYYY-MM-DD, and how it was tested. For a renewal this date is after the previous expiry. |
| Owner | Named person |
| Approver | Named person other than the code author and the owner. Write "none exists, solo builder" if you work alone. |
| Second person exists | Yes or no |
| Written at | YYYY-MM-DD HH:MM |
| Takes effect | YYYY-MM-DD HH:MM. At least 24 hours after "Written at" for a solo builder. |
| Expiry date (CRITICAL, at most 90 days after "Takes effect") or fix date (HIGH, at most 180 days after "Takes effect") | YYYY-MM-DD |
| Renewal | Original, or renewal 1 of 1 (link to the first record). No second renewal exists: fix it or do not release. |
| AI assisted review attached | Solo builder only: file name and date of the fresh session review |
| Open CRITICAL acceptances for this release | Count including this one. Must be 3 or fewer. |
| Review date | When the owner checks the control still works |
| Accepted by | Name and date |
| Status | Open, expired, closed (fix shipped, finding id) |
| Closed on | |
