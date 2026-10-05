# Backend Security

| Field | Value |
|-------|-------|
| Domain codes | SEC-API |
| Topics covered | Injection, Backend Security, SSRF, File Uploads, Error Handling, Server File Access |
| Part of | Hullproof Security Standard, see STANDARD.md |

Server side code: interpreters and injection, internal routes and background jobs, outbound requests, file processing, error handling and server side file access. Requirement IDs keep the SEC-API code. API surface, validation, webhooks, rate limiting and payments are in API-SECURITY.md; authorization is in AUTH.md.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 11 of the 43 requirements in this domain: every BLOCKER and every CRITICAL requirement in it. Hullproof Pro holds the other 32. Pro covers the server side habits that stop injection, unsafe file handling, outbound request abuse and job and workflow mistakes.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-API-017](#sec-api-017-parameterize-every-database-query) | Parameterize every database query | BLOCKER | LAUNCH | API, Backend, Database |
| [SEC-API-018](#sec-api-018-map-query-structure-input-through-a-fixed-allowlist) | Map query structure input through a fixed allowlist | CRITICAL | LAUNCH | API, Backend, Database |
| [SEC-API-019](#sec-api-019-keep-dynamic-sql-out-of-client-callable-database-functions) | Keep dynamic SQL out of client callable database functions | CRITICAL | LAUNCH | Database (Supabase), API |
| [SEC-API-020](#sec-api-020-never-run-shell-commands-built-from-untrusted-data) | Never run shell commands built from untrusted data | BLOCKER | LAUNCH | API, Backend, Serverless, AI features |
| [SEC-API-021](#sec-api-021-never-evaluate-untrusted-data-or-model-output-as-code) | Never evaluate untrusted data or model output as code | BLOCKER | LAUNCH | API, Backend, Serverless, AI features |
| [SEC-API-027](#sec-api-027-authorize-at-the-point-of-data-access-never-only-in-proxy) | Authorize at the point of data access, never only in Proxy | CRITICAL | LAUNCH | Backend, API, SaaS, Web (Next.js) |
| [SEC-API-056](#sec-api-056-keep-queues-off-the-data-api-unless-each-exposed-queue-is-locked-down) | Keep queues off the Data API unless each exposed queue is locked down | CRITICAL | LAUNCH | Database (Supabase), Backend |
| [SEC-API-057](#sec-api-057-keep-job-platform-request-verification-on-in-deployed-environments) | Keep job platform request verification on in deployed environments | CRITICAL | LAUNCH | Backend, Serverless, API |
| [SEC-API-034](#sec-api-034-restrict-fixed-outbound-calls-to-an-allowlist-of-hosts) | Restrict fixed outbound calls to an allowlist of hosts | CRITICAL | LAUNCH | API, Backend, Serverless, AI features |
| [SEC-API-035](#sec-api-035-guard-user-and-model-supplied-urls-before-connecting) | Guard user and model supplied URLs before connecting | CRITICAL | LAUNCH | API, Backend, Serverless, AI features |
| [SEC-API-045](#sec-api-045-never-serve-uploads-as-active-content-from-the-app-origin) | Never serve uploads as active content from the app origin | CRITICAL | LAUNCH | API, Web, Cloud |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Injection (SQL, ORM raw queries, NoSQL, OS command, template, eval) | API-SECURITY.md, AI-SECURITY.md | None | SEC-API-017, SEC-API-018, SEC-API-019, SEC-API-020, SEC-API-021 (more in Pro edition) |
| SSRF and outbound request control | API-SECURITY.md, FRONTEND-SECURITY.md, DATA-PROTECTION.md | Outbound customer webhooks | SEC-API-034, SEC-API-035 (more in Pro edition) |
| File uploads and file processing (type, size, content, storage path, malware) | DATA-PROTECTION.md, DATABASE-SECURITY.md | None | SEC-API-045 (more in Pro edition) |
| Background jobs and queues (payload authorization, idempotent retries, poison messages, queue exposure, batch and run time limits) | API-SECURITY.md, AUTH.md, PRIVACY.md | None | SEC-API-056 (more in Pro edition) |
| Cron and internal routes (job platform verification, scheduled job credentials) | API-SECURITY.md, DATABASE-SECURITY.md, INFRASTRUCTURE-SECURITY.md | None | SEC-API-057 (more in Pro edition) |
| Server side caching of user data | AUTH.md, PRIVACY.md | None | None in this document |
| Authorization and workflow integrity at the data layer | None | None | SEC-API-027 (more in Pro edition) |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-WEBHOOKS | Does the product send webhooks to URLs that customers supply, or request any other URL that a user chooses (link previews, import from URL)? | Search the schema and source for webhook_url, callback_url or a webhook endpoints table, and for outbound delivery jobs. Also search for link previews, unfurling, import from URL and any other request to a URL a user chose. Record the commands, the number of files searched and that nothing was found, or record the owner's written answer. A No here does not clear SEC-API-035: it is also named by GATE-URLFETCH, and both gates must be No. See GATE-TOOLS for model supplied URLs. | SEC-API-035 |
| GATE-UPLOADS | Does the product accept user uploaded files from any source (browser, client SDK, mobile picker, base64 or data URL body, inbound email attachment, avatar or file import), or keep user data in object storage buckets? | Search the source and storage configuration for multipart or formData file handling, signed upload URLs, upload libraries, client SDK uploads, base64 and data URL bodies, mobile pickers, inbound email attachments and avatar import. Cover stores other than S3 compatible ones (managed storage products, database large objects, file fields in a CMS), a storage bucket, putObject or getSignedUrl, and list the buckets on the storage provider. Record the commands, the number of files searched and that nothing was found, or record the owner's written answer. | SEC-API-045 (more in Pro edition) |
| GATE-URLFETCH | Does any server code request a URL, host, path or file that a user, a stored record, an imported file or a model chose? | List every call site of the outbound HTTP libraries (fetch, axios, got, undici, node http and https, SDKs that take a URL, headless browsers, HTML to PDF and SVG converters) with its URL source. A URL, host or path that is not a code constant counts. Include link previews, import from URL, user configured webhooks, avatar fetch, model fetch tools and server side renderers. Record the commands, the number of files searched and the call site list, or record that every call site uses a code constant. A No on GATE-WEBHOOKS does not answer this gate. | SEC-API-035 (more in Pro edition) |
<!-- hullproof:gates:end -->

---

## Injection

### SEC-API-017: Parameterize every database query

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API, Backend, Database |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW, DYNAMIC TEST |

**Requirement.** Every database query, including NoSQL queries, RPC calls and ORM raw helpers, MUST pass user influenced values as bound parameters or through a query builder that binds them, and MUST NOT concatenate or interpolate them into query text. A filter, search or select string that a client library parses (PostgREST style `or`, `and`, `not`, `filter`, `textSearch`, `select`, `order` with a string, GraphQL variables spliced into query text) is query text: it MUST be built with the typed builder methods that take each value as a separate argument. Where the string form is unavoidable, every interpolated value MUST first match a pattern that excludes the grammar's separators, wildcards, parentheses, quotes, percent signs and whitespace control characters, and a column or relation list MUST come from an allowlist (SEC-API-018).

**Why.** String built queries let an attacker rewrite the query, read every table and change or delete data. It is the core injection failure and needs no special skill.

**Implementation.**
- Use the ORM or query builder's parameter binding for all values.
- Treat raw SQL helpers (for example `sql.raw` in drizzle, `$queryRawUnsafe` style functions, `execute` with a built string) as forbidden for user influenced data.
- Do not rely on manual escaping as the main defense.
- Default stack: drizzle `sql` tagged templates bind values; `sql.raw` does not. supabase-js filter methods bind values; building PostgREST filter strings from input does not.
- PostgREST filter grammar [SRC-364]: `or`, `and` and `not` take parenthesised, comma separated conditions such as `or=(age.lt.18,age.gt.21)`, and `not` prefixes any operator. A value that carries a comma, dot or parenthesis can therefore add or change a condition. The documentation says a value that has a reserved character must be wrapped in double quotes. It does not list the reserved characters on that page and does not say how a double quote or backslash inside a quoted value is escaped, so quoting a value by hand is not safe. Use the typed builder, or reject at least those characters.

**Verify.**
1. Run Semgrep rules for template literals or string concatenation passed to `sql.raw`, `execute`, `query`, `rpc` and similar sinks, and to the filter sinks `.or(`, `.and(`, `.not(`, `.filter(`, `.textSearch(`, `.select(` and `.order(` and to GraphQL query strings. A rule pack that has no pattern for a sink family is not evidence for it; search the source for the sink names as well.
2. Review every raw SQL call that remains.
3. In a non production environment, send injection payloads to every search, filter, select and identifier parameter, in the dialect of the sink that parameter reaches. For SQL sinks use `'`, `' OR 1=1--` and `1; SELECT pg_sleep(5)`. For a parsed filter string use values that add a condition, close a group, or name a column that exists but is not selected (for example a value containing a comma followed by a column, operator and value, and a value containing a closing parenthesis). No error leaks or behavior changes may follow, and the result count and shape must equal the baseline response.

**Evidence.** Semgrep report with zero unresolved findings, the list of reviewed raw SQL and filter string sites, and the dynamic test output.

**Exceptions.** None. Reach clarification: a filter or query string built from input that only an authenticated staff account can reach is still a finding of this requirement, but the finding is rated HIGH when the code evidence shows that reach limit. Input reachable by any visitor or customer keeps the BLOCKER rating. A role counts as staff only when it is assigned through a server path and appears in the named access list; a role a customer can obtain is not staff. Where signup is open, an authenticated reach limit is not a reach limit.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.2.4 [SRC-010]; OWASP SQL Injection Prevention Cheat Sheet, Defense Option 1 and Option 4 [SRC-038]; OWASP Top 10 2025 A05:2025 [SRC-020]; CISA Secure by Design, Parameterized queries [SRC-063]; PostgREST Tables and Views, Logical operators [SRC-364].

**AI Agent Instruction.** Never build query text from user input, request data or model output. Use bound parameters or the query builder. If a query seems to need string building, stop and use SEC-API-018, or report why it cannot be parameterized. SQL that a model writes and runs follows SEC-AI-062 in AI-SECURITY.md.

---

### SEC-API-018: Map query structure input through a fixed allowlist

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | API, Backend, Database |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, AUTOMATED TEST |

**Requirement.** Input that selects query structure (table, column, sort key, sort direction, operator) MUST be mapped through a fixed server side allowlist to known identifiers, and the raw input MUST NOT reach the query. A column or relation list inside a filter, search or select string that a client library parses (SEC-API-017) comes from the same allowlist. An object, array or nested value taken from the request and passed as a `where`, `filter`, `include`, `select`, `orderBy` or NoSQL query argument is query structure too: it MUST be rebuilt on the server from allowlisted fields and operators and MUST NOT reach the ORM or driver as received.

**Why.** Identifiers cannot be bound as parameters, so sort and filter options are a common injection path even in ORM code, and an allowlist does not depend on the ORM escaping identifiers correctly. A request body passed straight into an ORM filter lets the caller choose fields and operators the form never offered, for example a filter that walks a relation to a hidden column (`user: { passwordHash: { startsWith: 'a' } }`) and reveals it one character at a time, or a NoSQL operator object (`{ "$ne": null }`, `{ "$regex": "^a" }`) in place of a plain value.

**Implementation.**
- Define a map from accepted input values to column names, and look the value up; unknown values are rejected.
- Use enums in the schema for sort direction and operators.
- Never spread, merge or pass `req.body`, `req.query` or a parsed JSON value into an ORM filter, `include` or `select`. Parse each accepted field to a primitive with the schema (Pro edition requirements) and build the filter object in code. Reject operator keys that start with `$` in NoSQL input unless the allowlist names them.
- Default stack: map the `sort` parameter to a column before passing it to `.order()` in supabase-js or `orderBy` in drizzle. Keeping the ORM on a version with no open injection advisory is covered in [DEPENDENCIES.md](DEPENDENCIES.md).

**Verify.**
1. Find every query whose table, column, order or operator comes from request data.
2. Confirm each passes through an allowlist map.
3. Send unknown and malicious identifier values (`name;drop table x`, `"id"--`), and a column that exists but is not on the allowlist, to every sort, filter and select parameter; expect 4xx.
4. Send to every endpoint that filters, searches or lists, a body or query value shaped as an object: one that traverses a relation to a column that is not on the allowlist, and one that holds an operator object (`$ne`, `$regex`, or the ORM's `contains`, `startsWith`, `in`). Expect a 4xx or a result identical to the one for a plain value, and no field the allowlist excludes.

**Evidence.** Code review notes listing each dynamic identifier and its allowlist; test output, including the object shaped input cases.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.2.4 [SRC-010]; OWASP SQL Injection Prevention Cheat Sheet, Defense Option 3 [SRC-038]; OWASP WSTG 4.2 WSTG-v42-INPV-05 [SRC-186]; OWASP Top 10 2025 A05:2025 (CWE-89) [SRC-020].

**AI Agent Instruction.** When a request chooses a sort column, filter field, table or operator, write an allowlist map and reject anything not in it. Never pass the raw value to the ORM, even when the ORM claims to escape identifiers.

---

### SEC-API-019: Keep dynamic SQL out of client callable database functions

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database (Supabase), API |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, STATIC ANALYSIS |

**Requirement.** Database functions and stored procedures callable by clients MUST NOT build SQL text from their arguments; where dynamic SQL is unavoidable, arguments MUST be passed with `EXECUTE ... USING` and identifiers MUST come from a fixed allowlist inside the function.

**Why.** A function exposed as an RPC is a public endpoint. Dynamic SQL inside it is injectable even when the application code calls it with bound parameters.

**Implementation.**
- Write functions in plain SQL or PL/pgSQL with static statements.
- Where dynamic SQL is needed, use `format()` with `%I` for allowlisted identifiers and `USING` for values, never `%s` with arguments.
- Function privileges, search path and schema placement are covered in [DATABASE-SECURITY.md](DATABASE-SECURITY.md).

**Verify.**
1. List every function in exposed schemas and grep their bodies for `EXECUTE`, `format(` and string concatenation.
2. Review each hit for arguments reaching query text.
3. Call each such RPC with injection payloads in every argument in a non production database.

**Evidence.** Function list with review notes; test output.

**Exceptions.** None for client callable functions. Functions in unexposed schemas called only by trusted jobs are reviewed under SEC-API-017.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.2.4 (L1; stage set to LAUNCH because a client callable RPC is the same exposure as any query path) [SRC-010]; OWASP SQL Injection Prevention Cheat Sheet, Defense Option 2 [SRC-038]; Supabase, Securing your API (Data API exposure) [SRC-072].

**AI Agent Instruction.** When you write a Postgres function that clients can call, do not build SQL strings from its arguments. If dynamic SQL is required, use `EXECUTE ... USING` and an internal identifier allowlist, and flag the function in your change summary for review.

---

### SEC-API-020: Never run shell commands built from untrusted data

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API, Backend, Serverless, AI features |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Code MUST NOT pass request data, file names, third party data or model output into a shell command string, and any subprocess MUST be started with an argument array and no shell. Untrusted data MUST NOT be the program, an option, or the script or expression argument of a shell or interpreter (for example `-c`, `-e`, `--upload-pack`, `--exec`, `-o ProxyCommand`). A value MAY be a positional argument only when the program is not a shell or interpreter, the value matched an allowlist pattern that forbids a leading dash, and it follows a literal `--` separator wherever the program supports one. An argument array with no shell is not enough on its own: `execFile`, `spawn`, `execa` and `fork` with a user controlled argument still run commands through programs such as `git`, `tar`, `ssh`, `find`, `env`, `xargs`, `curl` and `ffmpeg`.

**Why.** Shell metacharacters in untrusted data run arbitrary commands on the server, which gives full control of the host and every secret it holds.

**Implementation.**
- Use `execFile` or `spawn` with an argument array and `shell: false`, never `exec` or `execSync` with a built string.
- Validate each argument against an allowlist of exact values or a strict pattern with no leading dash, and place untrusted values after a literal `--` where the tool supports it.
- Prefer a library over calling a binary (for example an image library instead of a command line tool).

**Verify.**
1. Run Semgrep for `child_process.exec`, `execSync`, `spawn` with `shell: true`, and template literals passed to any process API.
2. Run Semgrep for `execFile`, `spawn`, `execa` and `fork` whose first argument is a shell, an interpreter, `git`, `tar`, `ssh`, `find`, `env`, `xargs`, `curl` or `ffmpeg`, or whose argument array holds a non literal element. Review every remaining subprocess call and list the source of each untrusted argument.
3. For each subprocess call that takes an untrusted value, send a help flag, a version flag, a short option and an output option in every untrusted argument position and assert the value is rejected or treated as data.

**Evidence.** Semgrep report with zero unresolved findings, the list of reviewed subprocess sites with the source of each untrusted argument, and the option probe results.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.2.5 [SRC-010]; OWASP Top 10 2025 A05:2025 [SRC-020]; OWASP Top 10 for LLM Applications 2026 LLM10:2026 [SRC-025].

**AI Agent Instruction.** Never build a shell command string from input, filenames or model output. Use an argument array with no shell. If a feature seems to need shell execution of user influenced data, stop and report it. Shell commands a model chooses follow SEC-AI-040 in AI-SECURITY.md.

---

### SEC-API-021: Never evaluate untrusted data or model output as code

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | API, Backend, Serverless, AI features |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Server code MUST NOT pass request data, stored user content, third party data or model output to `eval`, `new Function`, the `vm` module, string arguments of `setTimeout` or `setInterval`, or any other dynamic code execution API. This includes indirect forms (indirect or global `eval`, `Function` called without `new`, `vm.Script`, `vm.compileFunction`, `import()` or `require()` with a non constant specifier), a subprocess started as an interpreter with a script or expression argument, and any library that parses text into something executable (expression evaluators, JSONata, lodash `template`). A template engine that compiles untrusted text is dynamic code execution: server side template engines MUST compile only templates from the codebase or an admin controlled store, and user input or model output MUST be passed only as template data. Dependency code that request data can reach and that evaluates its input counts as server code for this requirement.

**Why.** Dynamic evaluation of attacker influenced text is remote code execution. Model output is attacker influenced whenever the prompt or retrieved content can be.

**Implementation.**
- Replace dynamic evaluation with a parser, a lookup table or a fixed set of handlers.
- Load templates from files or a fixed registry and pass untrusted values as variables. For user customizable emails or pages, offer named placeholders and replace them with plain string substitution after encoding.
- Where a product must run model generated code, it runs in an isolated sandbox as required in [AI-SECURITY.md](AI-SECURITY.md), never in the app process.
- Format strings: never use request data as the format template of a `printf` style, logging or string formatting call (for example C and C++ `printf`, Python `str.format` or `%` on text the caller wrote, Go `fmt.Sprintf`). Pass the data as an argument to a constant template. JavaScript template literals written in the code are not affected, but a server that builds a template from request data falls under the template rule above.

**Verify.**
1. Run Semgrep for `eval(`, `new Function(`, `Function(`, `vm.run*`, `vm.Script`, `vm.compileFunction`, `import(` and `require(` with a non constant specifier, and string arguments to timers, then run the rule over the indirect forms named in the Requirement. List the expression and template libraries in the dependency list and trace each call site that receives request or stored data.
2. Review each hit and trace its input to a constant source.
3. For each dependency hit, trace it with `pnpm why` or `npm ls` and classify it as reachable from request handling or build only. A build only hit is not a finding.
4. Search for template compile or render calls whose template argument is not a constant or a file path, then send template syntax (`{{7*7}}`, `${7*7}`, `<%= 7*7 %>`) in every field that feeds a template or an expression; the output must show the literal text. Send format directives (`%s%s%s%n`, `{0.__class__}`, `{}`) in every field that reaches a logging or string formatting call in a language that interprets them; the output must show the literal text.

**Evidence.** Semgrep report with zero unresolved findings, the list of reviewed eval, template, expression and format string sites, and the template probe output.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.3.2 [SRC-010]; OWASP Top 10 for LLM Applications 2026 LLM10:2026 [SRC-025]; NIST SP 800-218A PW.5.1 [SRC-051]; OWASP Top 10 2025 A05:2025 [SRC-020]; OWASP WSTG 4.2 WSTG-v42-INPV-18 [SRC-186]; MITRE CWE-1336 [SRC-263].

**AI Agent Instruction.** Never use `eval`, `new Function` or `vm` on data that is not a constant in the codebase, and never on model output. If a feature asks you to run generated code, stop and point to the sandbox requirement in AI-SECURITY.md.

---

## Backend services

### SEC-API-027: Authorize at the point of data access, never only in Proxy

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Backend, API, SaaS, Web (Next.js) |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, STATIC ANALYSIS, DYNAMIC TEST |

**Requirement.** Every read and write of protected data MUST go through server only code that checks the caller's authorization at the point of access, and a check in Next.js Proxy (formerly Middleware) or any edge routing layer MUST NOT be the only authorization for a route or action.

**Why.** Proxy checks run on routing and cookies only; they can be skipped by calling a Server Action or Route Handler directly, and they do not know which record is being read.

**Implementation.**
- Put data access in a Data Access Layer marked server only, where each function takes the verified identity and checks permission.
- Use Proxy only for redirects and early rejection, never as the access decision.
- Rules for what each role may reach are in [AUTH.md](AUTH.md).
- Default stack: import `server-only` in the Data Access Layer so client imports fail the build.

**Verify.**
1. List every route protected in Proxy and confirm the matching handlers or data functions repeat the check.
2. Call each protected Server Action and Route Handler directly with a session that Proxy would redirect; expect denial.
3. Search for database client imports outside the Data Access Layer.

**Evidence.** Review notes mapping Proxy rules to handler checks; direct call test output.

**Exceptions.** No acceptance is available: a finding here is in the authorization class under Protected classes in STANDARD.md, and the fix is to put the check at the point of data access.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.3.1 [SRC-010]; Next.js Authentication guide, Optimistic versus secure checks [SRC-080]; Next.js Data Security guide, Data Access Layer and `server-only` [SRC-078].

**AI Agent Instruction.** Put authorization checks inside the server function that reads or writes the data. Never rely on Proxy or Middleware as the access check. If you find a route protected only in Proxy, add the check at the data layer or report it.

---

## Background jobs and queues

### SEC-API-056: Keep queues off the Data API unless each exposed queue is locked down

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Database (Supabase), Backend |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST |

**Requirement.** Supabase Queues MUST NOT be exposed through the Data API unless a client must send or read messages itself, and when "Expose Queues via PostgREST" is on, every `pgmq.q_` table MUST have RLS enabled with policies scoped to the messages that client may touch, and `anon` MUST hold no grant on any `pgmq_public` function.

**Why.** Supabase documents that RLS is not enabled by default on the queue tables. Once the `pgmq_public` functions are exposed, anyone with the public project key can call `send` to plant a job that a worker then runs with a key that bypasses RLS, call `read` to see other users' messages, or call `pop` or `delete` to drop work such as a deletion request.

**Implementation.**
- Default to server side enqueueing: a Route Handler, Server Action or database function authenticates the caller, parses the payload (a Pro edition requirement) and sends the message over a server connection. Workers read with a server credential.
- If clients must use a queue directly, enable RLS on its `q_` table, write a policy per allowed operation, and grant only the operations needed: `send` needs select and insert, `read` and `pop` need select and update, `archive` and `delete` need select and delete.
- Grant to `authenticated` only on queues meant for clients, and never to `anon`. Never use the `service_role` key or the `postgres` role in client code.
- Messages a client enqueued stay untrusted: the worker still runs Pro edition requirements on them.
- General Data API exposure rules are in [DATABASE-SECURITY.md](DATABASE-SECURITY.md).

**Verify.**
1. Open Integrations, Queues, Settings in the Supabase Dashboard and record whether "Expose Queues via PostgREST" is on, and whether `pgmq_public` is in the exposed schemas list.
2. If it is on, run `select tablename, rowsecurity from pg_tables where schemaname = 'pgmq' and tablename like 'q\_%';` and expect `rowsecurity = true` on every row.
3. Run `select grantee, routine_name, privilege_type from information_schema.routine_privileges where routine_schema = 'pgmq_public';` and expect no row for `anon`.
4. With only the publishable key and no session, call `supabase.schema('pgmq_public').rpc('send', { queue_name: '<internal queue>', message: {} })` and `rpc('read', { queue_name: '<internal queue>', sleep_seconds: 0, n: 1 })` in a non production project; both must fail with a permission error.

**Evidence.** Queues settings screenshot or export; query output for RLS and grants; failed anonymous call output.

**Exceptions.** Projects that do not use Supabase Queues; record that. Otherwise no acceptance is available: a finding here is in the protected classes in STANDARD.md, and the fix is to lock down each exposed queue or remove it from the Data API.

**References.** Supabase Queues Quickstart, Expose Queues to client side consumers, Add an RLS policy on your tables in `pgmq` schema, and Grant permissions to `pgmq_public` database functions [SRC-257]; OWASP ASVS 5.0.0 v5.0.0-8.2.2, v5.0.0-8.3.1 [SRC-010]; OWASP ASVS 5.0.0 v5.0.0-13.2.2 (L2, supporting anchor for least privilege grants) [SRC-010]; Supabase, Securing your API (Data API exposure) [SRC-072]; OWASP Top 10 2025 A01:2025 [SRC-020].

**AI Agent Instruction.** Enqueue jobs from server code after authenticating and parsing the input. Do not turn on "Expose Queues via PostgREST" or grant `pgmq_public` functions to `anon` to make a feature work. If a client must use a queue directly, enable RLS on that queue's table, add policies and the minimum grants in a migration, and flag the change for review.

---

### SEC-API-057: Keep job platform request verification on in deployed environments

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Backend, Serverless, API |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW, DYNAMIC TEST, STATIC ANALYSIS |

**Requirement.** Every endpoint that a scheduler or job platform calls to run work (a Vercel Cron route, an Inngest serve endpoint, a QStash destination) MUST check the platform's secret or signature with the platform's verifier, over the raw request body where the platform signs the body, before any job code runs, and production and preview deployments MUST NOT set any option that turns that check off.

**Why.** A job endpoint is a public URL that runs privileged work. Inngest documents that its TypeScript SDK skips signature verification when `INNGEST_DEV=1` or `isDev: true` is set; copied into a deployed environment, that lets anyone send a forged event and run any function. QStash warns that whoever holds the signing keys can send requests that look like QStash, and that verifying against a re-serialized body fails or invites shortcuts.

**Implementation.**
- Vercel Cron: compare the `Authorization` header with `Bearer ` plus `CRON_SECRET` in constant time (SEC-API-001 and a Pro edition requirement in [API-SECURITY.md](API-SECURITY.md)).
- Inngest: set `INNGEST_SIGNING_KEY` in each deployed environment, and `INNGEST_SIGNING_KEY_FALLBACK` during rotation. Set `INNGEST_DEV` only in local `.env` files, never in Vercel or Render settings, and never hardcode `isDev: true`.
- QStash: use the SDK `Receiver` with the current and next signing keys, pass the raw body string, and check the `sub` claim matches the endpoint URL.
- Store signing keys as secrets (a Pro edition requirement in [SECRETS.md](SECRETS.md)).
- Where no HTTP trigger is needed, run the work in a Render background worker or cron job, which takes no incoming traffic.
- Stage reason: this is the job platform case of SEC-API-001, a LAUNCH BLOCKER, so it starts at LAUNCH.
- Default stack (checked 2026-10-03): a Render cron job runs a shell command, not an HTTP route, and can hold the same environment variables and API keys as any other Render service. Give each cron job only the variables it needs (for example through a separate environment group), and make the command exit when the work is done.

**Verify.**
1. Export environment variable names for every deployed environment (Vercel production and preview, Render) and confirm each job platform's signing key or `CRON_SECRET` is set and `INNGEST_DEV` is absent.
2. Run `grep -rnE "isDev:\s*true|INNGEST_DEV" --include=*.ts --include=*.js .` outside test folders and expect no hit in code that ships.
3. In a deployed non production environment, send each job endpoint an unsigned request, a request with a wrong secret, and a correctly signed request whose body has one byte changed; each must return 401 or 403, and the platform and app logs must show no job run.
4. For command style jobs (Render cron jobs, scripts run by a scheduler), list the environment variables each one can read and confirm none holds a secret the job does not use.

**Evidence.** Environment variable name exports; grep output; rejected request test output per endpoint.

**Exceptions.** None in deployed environments. Local development may disable verification.

**References.** Inngest, Signing Keys, Configuring the signing key and Signing keys and branch environments [SRC-260]; Upstash QStash, Verify Signatures, Via SDK and Manual verification [SRC-261]; Vercel, Managing Cron Jobs, Securing cron jobs [SRC-164]; Render, Cron Jobs and Background Workers (workers receive no incoming network traffic) [SRC-259]; OWASP ASVS 5.0.0 v5.0.0-13.2.1 (L2, stage follows SEC-API-001) [SRC-010]; OWASP Top 10 2025 A08:2025 (CWE-345) [SRC-020].

**AI Agent Instruction.** When you add a cron route, Inngest function or QStash consumer, wire the platform's verifier before any job code, and keep dev mode flags out of deployed configuration. Never set `INNGEST_DEV`, `isDev: true` or an equivalent bypass to fix a failing deployment; report the signing key problem instead.

---

## Server side request forgery

### SEC-API-034: Restrict fixed outbound calls to an allowlist of hosts

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | API, Backend, Serverless, AI features |
| Automation | PARTIAL |
| Verification method | STATIC ANALYSIS, CODE REVIEW |

**Requirement.** Where the server calls only known services, outbound requests MUST go only to hosts in a server side allowlist, and users MUST NOT be able to supply a full URL, host or port for those calls. A host written as a constant in code or read from server configuration meets this requirement; only a scheme, host or port that originates from a request, stored user content or model output fails it. A request derived value placed in the path or query of a call to a fixed host MUST match a strict identifier pattern (for example 1 to 64 letters, digits, underscore or dash) or pass through URL component encoding plus a check that the value is not `.` or `..`, and MUST NOT be able to add a slash, a parent directory segment, a question mark, a fragment, an at sign, a backslash or an encoded slash. A route MUST NOT forward a client supplied path or query to a provider using the server credential. The URL MUST be built with the URL constructor, and the code MUST assert the resulting origin and expected path prefix before sending.

**Why.** If any part of a request target comes from input, an attacker points the server at internal services or cloud metadata endpoints and reads what they return.

**Implementation.**
- Build outbound URLs from configured base URLs plus validated path segments or IDs. Do not build them by plain concatenation. The URL parser reads everything before the last at sign in the authority as credentials, so a value that starts with `@` and is appended to a base that has no path moves the request to another host, and a `startsWith` check on the base string does not see it [SRC-369]. The parser also resolves parent directory segments in a concatenated value, including the encoded form `%2e%2e`. Component encoding such as `encodeURIComponent` leaves `.` and `..` unchanged, and a path segment of `..` resolves to the parent, so check for those two values as well. Checked on Node.js v22.23.2.
- Keep the allowlist in configuration and check it in the shared HTTP client.
- Hullproof has no researched source on egress filtering for Vercel Functions, Supabase Edge Functions or Render, so the check lives in code.

**Verify.**
1. Run Semgrep for `fetch`, `axios` and `got` calls whose URL includes request data.
2. Confirm each outbound call goes through the shared client with the host allowlist.
3. Try to change the host through every user controlled field; expect rejection. In each id or path parameter send a slash, a parent directory segment (`../`, `..` alone and `%2e%2e`), a question mark, a fragment, an at sign, a backslash and an encoded slash with a mocked client, and assert the outbound URL equals the expected URL or the request is rejected.
4. Trace each outbound provider call whose resource identifier (customer id, subscription id, account id) comes from the database, and confirm none is read from a column a client can write (SEC-AUTHZ-004 in AUTH.md). A client writable provider id used in a keyed server call lets a user act on another customer's provider resource.

**Evidence.** Semgrep report; allowlist configuration.

**Exceptions.** Features that must fetch user supplied URLs follow SEC-API-035 instead.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.3.6 (L2, promoted to LAUNCH in the Hullproof ASVS stage mapping) [SRC-010]; OWASP SSRF Prevention Cheat Sheet, Case 1 [SRC-045]; OWASP API Security Top 10 2023 API7:2023 [SRC-021]; Escape, State of Security of Vibe Coded Apps (4 confirmed SSRF cases) [SRC-007]; WHATWG URL Standard, authority state and path parsing [SRC-369].

**AI Agent Instruction.** Build outbound URLs from configured base URLs only. Never let a request field set the scheme, host or port of a server side call. Route every outbound call through the shared client.

---

### SEC-API-035: Guard user and model supplied URLs before connecting

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | API, Backend, Serverless, AI features |
| Automation | PARTIAL |
| Verification method | AUTOMATED TEST, DYNAMIC TEST, STATIC ANALYSIS |

**Requirement.** Where a user, a stored record, an imported file or a model may choose a URL, host, path or file that the server requests (link previews, import from URL, user configured outbound webhooks, AI fetch tools, server side renderers), the server MUST allow only `http` and `https`, resolve the host, reject the request unless every resolved address is a publicly routable global unicast address (reject anything the IANA special purpose address registries do not mark as globally reachable, using a maintained address library), and connect only to the address it checked (address pinning). The guard MUST run in the connection path (a connect hook on the HTTP agent, or an egress proxy) when the connection is made, not only at registration or before the call, so a delivery worker that runs later, and every redirect hop, is checked again. Redirects MUST be refused, or each hop MUST pass the same guard. Every outbound call whose host, port or URL is not a code constant MUST use the guarded client, and a lint rule MUST fail the build on direct use of any other HTTP client outside that module. Addresses that arrive as IPv4 mapped, IPv4 compatible (`::/96`), NAT64 or 6to4 IPv6 forms MUST be unwrapped to the IPv4 address and checked. A server side renderer that loads subresources (headless browser, HTML to PDF, SVG converter) MUST run with request interception that applies the same guard, or in an environment with no route to internal services.

| Blocked range (minimum test list) | Meaning |
|---------------|---------|
| 0.0.0.0/8 and `::` | Unspecified |
| 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24 and 2001:db8::/32 | Documentation |
| 224.0.0.0/4 and ff00::/8 | Multicast |
| 240.0.0.0/4 and 255.255.255.255 | Reserved and broadcast |
| 2001::/32 and 64:ff9b:1::/48 | Teredo and local use NAT64 |
| 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, fc00::/7 | Private |
| 100.64.0.0/10 | Shared address space (carrier grade NAT) |
| 127.0.0.0/8 and `::1` | Loopback |
| 169.254.0.0/16 and fe80::/10 | Link local, including the cloud metadata address 169.254.169.254 |
| 192.0.0.0/24 and 198.18.0.0/15 | Protocol assignments and benchmarking |
| `::/96`, `::ffff:0:0/96`, 64:ff9b::/96 and 2002::/16 | IPv4 compatible, IPv4 mapped, NAT64 and 6to4 forms: unwrap, then check the IPv4 address |

The table is the minimum set a test must cover, taken from the IANA special purpose address registries [SRC-422] [SRC-423]. The rule is the allow only test above, so an address that is in neither the table nor the registries as globally reachable is still refused. Add the metadata addresses of any other cloud the product runs on.

**Why.** A user or prompt supplied URL can target `169.254.169.254`, `localhost` or an internal service, and DNS can return a safe address at check time and an internal one at connect time.

**Implementation.**
- Put the guard in one shared client used by every URL taking feature, and keep the table in the Requirement as the only copy of the test list.
- Parse the URL with the standard URL parser and read the host from the parsed result, never from the string: the parser treats everything before the last at sign in the authority as credentials, so `http://allowed.example@127.0.0.1/` has the host 127.0.0.1 [SRC-369]. Reject credentials in the URL, and pin the connection to the checked IP to stop DNS rebinding.
- Model output and retrieved content count as user supplied for this requirement.

**Verify.**
1. Unit test the guard with `http://169.254.169.254/`, `http://localhost`, `http://127.1`, `http://2130706433`, `http://[::1]`, `http://[::ffff:127.0.0.1]`, `http://allowed.example@127.0.0.1/`, `file:///etc/passwd` and `gopher://` URLs, and one address from each row of the table (including `http://[::127.0.0.1]/` and a multicast address such as `http://224.0.0.1/`); all must be rejected.
2. Test a hostname that resolves to a private address; it must be rejected.
3. Submit the same payloads to every URL taking feature in a deployed non production environment. For a server side renderer, render a document whose images and stylesheets name loopback and a local file, and confirm neither is fetched.
4. Insert a private URL directly into the table or queue that a delivery worker reads, run the worker, and confirm no connection is made.
5. Run the guard against a resolver stub that answers a public address first and `127.0.0.1` second; the connection must not reach the second address.
6. Point each URL taking feature at a server you control that answers 302 to the cloud metadata address and to loopback; neither request may happen.
7. List every call site of an outbound HTTP client (fetch, axios, got, undici, node http and https, and any SDK that takes a URL) with its URL source. Each must be a code constant or use the guarded client; the lint rule must fail on a direct call.

**Evidence.** Guard unit test output; dynamic test output per feature; the worker, resolver stub and redirect test output; the call site list.

**Exceptions.** None at LAUNCH. A product in which no server code requests a URL, host, path or file chosen by a user, a stored record, an imported file or a model is out of scope; the answer to GATE-URLFETCH records the search that shows it.

**References.** OWASP ASVS 5.0.0 v5.0.0-1.3.6 (promoted to LAUNCH in the Hullproof ASVS stage mapping) [SRC-010]; OWASP SSRF Prevention Cheat Sheet, Case 2 [SRC-045]; IANA IPv4 and IPv6 Special-Purpose Address Registries [SRC-422] [SRC-423]; Standard Webhooks specification 1.0.0, Server side request forgery (SSRF) [SRC-227]; OWASP API Security Top 10 2023 API7:2023 [SRC-021]; OWASP Top 10 2025 A01:2025 [SRC-020]; Escape, State of Security of Vibe Coded Apps [SRC-007]; WHATWG URL Standard, authority state [SRC-369].

**AI Agent Instruction.** When any feature fetches a URL that came from a user, a stored record, retrieved content or model output, call the shared URL guard first. Never write a new fetch path that skips it. If the guard blocks a legitimate URL, report it; do not loosen the blocked ranges.

---

## File uploads

### SEC-API-045: Never serve uploads as active content from the app origin

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | API, Web, Cloud |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, CONFIG REVIEW |

**Requirement.** Any file the server did not generate itself (user uploads, files fetched from third party URLs, model supplied files) MUST be served from a separate origin or with `Content-Disposition: attachment`, so that no uploaded file renders as HTML or runs script in the application's origin. A separate origin MUST be on a different registrable domain from the application and from any domain that shares cookies with it; a sibling subdomain of the application is a separate origin but the same site, and does not meet this. A file origin on the same registrable domain is acceptable only when every response carries `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff` and a `Content-Security-Policy: sandbox` header. This requirement applies wherever the product accepts, fetches or stores a file that a user can later open.

**Why.** An uploaded HTML or script file served inline from the app origin runs with the user's session, which is stored XSS through the file feature.

**Implementation.**
- Serve files from the storage provider's domain or a dedicated file domain on a different registrable domain, not the app domain or a subdomain of it.
- When files must pass through the app, send `Content-Disposition: attachment` and the stored, verified content type.
- Default stack: R2 presigned URLs work only on the `r2.cloudflarestorage.com` endpoint, which is already a separate origin.

**Verify.**
1. Upload an HTML file (where allowed, or by bypassing the client) and open its download URL.
2. It must download or render from a different origin, never execute in the app origin. From the file origin, fetch an authenticated app endpoint with credentials and read the parent domain's cookies; both must fail or return nothing. Where the file origin shares a registrable domain with the app, confirm the attachment, `nosniff` and sandbox headers.
3. Upload a file with a `Content-Type` that disagrees with its content, read it back, and confirm the served `Content-Type` is the stored, verified type and not an echo of the client supplied value.

**Evidence.** Test output; file serving configuration.

**Exceptions.** None.

**References.** OWASP ASVS 5.0.0 v5.0.0-3.2.1 [SRC-010]; OWASP File Upload Cheat Sheet, File Storage Location [SRC-042]; Cloudflare R2 docs, S3 endpoint only [SRC-125].

**AI Agent Instruction.** Do not serve uploaded files inline from the app's own domain. Serve them from storage or with an attachment disposition.
