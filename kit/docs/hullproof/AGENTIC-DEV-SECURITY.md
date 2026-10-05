# Agentic Development Security

| Field | Value |
|-------|-------|
| Domain codes | SEC-AGENT |
| Topics covered | MCP Security, AI-Assisted Development |
| Part of | Hullproof Security Standard, see STANDARD.md |

This document covers the workflow in which AI coding agents (Claude Code, Cursor and similar) write, run and ship code: the secrets and production access they hold, their command and MCP permissions, prompt injection through repository content, review of the code they produce, and the MCP servers a product exposes to its own users. AI features inside the product are in AI-SECURITY.md, general secret handling in SECRETS.md, dependency and CI controls in DEPENDENCIES.md, and branch protection and review policy in GOVERNANCE.md.

Government guidance advises using agents only for low risk tasks at first (CISA and partners, Careful Adoption of Agentic AI Services, SRC-068). Hullproof lets coding agents write security sensitive code because the controls below keep merge and deploy with a human: agents hold no production secrets, have no direct path to production, and every change they author passes the same gates as human code. If a team removes those controls, this reasoning no longer holds.

<!-- hullproof:index:start -->

> **Free edition.** This document contains 5 of the 32 requirements in this domain: every BLOCKER and every CRITICAL requirement in it. Hullproof Pro holds the other 27. Pro goes further on how far you trust your coding agents: what each one may run and reach, how its tools and servers are vetted, and how its changes are reviewed.

## Requirement index

