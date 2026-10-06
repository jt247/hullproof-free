---
trigger: glob
globs: **/Dockerfile*, **/*.tf, **/vercel.json, **/render.yaml, **/fly.toml, **/.github/workflows/**, **/docker-compose*.*, **/.env*
---
# Hullproof: infrastructure and CI

Advisory text for Windsurf and Devin, not enforced. Read INFRASTRUCTURE-SECURITY.md and DEPENDENCIES.md in docs/hullproof/ before editing these files. Start at the Coverage map and read only the requirement you need. The stage comes from docs/security/STAGE.md. Every BLOCKER applies from LAUNCH.

## Before you write code in this area

1. LAUNCH. Keep real secrets out of the repository, use .env.example with placeholders, and take CI credentials only from the CI secret store (SEC-SECRETS-004, SEC-SUPPLY-016). Give a pipeline or agent workspace no account wide or organisation wide credential (SEC-SUPPLY-035).
2. LAUNCH. Pin every third party action by its full 40 character commit SHA, with the version in a trailing comment, and never replace a SHA with a tag.
3. LAUNCH. Never run code from an untrusted pull request with secrets, and never put event data such as a pull request title or a branch name into a run script or a github-script body (SEC-SUPPLY-032).
4. LAUNCH. Commit the lockfile and install from it in CI. Keep a dependency vulnerability gate in CI (SEC-SUPPLY-002). Do not deploy source control files (SEC-SUPPLY-026).
5. LAUNCH. Keep no secrets in container images (SEC-CLOUD-016), keep production and non production credentials apart, and protect the production branch.
6. GROWTH adds. Give each workflow and job only the token permissions it needs, keep package install scripts off unless a package is approved, and keep workflow files under review like code.
7. Do not open ports, widen CORS, or make storage public without recording the reason.

## Refuse

- Committing a real secret, even in a workflow file.
- Referring to an action by a tag or a branch name.
- Giving a pipeline job write access it does not need.
- Running a reset style rollback against a real database from CI.

If a control blocks you, stop and report it with the ASSUMPTION, VERIFIED or SUSPECTED labels and a severity from docs/hullproof/STANDARD.md.
