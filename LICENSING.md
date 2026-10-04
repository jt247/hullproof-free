# Licensing

Hullproof free edition uses two licenses, split by what a file is. This page tells you which one covers which path.

Copyright 2026 Rare Phronesis Limited.

## Code: Apache License 2.0

Full text: [LICENSE](LICENSE). The code is everything that runs or configures a tool.

| Path | What it is |
|------|------------|
| `kit/.claude/hooks/` | The read only shell hook |
| `kit/tools/hullproof/` | Scanner rules, helper scripts, test fixtures, the gitleaks configuration and the tools README |
| `kit/.claude/agents/`, `kit/.claude/skills/`, `kit/.claude/rules/` | Agent, skill and scoped rule files that configure Claude Code |
| `kit/docs/hullproof/.kit-manifest` | The file list the auditor uses to check the kit |

## Documentation: CC BY-SA 4.0

Statement: [LICENSE-DOCS.md](LICENSE-DOCS.md). Full legal code: [LICENSE-DOCS-CC-BY-SA-4.0.txt](LICENSE-DOCS-CC-BY-SA-4.0.txt). The documentation is everything written to be read.

| Path | What it is |
|------|------------|
| `kit/docs/` | The standard, the domain documents, the release checklist, REFERENCES.md and the templates |
| `conventions/` | ID format, requirement template, severity rules and source rules |
| `README.md`, `CHANGELOG.md` | Repository text |
| `LICENSING.md`, `SECURITY.md` | These policy pages |

## Not covered by either license

1. `NOTICE.md` is a list of credits and notices for other people's work. It is not licensed content.
2. Third party material keeps its own license. Hullproof cites standards and vendor pages by ID and link, and paraphrases facts. Sources and their licenses where known are in `NOTICE.md` and `kit/docs/hullproof/REFERENCES.md`. Nothing here grants you rights to third party material.
3. Names and trademarks of other organisations belong to their owners.

## Hullproof Pro

The paid edition is a separate package under its own commercial license (LICENSE-PRO.md, inside that package). It is not included in this repository or in the free edition download, and these two licenses do not cover its Pro only files. Files that appear in both editions stay available to everyone under the licenses above.

## What this means in practice

If you copy the kit into your project, keep `LICENSE`, `LICENSE-DOCS.md` and `NOTICE.md` in your repository along with the license notices that come with the files. If you share or adapt the documentation, credit Hullproof and release your adapted text under CC BY-SA 4.0 as the license requires. If this page and the license texts differ, the license texts apply.