| ID | Title | Severity | Stage | Applies To |
|---|---|---|---|---|
| [SEC-AGENT-007](#sec-agent-007-authenticate-every-call-to-a-product-mcp-server) | Authenticate every call to a product MCP server | BLOCKER | LAUNCH | AI features, API |
| [SEC-AGENT-008](#sec-agent-008-authorize-each-product-mcp-tool-call-for-the-caller) | Authorize each product MCP tool call for the caller | BLOCKER | LAUNCH | AI features, API |
| [SEC-AGENT-009](#sec-agent-009-no-token-passthrough-from-a-product-mcp-server) | No token passthrough from a product MCP server | CRITICAL | LAUNCH | AI features, API |
| [SEC-AGENT-011](#sec-agent-011-no-production-secrets-in-coding-agent-context) | No production secrets in coding agent context | BLOCKER | LAUNCH | Agentic workflow |
| [SEC-AGENT-014](#sec-agent-014-no-direct-agent-path-to-production) | No direct agent path to production | CRITICAL | LAUNCH | Agentic workflow |
<!-- hullproof:index:end -->

---

## Coverage map

Severity, stages, exceptions, and the Production Security Gate are defined in [STANDARD.md](STANDARD.md).

<!-- hullproof:coverage-map:start -->
Each requirement in this document is listed in exactly one row. A row with no requirements points to the document that owns that topic. "Primary for" names the duplicate clusters whose one owning requirement is in that row; report one finding per cluster against the owner.

| Area | Also see | Primary for | Requirements in this document |
|------|----------|-------------|-------------------------------|
| Authentication on MCP servers the product exposes | None | None | SEC-AGENT-007 |
| Per call authorization on product MCP tools | AI-SECURITY.md | MCP server authorization | SEC-AGENT-008 |
| No token passthrough to upstream APIs | None | None | SEC-AGENT-009 |
| MCP servers and third party tools the product consumes | AI-SECURITY.md | None | None in this document |
| Production secrets kept out of agent context | SECRETS.md | None | SEC-AGENT-011 |
| No direct agent path to production: push, migrate, deploy | DEPENDENCIES.md | None | SEC-AGENT-014 |
| Package hallucination and slopsquatting in agent suggested dependencies | DEPENDENCIES.md | None | None in this document |
| Which security tasks an agent may perform and which need a human | GOVERNANCE.md | None | None in this document |
| Agent threats in the threat model | GOVERNANCE.md | None | None in this document |
<!-- hullproof:coverage-map:end -->

<!-- hullproof:gates:start -->
### Applicability gates

Answer each gate once, with evidence, in the Gates section of `docs/security/STAGE.md`. A gate answered No marks the IDs listed for it NOT APPLICABLE, with the gate name as the reason. A bare No is not evidence: the answer needs a recorded search or a dependency check, or for a fact no repository can show, the owner's signed and dated answer. For a gate whose list holds a BLOCKER, a No is valid only when the auditor re runs the search over every tracked file except dependency folders and lockfiles, on the audited commit, and saves the command, the number of files searched and the result. Search terms are hints, and the gate is answered from its question about the data model, the routes or the dependencies. An ID that more than one gate names is NOT APPLICABLE only when every gate naming it is answered No. A gate answered Yes, or not answered, leaves its IDs in scope. See Not applicable and evidence of absence in the security standard.

| Gate | Question | Evidence of absence | A No answer marks these NOT APPLICABLE |
|------|----------|---------------------|----------------------------------------|
| GATE-MCP | Does the product expose an MCP server that outside clients or agents can call? | Search every tracked file, including the package manifest of every workspace, workspace folders and serverless folders, for @modelcontextprotocol/sdk, McpServer, mcp-handler, an /mcp route, and the protocol terms tools/list, tools/call and jsonrpc, and for a route that dispatches on a method field. A file that mentions mcp, tools/list or tools/call is an MCP server until read. Record the commands, the number of files searched and that nothing was found, or record the owner's written answer for a fact no repository can show. | SEC-AGENT-007 (BLOCKER), SEC-AGENT-008 (BLOCKER), SEC-AGENT-009 |
<!-- hullproof:gates:end -->

---

## MCP servers the product exposes

### SEC-AGENT-007: Authenticate every call to a product MCP server

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | AI features, API |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, AUTOMATED TEST, CODE REVIEW |

**Requirement.** An MCP server the product exposes over HTTP with tools that read or change non public data MUST authenticate every request with a bearer token sent in the Authorization header, MUST accept only tokens issued for that server as audience and within their validity window, and MUST answer any missing, invalid, expired or wrong audience token with HTTP 401. Token audiences MUST be separate: a token accepted by the MCP server is not accepted by any other API route, and a token issued for the web or mobile app is not accepted by the MCP server. An MCP token carries a scope per tool group and expires in 1 hour or less (the lifetime is Hullproof policy; no external source).

**Why.** A product MCP server is an API that model clients call on a user's behalf. Without authentication, anyone who finds the endpoint can call its tools against user data. Without audience checks, a token issued for another service is replayed against this one. The protocol makes authorization optional, so this failure is easy to ship.

**Implementation.**
- Implement the MCP authorization specification: OAuth 2.1, Protected Resource Metadata (RFC 9728), and audience validation of each access token.
- Reject tokens in query strings; read them only from the Authorization header.
- Validate expiry and audience on every request; the 2026-07-28 protocol is stateless, so never treat a state handle passed as a tool argument as proof of identity.
- Default stack: when Supabase Auth issues the tokens, verify the JWT signature, `exp` and `aud` server side before any tool runs.
- Owned by SEC-AGENT-008 in AGENTIC-DEV-SECURITY.md for this root cause (MCP server authorization); report one finding.
- Scope: this requirement covers a product MCP server as a resource server. A product that must issue OAuth tokens to MCP clients itself should delegate that to a managed authorization server and, in its dashboard, confirm that authorization codes are single use and short lived and that client registration and redirect URIs are exact matches (ASVS V10.4). Record the choice in the architecture record (a Pro edition requirement).
- Supabase documents the `aud` claim of its access tokens as `authenticated` or `anon`, a role value and not a per server audience, so a stock token cannot show that it was meant for the MCP server (Supabase JWT claims reference, checked 2026-10-03 [SRC-356]). Because of that, issue the MCP server its own short lived token with its own audience, or run the check on a custom audience claim, and verify it as in Verify steps 1 and 2. Supabase Auth documents the `aud` claim and a custom access token hook that sets claims.

**Verify.**
1. Call each tool with no token and expect 401.
2. Call with an expired token, a token for another audience, and a token in the query string, and expect 401 each time.
3. Call with a valid token and confirm success.
4. Keep these cases as automated tests in CI.
5. Present a valid web or mobile session token of the same user to the MCP server and expect 401.
6. Present a valid MCP token at an ordinary API route and expect 401.

**Evidence.** Passing automated test run covering the token cases in steps 1 to 3, 5 and 6 for every exposed tool.

**Exceptions.** Not applicable when the product exposes no MCP server; record the search (MCP server code and dependencies) that shows it.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.3.1, v5.0.0-9.2.1, v5.0.0-10.3.1 [SRC-010]; MCP Specification 2026-07-28 Authorization: Token Handling and Access Token Usage: Token Requirements [SRC-144]; MCP Security Best Practices 2026-07-28 State Handle Hijacking: Mitigation [SRC-145]. Stage: v5.0.0-10.3.1 is ASVS L2, promoted to LAUNCH because the MCP specification requires audience validation for MCP servers. Supabase JWT claims reference (aud values) [SRC-356].

**AI Agent Instruction.** When building or changing a product MCP server, add token verification before any tool handler runs and write the four negative tests. Refuse to ship a tool that reads or changes non public data without authentication, and refuse to accept tokens from query strings.

---

### SEC-AGENT-008: Authorize each product MCP tool call for the caller

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | AI features, API |
| Automation | PARTIAL |
| Verification method | DYNAMIC TEST, AUTOMATED TEST, CODE REVIEW |

**Requirement.** Every tool call to a product MCP server MUST be authorized on the server against the authenticated caller's permissions, scopes and tenant, at the time of the call, before the tool reads or changes data. A tool handler that serves user data MUST run its database queries as the calling user so that row level security applies; the service role key, an owner connection string and any client built from them MUST NOT be used by or reachable from the import graph of any tool handler.

**Why.** Authentication proves who is calling, not what they may do. A low privilege caller who can invoke an admin tool, or a tool that accepts any record ID without an ownership check, exposes other users' and tenants' data. Checking permissions once at connection time and reusing them later lets revoked access keep working.

**Implementation.**
- Map each tool to the permission or scope it needs and check it in the handler, deny by default.
- Apply the same ownership and tenant checks as the equivalent API route; reuse the existing authorization helpers.
- The tool list returned to a caller may be filtered by scope, but filtering the list is not authorization; the handler still checks.
- Default stack: run database queries as the calling user so Supabase RLS applies, never with the service role key in a tool handler that serves user data. An admin client dressed as a user scoped client behind an owner filter is still the service role: one tool that forgets the filter is a cross tenant read.
- Owner note: A missing artefact is one finding, not one per requirement that mentions it.

**Verify.**
1. With a low privilege token, call every privileged tool and expect denial.
2. With user A's token, call each tool with user B's or tenant B's record IDs and expect denial.
3. Revoke a scope and confirm the next call is denied without reconnecting.
4. Call each write tool with a read scoped token and expect 403.

**Evidence.** Passing automated authorization tests for every exposed tool, including cross user and cross tenant cases.

**Exceptions.** Not applicable when the product exposes no MCP server; record the search (MCP server code and dependencies) that shows it.

**References.** OWASP ASVS 5.0.0 v5.0.0-8.2.1 and v5.0.0-8.3.1 [SRC-010]; MCP Specification 2026-07-28 Tools: Security Considerations [SRC-144]; OWASP MCP Security Cheat Sheet section 1 [SRC-146]; CISA and partners Careful Adoption of Agentic AI Services 2026 Risks: Design and configuration [SRC-068].

**AI Agent Instruction.** For every product MCP tool you write, add a server side permission and ownership check in the handler and tests that prove denial for other users and tenants. Never rely on the model, the tool list, or the client to restrict which tools run. If an existing tool lacks this check, report it as a BLOCKER.

---

### SEC-AGENT-009: No token passthrough from a product MCP server

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | AI features, API |
| Automation | PARTIAL |
| Verification method | CODE REVIEW, DYNAMIC TEST |

**Requirement.** A product MCP server that calls upstream APIs MUST use its own separately issued upstream credential for those calls and MUST NOT forward the access token it received from the MCP client.

**Why.** Forwarding the client's token lets upstream services act on a token never meant for them, skips the MCP server's own checks and audit trail, and turns the server into a confused deputy that attackers can use to reach upstream systems with stolen tokens.

**Implementation.**
- Obtain upstream tokens through the upstream provider's own flow and store them server side.
- Strip the incoming Authorization header before any outbound request.
- Log which upstream credential each tool call used, without logging token values.

**Verify.**
1. Search the server code for outbound requests that reuse the incoming Authorization header or token variable.
2. Capture outbound traffic in a test environment and confirm the token sent upstream differs from the token the client presented.

**Evidence.** Code review record and a captured test showing distinct upstream credentials.

**Exceptions.** None for tokens issued to the MCP server as audience. Waiver for other cases needs an owner, a compensating control and an expiry date. Not applicable when the product exposes no MCP server; record the search (MCP server code and dependencies) that shows it.

**References.** MCP Specification 2026-07-28 Security Considerations: Access Token Privilege Restriction [SRC-144]; MCP Security Best Practices 2026-07-28 Token Passthrough: Mitigation [SRC-145]; OWASP ASVS 5.0.0 v5.0.0-10.3.1 [SRC-010]; OWASP Top 10 for Agentic Applications 2026 ASI03 [SRC-023].

**AI Agent Instruction.** Never forward an incoming MCP access token to another service. When a tool needs upstream access, use a separate server held credential and say which one in your change summary.

---

## Secrets and production access

### SEC-AGENT-011: No production secrets in coding agent context

| Field | Value |
|-------|-------|
| Severity | BLOCKER |
| Stage | LAUNCH |
| Applies To | Agentic workflow |
| Automation | PARTIAL |
| Verification method | SECRET SCAN, CONFIG REVIEW |

**Requirement.** Production credentials (production database connection strings, service role keys, production API and payment secret keys, cloud admin tokens, production deploy tokens) MUST NOT be present in the workspace, environment variables, shell profile, MCP server configuration or credential files of any machine or container where a coding agent runs. Coding agents MUST hold only development or staging credentials. A hosted connector, OAuth grant, plugin or MCP server authorized by the developer's account counts as holding a credential: a connector that can change production data, settings, deployments, messages or payments MUST be authorized to development or staging resources only, or be disabled in agent sessions.

**Why.** Neither Claude Code nor Cursor fully blocks an agent from reading secrets. Deny rules miss shell commands that read files without naming them, `.cursorignore` does not cover terminal or MCP tools, and the default sandbox can read `~/.ssh` and `~/.aws/credentials`. A prompt injected or mistaken agent that can reach a production key can read or destroy production data directly. Secrets an agent reads also land in local plaintext transcripts. Keeping production secrets off the machine is the most dependable control because it does not rely on deny rules working or on the agent obeying them.

**Implementation.**
- Keep production secrets only in the hosting platform's environment settings and a password manager, never in local `.env` files.
- Use separate development projects with their own keys for local work.
- Before each session, check the shell environment and any credential files for production values; log out of production CLI sessions on agent machines.
- Default stack: local `.env.local` holds development Supabase, Stripe test mode, Paystack test and similar keys only; production values live in Vercel and Render environment settings; the Supabase service role key for production is never on a laptop.
- From GROWTH, use a separate Supabase organization for production so development roles cannot read the production service role key.
- Owned by a Pro edition requirement in SECRETS.md for this root cause (Environment credential separation); report one finding.
- Agent settings, instruction and MCP files are places where keys end up (an approved command can leave a key in a local settings file). A Pro edition requirement owns the scan of those locations and reports counts and line numbers only; a production value found there is reported here.
- Solo builder separation recipe (one machine, one linked project): (1) create a staging project and keep only its keys in local `.env.local`; (2) keep production keys only in the host environment store (Vercel, Render) and the password manager; (3) link every CLI on the machine, including the Supabase CLI, to the staging project, and unlink production before an agent session if it was linked for a task; (4) run production migrations from CI after merge. Record the staging and production project identifiers in `docs/security/STAGE.md`.

**Verify.**
1. Run Gitleaks or TruffleHog over the working directory including untracked files, and over `~/.config`, shell profiles and any `.env*` files, using the Gitleaks `--redact` flag so findings print without the secret; compare found keys against the key labels and last characters that the provider console shows for production keys (not the shared prefix, which every key from one provider has), never against production values.
2. Run `env | cut -d= -f1` in the agent's shell to list variable names only, and confirm no production variable name appears; where a name is also used in production, ask the owner to check in the provider dashboard which project each local key is bound to, and confirm it is a development project. Never pull production values onto the machine to compare them (for example with `vercel env pull`), because that puts a production secret on the agent machine.
3. Check Supabase, Vercel, AWS, Stripe and similar CLI logins on the machine and confirm none point at production.
4. Confirm every MCP server token in the inventory targets development resources. List every connector the coding agent can load at account, project and user scope and record the organization or project each is authorized to; any grant that includes a production project fails. Ask the agent to list production projects through each connector and expect none.
5. Release environment check: compare the project identifiers in local environment files and CLI link metadata with the production identifiers in `docs/security/STAGE.md`, comparing identifiers and fingerprints, never printing key values. Any match fails.

**Evidence.** Dated scan report and checklist per developer machine and agent container, signed off by the developer, and an export or screenshot of the connector settings. A provider audit log is never proof of absence, because a connector call appears in it as the account owner.

**Exceptions.** A solo builder on one machine meets this requirement with the recipe in Implementation. The exception is not a waiver: production keys on the machine still fail.

**References.** NIST SSDF 1.1 PO.5.1 [SRC-050]; NIST SP 800-218A PO.5.1.R2 and PO.5.1.R6 [SRC-051]; OWASP Top 10 for Agentic Applications 2026 ASI03 [SRC-023]; CISA and partners Careful Adoption of Agentic AI Services 2026 Introduction and Operate: Privileges and authentication [SRC-068]; Claude Code docs Permissions: Read and Edit, Sandboxing: default reads and env, Data usage [SRC-147]; Cursor docs Ignore file [SRC-148].

**AI Agent Instruction.** Never ask for, read, print, copy or use a production credential. If you find one in the workspace, environment or configuration, stop work, report its location (not its value) as a BLOCKER, and tell the developer to remove it and rotate it under a Pro edition requirement. If a task appears to need production access, stop and hand it to a human.

---

### SEC-AGENT-014: No direct agent path to production

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Stage | LAUNCH |
| Applies To | Agentic workflow |
| Automation | PARTIAL |
| Verification method | CONFIG REVIEW |

**Requirement.** Coding agents and the credentials they hold MUST NOT be able to push to the production branch, bypass its rulesets, run production database migrations, or trigger a production deployment; changes reach production only through a merge and deploy performed or approved by a human.

**Why.** Code an agent writes or is tricked into writing should never execute in production without checks. If an agent token can push to `main` or call a deploy API, a single prompt injection or mistaken command ships straight to users. Keeping merge and deploy with a human is also what makes Hullproof's use of agents for sensitive code consistent with guidance to use agents only for low risk tasks.

**Implementation.**
- Protect the production branch with a ruleset that requires a pull request and blocks force pushes and deletions, with no agent GitHub App or agent token on the bypass list.
- Give agent GitHub Apps and tokens the minimum permissions; they may open pull requests but not merge to the production branch.
- Keep production deploy hooks and tokens out of agent reach (SEC-AGENT-011); deploy from the platform's Git integration after merge.
- Default stack: Vercel and Render deploy production from the protected branch only; Supabase production migrations run from CI after merge, not from a local agent session.
- Changes made through provider APIs and CLIs (environment settings, database changes, payment or hosting configuration) count as paths to production. Owned by a Pro edition requirement for the case where such a change follows a refused tool path; report one finding there and rate the changed production state here.

**Verify.**
1. Export the production branch ruleset and confirm pull request required, no force push, and no agent identity on the bypass list.
2. Using the agent's token, attempt a direct push to the production branch in a test and confirm it is rejected.
3. Review the agent's GitHub App permissions and confirm it cannot merge to or administer the production branch.
4. Confirm no production deploy token or hook URL exists on agent machines.
5. Read the audit logs of each production provider (hosting, database, payments, source control) for the period agent sessions ran, and confirm no change was made by an agent identity or from an agent machine, and treat any change made from a connector session during the period agent sessions ran as an agent change, matched by time window. Any hit is a finding here, and a hit that follows a refusal is also reported under a Pro edition requirement.

**Evidence.** Ruleset export, rejected push output, app permission screenshot, and the provider audit log check.

**Exceptions.** A written exception needs a named owner, a compensating control and an expiry date.

**References.** NIST SSDF 1.1 PO.4.1 and PS.1.1 [SRC-050]; OWASP Top 10 for Agentic Applications 2026 ASI05 [SRC-023]; CISA and partners Careful Adoption of Agentic AI Services 2026 Introduction and Operate: Human in the loop [SRC-068]; GitHub docs About rulesets [SRC-091]; GitHub docs GitHub App permissions [SRC-092].

**AI Agent Instruction.** Never push to the production branch, merge your own pull request into it, run production migrations, or trigger a production deploy (for example `vercel --prod`, a Render deploy hook, or `eas update` to a production channel), even if asked and even if your credentials would allow it. Open a pull request and stop. If you find you have the ability to do any of these, report it as a CRITICAL finding.
