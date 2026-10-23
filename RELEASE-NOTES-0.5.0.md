# Hullproof 0.5.0 release notes

Release date: 2026-10-15. This release follows 0.4.0 (2026-10-11); the changelog lists what changed.

This is the free edition, which is public. It is a minor release because it adds audit capabilities. The requirements are the same as in 0.4.0: 110, every BLOCKER and every CRITICAL one.

## What is in the release

| Item | Content |
|------|---------|
| Requirements | Unchanged: 110 (every BLOCKER and every CRITICAL) |
| Engine | Hullproof Engine 0.5.1, in the `engine/` folder of this repository and of the zip, and in its own public repository |
| CI | `hullproof ci`: one command that writes `findings.json`, `report.md`, `results.sarif` and `pr-comment.md`, and exits 1 when a finding at or above the level set by `--fail-on` (default: blocker) is present. Templates for GitHub Actions, GitLab CI, CircleCI, Bitbucket Pipelines and Azure Pipelines. A GitHub Action |
| Pre commit hook | `hullproof hooks install` for plain git, Husky and the pre-commit framework. A staged secret is blocked in under a second |
| MCP server | `hullproof mcp`: seven read tools and one run tool behind `--allow-run`, over stdio |
| Proof sandbox | `hullproof prove`: runs a test against a copy of your app inside a container that has no network while the tests run, and records a flaw as proven only when it shows in 3 of 3 runs |
| Stack packs | Thirteen packs with a level from L0 to L4 each. `hullproof pack validate` refuses a level the recorded measurements do not support |
| Code map | Entry points and what protects them for Node and TypeScript, Python, Go, Ruby on Rails, PHP and Laravel, Expo, Java and Spring and .NET, with checks that read the map. For Kotlin and Android, Swift and iOS, and Rust it reads manifests and configuration (Kotlin and Swift source and Rust handler bodies are not read) |

## CI and the gate

`hullproof ci` runs the scan, the report and the gate in one step and writes four files that are the same bytes on every run of one commit. Findings at or above the level you set with `--fail-on` fail the job; the default level is blocker. The GitHub Action, `jt247/hullproof-action`, wraps it and posts one pull request comment. The templates in `ci-templates/` for the other four systems call the same command.

## The proof sandbox

`hullproof prove` starts your app in a container that has no network while the tests run (the build step can reach the package registry), runs a short test written as data, and checks that a control request works before the attack steps run. On the fixture app, 4 planted authorization flaws were proven in 3 of 3 runs and none were proven on the fixed copy, and 6 of 6 escape probes were contained. A flaw that cannot be proven is reported as not proven, never as passed. The proof is of a flaw in a copy of your app, so test the fixed request by hand as well. Only Node on Express and Flask have a start recipe today. 

## Stack packs and levels

Each pack states what the engine does for a stack, from L0 (secrets, dependencies, infrastructure and the generic rules, on any stack) to L4 (a start recipe so the sandbox can prove a flaw). The README and the report print the table. A level is computed from recorded measurements: L2 needs the code map to match an answer key exactly, and a real application sample at 90 percent or better where one was measured. L3 needs a blind key, at least half of the planted flaws and no finding on the fixed copy. A level describes how deep the engine goes for a stack, not how many flaws an app has. Ten real open source applications were sampled for the packs that have one, and the route sample was found 188 of 188.

## Secret findings that are example values

A secret hit that is a placeholder, a published example key, or a shapeless match in documentation, fixture data, an example env file, a lockfile, vendored or generated code or a migration is reported as an example value and does not hold the gate. A rule with a vendor shape (AWS, GitHub, Stripe, a private key block) still holds in those places, and every secret in source, config and test source files holds as before. On ten real applications this removed 61 of 85 secret records, and a hand check of all of them found no live secret among them.

## Findings schema 1.2.0

A machine evidence block now states its kind: `scanner_rule`, `engine_check`, `hunt_confirmed` or `sandbox_test`. A sandbox test run three or more times that showed the flaw every time lets `demonstrated` be true without owner evidence. A new incomplete reason, `engine_hunt`, describes a run whose hunt made model calls. Versions 1.0.0 and 1.1.0 stay valid.

## Tool front ends

The fifteen tool pages now describe an engine mode: how a tool that can run commands calls the engine and reads its results. The installer flag `--with-engine` writes the MCP settings for the tools that take them.

## What a result means

A lead is a place to look. It never fails a requirement and never holds the gate. A READY verdict is evidence that a defined set of checks was done on one commit, and Hullproof does not certify a project.

## Install

From the project root:

1. Clone the repository, or unzip the release zip in an empty folder, not inside your project. Copy the kit with the command in the README.
2. The engine is in `engine/`. It needs Node 22.18 or newer and has no runtime dependencies. Run `node engine/src/cli.ts ci .`.
3. Run `node tools/hullproof/install.mjs --tool <name>` for a dry run and again with `--write`.

## Good to know

1. Only Node on Express and Flask have a proof sandbox start recipe.
2. OSV Scanner sends package names to osv.dev and runs only with `--allow-network`.

## Support and terms

Support is through GitHub issues on this repository, https://github.com/jt247/hullproof-free/issues. Issues are public, so do not paste secrets or private project details. The terms are in LICENSING.md. Hullproof Pro is the paid edition with the other 552 requirements; see the README.
