# Hullproof tools

A small rule pack and helpers that back the static checks in the Hullproof requirements. They find leads for a reviewer. They do not replace the Verify steps, and a clean run proves only that these rules and these secret shapes were not found.

## Contents

| Path | What it does |
|------|--------------|
| `rules/*.yaml` | Semgrep rules, one file per topic. Every rule carries `sec_ids`, `severity_hint` and `confidence` in its metadata. |
| `gitleaks.toml` | The gitleaks config for every Hullproof scan. Extends the default rules, adds the default stack secret shapes, allows only the public Supabase keys. |
| `tests/*.ts`, `tests/*.tsx`, `tests/*.py` | Fixtures with `ruleid:` and `ok:` annotations for `semgrep --test`. |
| `tests/variants/` | Known bad code variants used to measure the catch rate (see Measured catch rates). |
| `tests/test_*.py` | Python tests for the rule metadata, the catch rates, the gitleaks config, the helpers and `policy_set.py`. |
| `tests/lockfiles/` | Small pnpm, npm and Yarn lockfiles for the lockfile recipe tests. |
| `helpers/policy_set.py` | Rebuilds the final live policy, function and grant set from ordered SQL migrations and flags risks. Python 3 standard library only. |
| `helpers/run_rules.sh` | Runs the rule pack against a repo from a private temporary folder and prints counts only. |
| `helpers/recipes.md` | One line grep commands, the secret scan commands, the lockfile reachability recipes, the kit integrity check and the report provenance recipes. |
| `helpers/enumerate.md` | Tested recipes that list route handlers (Next.js app and pages router, server actions, Express routers) and answer the gate questions from the data model and the code (tenants, payments, tools, URL fetching, MCP, uploads). |
| `helpers/ledger.py` | Coverage ledger: compares the in scope requirement IDs with the rows of a results table and prints the missing, duplicate and extra IDs. Python 3 standard library only. |
| `helpers/ssrf_guard_test.py` | SSRF guard test harness: blocked address ranges and 100+ test URLs with expected verdicts computed by Python `ipaddress`. No network calls. |
| `helpers/connector-evidence.md` | What to export per provider to see the grants of hosted coding agent connectors, and how to compare them with the inventory using counts. |
| `helpers/injection-corpus.md` | The named injection corpus for SEC-AI-050 (garak probes) and how to use the shipped delimiter breakout set for SEC-AI-016. |
| `tests/fixtures/` | Synthetic repositories and text files used by the helper tests, including `injection-delimiters.txt`. |

## Run

```bash
# Rule pack against a repo. Prints counts only. The optional second argument keeps file, line and rule ids (no source text).
tools/hullproof/helpers/run_rules.sh /path/to/repo

# Secret scan with the Hullproof config, never the repo's own
gitleaks dir . --redact --no-banner --config tools/hullproof/gitleaks.toml --ignore-gitleaks-allow
gitleaks git . --redact --no-banner --config tools/hullproof/gitleaks.toml --ignore-gitleaks-allow

# Policy set from migrations (default stack: supabase/migrations)
python3 tools/hullproof/helpers/policy_set.py supabase/migrations

# Coverage ledger: every in scope ID must appear exactly once in the results table
python3 tools/hullproof/helpers/ledger.py docs/hullproof/PRE-LAUNCH-AUDIT.md --results docs/security/reports/PRE-LAUNCH-RESULTS-2026-01-31.md --stage LAUNCH

# SSRF guard cases (list them, export them for your own test runner, or run a guard program against them)
python3 tools/hullproof/helpers/ssrf_guard_test.py --list
python3 tools/hullproof/helpers/ssrf_guard_test.py --cmd 'node tools/guard-cli.mjs'

# Self tests for the kit
semgrep --test --config tools/hullproof/rules tools/hullproof/tests
python3 -m unittest discover -s tools/hullproof/tests -p 'test_*.py'
```

A person runs `run_rules.sh` and `policy_set.py`. The skills and agents never run them: the hook allows no `bash` or `python3`. The skills run only the two gitleaks commands from the Run section. `semgrep scan` and `osv-scanner scan` are run by the owner in their own terminal and saved to files, because the hook allows no scan form for them.

## The read only hook

