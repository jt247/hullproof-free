---
paths:
  - "**/Dockerfile*"
  - "**/*.tf"
  - "**/vercel.json"
  - "**/render.yaml"
  - "**/fly.toml"
  - "**/.github/workflows/**"
  - "**/docker-compose*.*"
  - "**/.env*"
---
# Infrastructure and CI rules

Before editing these files, open the Coverage map in `docs/hullproof/INFRASTRUCTURE-SECURITY.md` and `docs/hullproof/DEPENDENCIES.md`, find the rows for your change, then read only those requirement blocks (list them with `grep -n '^### SEC-' docs/hullproof/INFRASTRUCTURE-SECURITY.md`, then Read with an offset). Do not load a whole document.

1. Never commit real secrets. Use `.env.example` with placeholders and platform environment variables for real values. CI credentials come only from the CI secret store (SEC-SECRETS-004, SEC-SUPPLY-016).
2. Pin every third party action by its full 40 character commit SHA, with the version in a trailing comment. Never replace a SHA with a tag (a Pro edition requirement).
3. Give each workflow and job only the token permissions it needs, and never run code from an untrusted pull request with secrets (Pro edition requirements).
4. Never put event data such as a pull request title, branch name or issue text straight into a `run:` script or a `github-script` body. Pass it in through an environment variable (SEC-SUPPLY-032).
5. Install packages in CI from the committed lockfile with install scripts off unless a package is approved (Pro edition requirements).
6. Do not open ports, widen CORS, or make storage public without recording the reason.
7. Keep production and non production credentials separate (a Pro edition requirement).
