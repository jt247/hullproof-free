# Security policy

## Scope

This policy covers the Hullproof kit, in the free edition and in Hullproof Pro: the read only shell hook, the scanner rules, the helper scripts, the skills, the agents and the scoped rules, and the standard text that tells agents what to do.

Examples of reports in scope: a way around the hook that lets a command outside the read only list run, a flaw in an agent or skill instruction that lets repository content steer the auditor, a script that writes or sends data it should not, or a requirement whose text lets an insecure design pass.

The projects that Hullproof scans are not in scope. A vulnerability in your own code is for you to fix.

## How to report

Send your report by email to joshua@joshuatheophilus.com with the subject "Hullproof security report". It covers the free edition and Hullproof Pro. Send only what is needed to reproduce the problem. Do not send secrets, customer data or the contents of Pro files beyond the lines that show the problem. For a Pro file, say that it is a Hullproof Pro file and give its path.

If the Security tab of https://github.com/jt247/hullproof-free shows a Report a vulnerability button, you may use it instead. It sends the report privately to the repository maintainers. If the button is not there, use email.

Please do not open a public issue or pull request for a vulnerability.

Please include:

1. The file or requirement ID that is affected.
2. The Hullproof version, from `CHANGELOG.md`, and the Claude Code version if the report involves the hook or an agent.
3. Steps to reproduce, with the exact command or input.
4. What you expected and what happened.
5. The impact as you see it.
6. Whether you want to be credited, and under what name.

## What happens next

1. We aim to acknowledge your report within 7 days. This is a target for the first reply, not a promise of a fix date.
2. We will tell you whether we can reproduce it and what we plan to do.
3. We credit reporters who want credit, in the changelog entry for the fix.
4. We do not offer a bounty.

## Supported versions

Only the latest release is supported. When a fix is made it goes into a new release, not into older ones, and the release is listed in `CHANGELOG.md`.

## Out of scope

1. Findings in third party tools such as Claude Code, Semgrep, gitleaks or `osv-scanner`. Report those to their maintainers.
2. Differences in how one model or model version follows the agent instructions. The hook is the enforced control, and the written rules are instructions.
3. Findings in the projects you scan with Hullproof.