`.claude/hooks/hullproof-readonly-bash.mjs` has three profiles. `reviewer` allows read only helpers and new report files. `auditor` adds redacted gitleaks scans and `curl` to the confirmed live target. `skill` is the auditor profile plus exactly these commands: `date +%Y-%m-%d`, `git check-ignore -q <path>`, `git ls-files --others --exclude-standard`, `command -v gitleaks` (or `semgrep`, or `osv-scanner`), `semgrep --version`, `node --version` and `gitleaks version`. The skills attach it themselves with a `hooks` block in their frontmatter (matcher `Bash|Read|Grep|Glob`; Write is not matched because the skills write their own report). If the skill's hook does not load, register it in the project `.claude/settings.json` for the main session, otherwise the skill reports HOOK: INACTIVE and runs without Bash. Check it with `node .claude/hooks/hullproof-readonly-bash.mjs --selftest`.

What it guards beyond secret file names: `CLAUDE.md`, `AGENTS.md`, `docs/security/notes*` and `.md` or `.txt` files in a folder named `notes` allow Grep count and files_with_matches modes and `grep -c`, `grep -l`, but not Read or content output. `.env.example`, `.env.sample` and `.env.template` (exact names) allow only `grep -o` or `grep -c` with the key name pattern `'^[A-Za-z_][A-Za-z0-9_]*=' <file>` and Grep in files_with_matches or count mode, never Read.

## Hook limits

What the hook cannot do:

1. It checks paths and command forms, never file content. A secret pasted into a source file, a README or any note outside the protected names can still be printed by Read or by a content search. The skill and agent rules tell the model to use `-o` with a name pattern or `-c`, but nothing enforces that.
2. A recursive search (`grep -r`, Grep content mode on a folder) over a folder that holds `CLAUDE.md` or a notes folder is not blocked, because blocking it would stop most source searches. Name exact folders.
3. It cannot filter output. `ls`, `find`, `git ls-files` and Glob print file names as they are, so a file name that is itself a secret reaches the model. The skills tell the model to report such a name as `<kind>-shaped name` plus its folder. That is a text rule only.
4. Reads outside the project are blocked, so agent settings at user level (`~/.claude/`) cannot be inspected by the skills or agents. The owner supplies them.
5. When the hook is inactive there is no guard on Read, Grep or Glob. The skill text then tells the model never to Read `.env*`, `.mcp.json`, `settings*.json`, key files or credential files.

`policy_set.py` assumes the Supabase platform grants on new public tables and functions (anon, authenticated, service_role). Pass `--no-platform-defaults` when your migrations revoke those first or you run plain Postgres. Output holds object names and counts only. No expressions, no row data. Names come from the SQL files and are printed as written, so a name that someone built to look like a secret would be printed too (LOW).

## The scan runs with this config, not the repo's

Gitleaks reads `.gitleaks.toml` from the scanned folder when no `--config` is given, honors `gitleaks:allow` comments, and a repository can use both to hide its own findings. Semgrep honors the repository's `.semgrepignore`, skips folders named `test` or `tests` by default, and honors `nosemgrep` comments. So:

1. Gitleaks evidence scans name `tools/hullproof/gitleaks.toml` with `--config` and add `--ignore-gitleaks-allow`. A scan that does not name this file is not Hullproof evidence.
2. `helpers/run_rules.sh` scans a clean copy of the tracked and not ignored files, with an ignore file that names only `node_modules`, and turns `nosemgrep` comments off. It prints how many files had such comments. If the kit sits inside the scanned repository, the intentional findings in the kit's own `tools/hullproof/tests` fixtures are counted apart (`KIT FIXTURE FINDINGS`). Check that folder is untouched with `shasum -a 256 -c docs/hullproof/.kit-manifest`.
3. The config has no path allowlist for `.next`, `dist`, `build`, `.vercel` or `coverage`. The shipped bundle is where a secret ends up, and a config that skipped those folders would find nothing in the build output by construction. A scan that ends with `scanned ~0 bytes` scanned nothing and the requirement is NOT ASSESSED.
4. Repository scanner files (`.gitleaks.toml`, `.gitleaksignore`, `.semgrepignore`, `osv-scanner.toml`) are items for a reviewer to read, because they change what a scan can see.

## Rule pack

Severity hint is the severity a finding of this kind usually deserves before context. Confidence is how often a hit is a real problem. Every hit is a lead: read the code and decide. SEC IDs are real requirement IDs, checked by `tests/test_rule_pack.py` against the kit documents.

