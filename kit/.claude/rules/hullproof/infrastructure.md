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

Read `docs/hullproof/INFRASTRUCTURE-SECURITY.md` and `docs/hullproof/DEPENDENCIES.md` before editing these files.

1. Never commit real secrets. Use `.env.example` with placeholders and platform environment variables for real values.
2. Grant CI jobs and deploy tokens the minimum scope. Pin third party actions to a version.
3. Do not open ports, widen CORS, or make storage public without recording the reason.
4. Keep production and non production credentials separate.