| Rule id | SEC IDs | Severity hint | Confidence | What it flags |
|---------|---------|---------------|------------|---------------|
| `hullproof-webhook-parse-before-verify` | SEC-API-101 | HIGH | MEDIUM | JSON body parsed before the signature is verified. |
| `hullproof-webhook-empty-secret-fallback` | SEC-API-101 | CRITICAL | MEDIUM | A signing secret that falls back to an empty string or the text "undefined". An HMAC with an empty key is valid, so anyone can sign. |
| `hullproof-secret-compare-env` | SEC-API-101, SEC-API-102 | HIGH | MEDIUM | A request value compared to an environment secret with a plain comparison, including the "Bearer undefined" case. |
| `hullproof-server-action-no-auth` | SEC-AUTHZ-002, SEC-API-001 | HIGH | MEDIUM | Server action with no auth call. |
| `hullproof-module-scope-auth-client` | SEC-AUTH-026 | HIGH | HIGH | Cookie bound auth client created at module scope. |
| `hullproof-server-html-interpolation` | SEC-API-147, SEC-WEB-001, SEC-WEB-031 | HIGH | LOW | Template literal with HTML and an interpolated value that is not wrapped by a listed escape function. Name based exemptions were removed: a helper that only trims is not an escape function. |
| `hullproof-html-concat` | SEC-API-147, SEC-WEB-001 | HIGH | MEDIUM | HTML string joined to a value by `+`. |
| `hullproof-html-response-body` | SEC-API-147, SEC-WEB-001 | HIGH | LOW | A response sent as HTML (`text/html`, `res.type("html")`, `c.html`) with a body that is not a constant. |
| `hullproof-dangerous-inner-html` | SEC-WEB-031, SEC-WEB-001 | HIGH | MEDIUM | `dangerouslySetInnerHTML`, `srcDoc`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` and `writeln`, `createContextualFragment`, `setHTMLUnsafe` with a non literal value. |
| `hullproof-handlebars-unescaped`, `hullproof-jinja-unescaped`, `hullproof-ejs-pug-unescaped` | SEC-API-147, SEC-WEB-031 | HIGH | MEDIUM | Triple stash, `\| safe`, `autoescape off`, `<%-`, `!=` in template files. |
| `hullproof-template-engine-escape-off`, `hullproof-python-safe-markup` | SEC-API-147, SEC-WEB-031, SEC-API-021 | HIGH | LOW | `SafeString`, `noEscape`, `autoescape: false`, `Markup`, `mark_safe`, `render_template_string` with non literal values. |
| `hullproof-raw-sql-concat` | SEC-API-017 | CRITICAL | HIGH | Query call whose string is built by template, `+`, `.concat` or `.join`. Covers `query`, `execute`, `raw`, `unsafe`, the `*Raw` family and the Prisma unsafe calls. |
| `hullproof-sql-raw-non-literal` | SEC-API-017 | HIGH | MEDIUM | `sql.raw(x)`, `Prisma.raw(x)`, knex and sequelize raw helpers with a non constant argument. |
| `hullproof-sql-tagged-template-misuse` | SEC-API-017 | CRITICAL | MEDIUM | A tagged template function called as an ordinary function with an interpolated string, or a raw helper inside a tagged template. |
| `hullproof-sql-built-string-reaches-query` | SEC-API-017 | CRITICAL | MEDIUM | A string that starts like SQL and holds a concatenated or interpolated value reaches a query call, directly or through a variable. Covers the generic method names (`get`, `all`, `run`, `exec`, `prepare`, `any`, `one`) only when the string starts with a SQL keyword. |
| `hullproof-sql-string-built-in-variable` | SEC-API-017 | HIGH | LOW | Keyword regex over template literals. Noisy, kept as a backstop. |
| `hullproof-postgrest-filter-string` | SEC-API-018, SEC-API-017 | HIGH | MEDIUM | Non constant column, filter string, sort key or select list passed to a PostgREST builder (`or`, `and`, `filter`, `not`, `order`, `eq`, `in`, `textSearch`, `select`). |
| `hullproof-postgrest-interpolated-filter` | SEC-API-018, SEC-API-017 | CRITICAL | HIGH | A value interpolated into an `or`, `and`, `filter`, `not` or `select` string on a Supabase or PostgREST builder. |
| `hullproof-subprocess-shell-string` | SEC-API-020 | CRITICAL | MEDIUM | `exec`, `execSync`, `execa` command strings, and `shell: true`, with a command that is not a plain string. |
| `hullproof-subprocess-shell-interpreter` | SEC-API-020 | CRITICAL | HIGH | `sh -c`, `bash -c`, `cmd /c`, `powershell -Command` started with a non constant script. |
| `hullproof-subprocess-arg-no-separator` | SEC-API-020 | HIGH | LOW | `execFile` or `spawn` with a non constant argument and no `--` in the list (option injection, for example `git ls-remote` with an upload pack option). |
| `hullproof-subprocess-request-data` | SEC-API-020 | CRITICAL | HIGH | Request data (taint, same file) reaches a subprocess call. |
| `hullproof-eval-or-new-function` | SEC-API-021, SEC-WEB-031 | HIGH | HIGH | `eval`, indirect and global `eval`, `Function`, `Reflect` forms, `vm` run and compile calls, string timers. |
| `hullproof-eval-through-alias` | SEC-API-021 | HIGH | MEDIUM | `eval` or `Function` copied to another name in the same block and then called, and `.constructor.constructor`. |
| `hullproof-expression-library-eval` | SEC-API-021 | HIGH | MEDIUM | `mathjs` evaluate, lodash template, ejs, pug, Handlebars, nunjucks, jsonata, vm2 with a non constant source. SEC-API-022 was folded into SEC-API-021. |
| `hullproof-dynamic-module-path` | SEC-API-021 | MEDIUM | LOW | `require` or `import()` of a computed path. Relative template paths with a fixed folder prefix are skipped. |
| `hullproof-ssrf-request-data-to-url` | SEC-API-035, SEC-API-034 | CRITICAL | MEDIUM | Request data (taint, same file) reaches `fetch`, axios, got, ky, undici, `http.request`, `page.goto` or the first argument of `new URL(x, base)` with no guard call. Guard names are matched by a regex you can edit. |
| `hullproof-ssrf-stored-url` | SEC-API-035, SEC-API-034 | HIGH | LOW | Outbound call to `record.url`, `endpoint.url`, `callbackUrl` and similar: a stored address that a user supplied earlier. |
| `hullproof-ssrf-url-built-from-base` | SEC-API-034, SEC-API-035 | MEDIUM | LOW | A base URL joined to a value with `+`. |
| `hullproof-tool-handler-admin-client-no-scope` | SEC-AI-020, SEC-AI-021, SEC-AGENT-008, SEC-SECRETS-003 | CRITICAL | LOW | An MCP or model tool handler that takes at most one parameter and uses an admin or service role client. Flag for review. |
| `hullproof-user-metadata-authz` | SEC-DB-006, SEC-AUTHZ-005 | CRITICAL | MEDIUM | Authorization decision based on user editable metadata. |
| `hullproof-math-random-token` | SEC-DATA-001, SEC-AUTH-001 | HIGH | MEDIUM | `Math.random` used for a token or secret. |
| `hullproof-cors-reflect-origin`, `hullproof-cors-origin-true` | SEC-WEB-022 | HIGH | MEDIUM, HIGH | Reflected or open CORS origin. |
| `hullproof-token-in-browser-storage`, `hullproof-token-value-in-browser-storage` | SEC-AUTH-022, SEC-WEB-013, SEC-MOBILE-002 | HIGH | MEDIUM | Token written to browser storage. |
| `hullproof-open-redirect` | SEC-AUTH-039, SEC-AUTH-030 | MEDIUM | MEDIUM | Redirect target taken from the request. |

Rules that need a name list read it from the rule itself, so a project edits one regex: the escape function names in `server-html-interpolation.yaml` and `html-variants.yaml`, the guard call names in the sanitizer of `ssrf-unguarded-url.yaml`, the admin client names in `tool-endpoint-admin-client.yaml`, and the auth helper names in `server-action-no-auth.yaml`.

## Measured catch rates

Two sets of known bad code, run with `python3 tools/hullproof/tests/test_variant_catch.py` from the project root. A variant counts as caught when any rule reports a finding inside its block. These numbers come from internal testing on synthetic code. Nothing here is a vendor benchmark.

**Set 1, 33 core variants** (`tests/variants/core-variants.ts`). 26 of them are SQL, eval and server HTML variants. The rules were written after seeing these variants, so this set is a regression floor, not a prediction.

| Family | Variants | Caught |
|--------|----------|--------|
| SQL (template, concat, `.concat`, array join, `sql.raw`, `whereRaw`, `prepare`, `exec`) | 8 | 8 |
| Eval (indirect eval, `globalThis.eval`, `vm.Script`, `vm.compileFunction`, `mathjs`, lodash template, `import(x)`, string timer) | 9 | 9 |
| Server HTML (concat, trim only wrapper, interpolation before the tag, SVG, join) | 9 | 8 |
| PostgREST filter strings | 2 | 2 |
| Subprocess (`git` option, `sh -c`, `exec(cmd)`) | 3 | 3 |
| Outbound URL built on a fixed base | 2 | 1 |
| **All** | **33** | **31** |
| **The 26 SQL, eval and HTML variants** | **26** | **25** |

Known misses in this set, marked `expect-miss` so the test fails if they start to be caught: markup held in variables and joined in one template (`${open}${name}${close}`), and a template literal that puts an unencoded id on a fixed base URL path (263 such lines in one real codebase, most with ids that come from the database, so a rule would bury the real ones).

**Set 2, 61 held out variants** (`tests/variants/heldout-variants.ts`). Written in shapes that differ from set 1 and run once against the rules before any tuning. They cover more sinks (Sequelize, Prisma unsafe, knex raw, `ffmpeg`, `tar`, `got`, request taint into `fetch`, empty webhook secrets, MCP tools). The author of the variants is also the author of the rules, so the real world rate is lower than these numbers. 10 of the 61 were written as known gaps and are marked `expect-miss`.

| Family | Variants | First run | Final |
|--------|----------|-----------|-------|
| SQL | 9 | 8 | 8 |
| Eval and dynamic code | 10 | 7 | 8 |
| Server HTML and DOM | 11 | 10 | 10 |
| PostgREST | 7 | 6 | 6 |
| Subprocess | 9 | 8 | 8 |
| Outbound URL | 8 | 6 | 6 |
| Webhook secret | 4 | 3 | 3 |
| Tool endpoints | 3 | 2 | 2 |
| **All** | **61** | **50** | **51** |

One variant that was not marked as a known gap was missed on the first run (`Function.prototype.constructor(...)`). The rule was extended and it is caught in the Final column. The 10 known gaps stay missed on purpose: a SQL string built by a formatting library, a dynamic `import` of a `../` template path, a timer given a function variable, markup built with `.concat` inside `.map`, a match filter parsed from JSON, `execFile('git', args)` with an argument array held in a variable, a function parameter named `target` passed to `fetch`, `http.get` of such a parameter, a webhook handler that returns early when the secret is missing, and a two parameter tool handler that uses the admin client.

**Noise on real code.** The pack was run on two real codebases (about 360 and 420 TypeScript files, written by one team, counts only). The rules hit a handful of sites, all worth a reviewer's time: an interpolated PostgREST `or` string (two sites, staff only pages), a stored customer webhook URL used by a plain `fetch`, and server built HTML from uploaded spreadsheet content (two hits). Four classes of false positive showed up during tuning and were removed before the numbers above: zod `.or(z.literal(...))`, `express.raw(...)`, a product MCP server whose tool handlers sit inside a factory that receives the signed in user, and taint that flowed through the response of an outbound call. Because those two codebases were also used for tuning, treat the zero false positive result as a best case.

## Gitleaks config

`gitleaks.toml` extends the default rules (`useDefault = true`) and adds the secret shapes of the default stack that the default rules missed. The default rules were tested first against one synthetic value per shape (`tests/test_gitleaks_config.py`), and a custom rule exists only where a planted value was missed or the shape needs a different test. Shape basis: docs means the vendor documentation states the shape, lenient means the prefix is known and the length is a loose range, context means the value has no shape and needs a nearby name.

| Secret | Rule | Basis |
|--------|------|-------|
| Supabase legacy service role key (JWT with the `service_role` claim) | `hullproof-supabase-service-role-jwt` | Payload encoding, checked at all three byte alignments. The default `jwt` rule cannot tell this from an anon key. |
| Supabase `sb_secret_` key | `hullproof-supabase-secret-key` | docs (`sb_secret_<random>_<checksum>`) |
| Supabase anon JWT, `sb_publishable_` key | Allowed, not secrets | Only a JWT whose payload role is `anon`, and exact `sb_publishable_` keys. Allowed by content, never by variable name. |
| Paddle API key, live and sandbox | `hullproof-paddle-api-key` | docs (vendor regex) |
| Paddle notification destination secret | `hullproof-paddle-webhook-secret` | docs (`pdl_ntfset_` prefix and example) |
| Paystack secret key | Default `stripe-access-token` finds the same shape | tested |
| Resend | `hullproof-resend-api-key` | lenient (prefix `re_` from docs) |
| Render | `hullproof-render-api-key` | lenient (prefix `rnd_`) |
| Vercel token | `hullproof-vercel-token` | context |
| Cloudflare R2 secret access key | `hullproof-r2-secret-access-key` | context (64 hex next to an r2, cloudflare or s3 secret name) |
| PostHog personal and project secret keys | `hullproof-posthog-secret-key` | docs (prefixes `phx_` and `phs_`). The `phc_` project token is public and is not matched. |
| Sentry organization auth token | `hullproof-sentry-org-auth-token` | prefix `sntrys_`, length lenient. The user token is found by a default rule. |
| Upstash REST token | `hullproof-upstash-token` | context. An Upstash Redis URL is found by the URL rule. |
| Anthropic, Google API keys | Default `anthropic-api-key`, `gcp-api-key` | tested |
| OpenAI project, service account, admin keys | `hullproof-openai-project-key` | lenient (the default rule needs a marker string that newer keys may lack) |
| Connection URL with a password (`postgres`, `mysql`, `mongodb`, `redis`, `amqp`, `mssql`) | `hullproof-url-with-password` | Placeholders such as `[YOUR-PASSWORD]`, `${VAR}` and `password` are skipped. |
| AWS access key id in an MCP or agent settings file | `hullproof-aws-key-in-agent-config` | Looser alphabet than the default, agent config paths only. |
| Literal key, token or password value in an MCP or agent settings file | `hullproof-agent-config-literal-secret` | Values that read from the environment (`${VAR}`) are skipped. |

Allowlists, in full: `node_modules` (third party code, check that it is not tracked), the Supabase anon JWT and `sb_publishable_` shapes above, the default generic rule on the kit's own markdown documents, and the URL rule on the kit's own hook script, which holds a synthetic URL in its self test table. Nothing else is allowed, and no build folder is.

Limits. A bare value with no prefix in a minified bundle (an R2 secret, an Upstash token, a Vercel token) can only be found by name, and the name is gone in a minified bundle. Run the planted value check in `helpers/recipes.md` on the folder you ship. Commit messages are not scanned by gitleaks, so the recipes search them by prefix and print hashes only. A secret split across lines or encoded is not found. The lenient shapes can miss a key with an unexpected length and can match a long identifier that looks like one.

## Honest limits of the rule pack

1. These rules are text and syntax patterns. A hit is a lead. A clean run proves only that these patterns were not found.
2. Taint rules (`subprocess-request-data`, `ssrf-request-data-to-url`, `sql-built-string-reaches-query`) follow values inside one file. They do not cross files, they match request objects by name (`req`, `request`, `ctx`, `event`), and they do not follow a function parameter that is not a request. A route handler that gets its values from a helper in another file is not seen.
3. The SSRF guard is recognized by function name. An inline `if` on the hostname is not recognized and shows as a finding. The rule says nothing about whether the guard is correct: DNS rebinding, redirects and address range gaps (100.64.0.0/10, mapped IPv6, 6to4, NAT64) need the Verify steps and a dynamic test.
4. The escape function list is by name. Someone can name a trimming helper `escapeHtml`. Keep the list to the project's one registered escape function and read it.
5. The tool handler rule flags only handlers with at most one parameter that use an admin client. A handler with two parameters is assumed to receive the caller and is not flagged. A caller check made in middleware before the handler runs shows as a finding, so confirm where the caller is authenticated. Registrations inside a function that takes a parameter (a per user factory) are skipped.
6. The webhook rules find the empty secret idiom and the plain secret comparison. They do not find a handler that skips verification when a secret is missing (that is a missed variant in set 2).
7. The server action rule matches auth helper names by regex (`auth`, `getUser`, `requireUser`, `session` and similar). Adjust it to the project helper. It covers files with a top level `"use server"` directive. Route Handlers are covered by the recipes.
8. The module scope rule matches cookie bound clients only (`createServerClient` and the auth helpers clients). A service role client at module scope is a different requirement (SEC-SECRETS-003).
9. The regex rules for HTML and SQL strings use template literal text. Expect noise and treat as leads. Nested template literals inside an interpolation confuse them.
10. The open redirect rule treats a relative path with a leading slash as still tainted. Confirm by reading the code.
11. Other languages are covered only where a rule says so (template files and a Python rule). The pack is written for TypeScript and JavaScript.
12. The catch rates above are measured on synthetic variants written by the author of the rules. They show what the rules can see, not how often real code that is vulnerable gets flagged.

## Additional rules

Rules and helpers beyond the core set of request data taint, SQL, eval and server HTML checks.

1. `hullproof-ssrf-stored-url` and `hullproof-ssrf-url-built-from-base`. The first finds the common customer webhook shape, where the address comes from a database row. The second covers fixed base concatenation.
2. `hullproof-dynamic-module-path`, `hullproof-eval-through-alias` and the Python and template file rules.
3. `hullproof-secret-compare-env`, which finds the plain comparison and the "Bearer undefined" case next to the empty secret rule.
4. `hullproof-aws-key-in-agent-config` and `hullproof-agent-config-literal-secret`, for the MCP and agent settings case.
5. `tests/variants`, `tests/test_variant_catch.py` and the held out set, so the catch rate is repeatable.
6. `hullproof-dangerous-inner-html` also flags `innerHTML`, `outerHTML`, `insertAdjacentHTML` and `document.write` with non literal values, since they are sibling sinks under SEC-WEB-031. `hullproof-eval-or-new-function` also flags `vm.run*` and string arguments to timers, as the Verify step for SEC-API-021 lists them. `policy_set.py` also flags policies that read `user_metadata` (SEC-DB-006) and reports an INFO line for security definer functions executable by `authenticated`.

## Policy helper flags

| Flag | Severity hint | SEC ID | Meaning |
|------|---------------|--------|---------|
| `RLS_NOT_ENABLED` | CRITICAL when client roles hold grants, otherwise HIGH | SEC-DB-001 | Table created in a migration with RLS never enabled. |
| `POLICY_NO_ROLE` | MEDIUM | SEC-DB-002 | Policy without a TO clause applies to PUBLIC, including anon. |
| `UPDATE_NO_WITH_CHECK` | LOW | SEC-DB-002 | Hygiene only. Postgres reuses USING when WITH CHECK is absent, so the row cannot move outside the USING test. |
| `CLIENT_WRITABLE_SENSITIVE_COLUMNS` | CRITICAL for role, plan, credit, admin, verified, stripe, paddle, tier, balance named columns, otherwise HIGH | SEC-DB-004, SEC-AUTHZ-004 | A permissive client INSERT or UPDATE policy exists on a table with sensitive named columns, and the client role holds a table level or column level write grant that covers them. |
| `DEFINER_NO_SEARCH_PATH` | HIGH | SEC-DB-009 | Security definer function without `set search_path`. |
| `DEFINER_EXEC_ANON_OR_PUBLIC` | HIGH | SEC-DB-008 | Security definer function that anon or PUBLIC can execute. |
| `DEFINER_EXEC_AUTHENTICATED` | INFO | SEC-DB-008 | Executable by authenticated. Confirm identity comes from the session, not a parameter. |
| `POLICY_USES_USER_METADATA` | CRITICAL | SEC-DB-006 | Policy text reads user editable claims. |

Limits. The parser is regex based and does not run DO blocks or dynamic SQL. It ignores role membership and ownership. Function identity uses a name plus argument type heuristic. Verify the result against the live catalog (`information_schema.column_privileges`, `pg_policies`) before you close a BLOCKER.

## Scanner family to SEC ID map

Use this to say which requirement a scanner result belongs to, and which requirement still has no scanner.

| Scanner family | What it reports | SEC IDs | Command or setting |
|----------------|-----------------|---------|--------------------|
| Semgrep rule pack | Code patterns in the rule pack table | See the rule pack table | `helpers/run_rules.sh` |
| Policy helper | Final RLS, function and grant state | SEC-DB-001, SEC-DB-002, SEC-DB-004, SEC-DB-006, SEC-DB-008, SEC-DB-009, SEC-AUTHZ-004 | `helpers/policy_set.py` |
| Trust policy (registry trust level must not drop) | A package whose publish trust level fell against earlier releases | SEC-SUPPLY-004 | pnpm `trustPolicy: no-downgrade` in `pnpm-workspace.yaml` |
| Minimum release age | Versions younger than the cooldown are not installed | SEC-SUPPLY-004, SEC-SUPPLY-001 | pnpm `minimumReleaseAge` (minutes) in `pnpm-workspace.yaml` |
| Exotic dependencies | Transitive packages fetched from git or tarball URLs | SEC-SUPPLY-004, SEC-SUPPLY-013 | pnpm `blockExoticSubdeps: true`, or `grep -cE 'tarball:|git\+|github:' pnpm-lock.yaml` |
| Missing integrity | Lockfile entries with no integrity hash, and CDN scripts with no `integrity` attribute | SEC-SUPPLY-001 for lockfiles, SEC-SUPPLY-011 for browser scripts | `grep -c 'resolution:' pnpm-lock.yaml` against `grep -c 'integrity:' pnpm-lock.yaml`, and `sgx -L 'integrity=' .` on HTML |
| Gitleaks, working tree and history | Committed secrets, found with the Hullproof config | SEC-SECRETS-004, SEC-SECRETS-005, SEC-SECRETS-006 | `gitleaks dir` and `gitleaks git` with `--redact --config tools/hullproof/gitleaks.toml --ignore-gitleaks-allow` (see recipes) |
| Gitleaks hit in local env or agent settings | A live secret within reach of a coding agent | SEC-AGENT-011, SEC-AGENT-012, SEC-AGENT-013 | Route here, not to SEC-SECRETS-004 |
| Gitleaks on build output | Secrets in the shipped bundle | SEC-SECRETS-001 | Same command on `.next/static` or the Expo export. The config has no path allowlist, so the folder is scanned. If the summary says `scanned ~0 bytes`, the scan did nothing: NOT ASSESSED |
| OSV Scanner | Known advisories in direct and transitive packages | SEC-SUPPLY-002 | `osv-scanner scan source -r` then classify with the lockfile recipes in `helpers/recipes.md` |
| OSV on abandoned or vendored code | Not detected by OSV | SEC-SUPPLY-006 | Manual vendored copy review |

Gaps. No requirement in `DEPENDENCIES.md` names release age, trust policy or exotic sources directly. They are mapped to the closest existing IDs above, and a dedicated ID would be cleaner.

## Writing note

All text here follows the Hullproof writing rules. Commands, flags and rule ids keep their hyphens because they are identifiers.

## SSRF guard harness

`helpers/ssrf_guard_test.py` tests an outbound request guard (SEC-API-034, SEC-API-035) without a network. It holds the blocked ranges (private use, loopback, link local including the cloud metadata address, shared address space 100.64.0.0/10, the unspecified address, documentation and benchmarking ranges, multicast and reserved space, unique local and link local IPv6, Teredo) and unwraps the IPv4 inside mapped, 6to4 and NAT64 addresses before it judges them. The 100+ cases include decimal, octal and hex IPv4 forms, short forms such as `127.1`, a trailing dot, the at sign trick (`http://allowed.example@127.0.0.1/`), fragment and backslash delimiters, bracketed IPv6 with a zone id, and names whose stub answer is private. The expected verdict of each case is computed from the table with the `ipaddress` module.

Your guard must accept an injected resolver, because the harness never resolves a name. With `--cmd` the program gets the URL on standard input and the stub answers in the environment variable `SSRF_RESOLVE`, and prints `allow` or `block`. With `--emit json` you can feed the same cases to a test in the guard's own language. A guard that only passes these cases is not proven safe: DNS rebinding, redirects and server side renderers need the checks in `python3 tools/hullproof/helpers/ssrf_guard_test.py --rebind-note`.

## Coverage ledger

`helpers/ledger.py` reads the checklist (`PRE-LAUNCH-AUDIT.md` or a file in `checklists/`) and a results table (a markdown table with an ID column and a Result column) and prints one count line, then the IDs that are missing, duplicated or not in scope. It exits 1 when any exist. `--stage` cuts the checklist to the declared stage, `--ids` takes an explicit in scope list, and `--section` limits it to the tables under one heading (the audit report uses `Coverage ledger`). The skills write the same count line in the results file; the hook allows no Python, so the owner runs the script as the independent check.
