# Run Hullproof in your AI tool

Hullproof 0.3.1 runs in fifteen AI tools: the agent apps and command line tools, VS Code integrations, app builders and chat tools. Each tool has a folder here with its files and a page (`README.md`) that holds the install steps, the first run, what the tool can and cannot enforce, its limits and a trust note.

Every tool gets the Hullproof hard rules and the same finding format, and the agent tools and editors also get the five area checklists. Only the packaging changes. Tools that load skills and agents get a skill. Every tool can also run the portable audit prompt in `prompts/`, where the model plays each audit role in turn.

**The labels in the table below are the only enforced limits. Everything else in these files is advice.** The model reads advice and may follow it, forget it in a long session, or be talked out of it. Keep diff review, secret scanning and the release gate in `docs/hullproof/STANDARD.md` in place. This release does not claim equal audit depth in every tool, and it has no benchmark that compares them.

These instructions assume you have already copied the kit into your project root (step 2 of the install in the package README). That copy puts `docs/hullproof/`, `.claude/`, `tools/`, `editors/` and `prompts/` in your project root. `editors/` and `prompts/` are the only kit folders without a `hullproof` name. Leave them where they land: the kit manifest lists them, and the auditor reports `KIT: MISMATCH` if they are moved or deleted. The package README shows how to remove them together with their manifest lines. Give the project a `docs/security/STAGE.md` from `docs/hullproof/templates/STAGE.md`.

## Which tools, and how each one runs

Install with one command from the project root. Dry run first, which changes nothing, then add `--write`:

```bash
node tools/hullproof/install.mjs --tool cursor
node tools/hullproof/install.mjs --tool cursor --write
```

Replace `cursor` with the name in the Install column. `node tools/hullproof/install.mjs --list` shows every tool. The installer never overwrites a file of yours: plain files are skipped, text files get a marked block, and JSON files are merged with a backup. `tools/hullproof/INSTALL.md` has the details.

| Tool | Desktop app | CLI | VS Code | Install | Ways it runs | Enforcement |
|------|-------------|-----|---------|---------|--------------|-------------|
| Claude Code | Yes | Yes | Yes | `--tool claude-code` | agent, rules, prompt | partial |
| Codex | Yes | Yes | Yes | `--tool codex` | agent, rules, prompt | partial |
| Antigravity | Yes | Yes | Own IDE | `--tool antigravity` | agent, rules, prompt | partial |
| Gemini CLI | No | Yes | Yes, as advice | `--tool gemini-cli` | agent, rules, prompt | partial |
| Cursor | Yes | Yes | No | `--tool cursor` | agent, rules, prompt | partial |
| Windsurf and Devin | Yes | Yes | No | `--tool windsurf` | agent, rules, prompt | partial |
| GitHub Copilot | No | Yes | Yes | `--tool copilot` | agent, rules, prompt | partial |
| Lovable | Yes | No | No | `--tool lovable` | rules, prompt, install by chat | advisory |
| Replit | Yes | No | No | `--tool replit` | rules, prompt, install by chat | advisory |
| Bolt | Browser | No | No | `--tool bolt` | rules, prompt | advisory |
| Emergent | Browser | No | No | `--tool emergent` | rules, prompt | advisory |
| v0 | Browser | No | No | `--tool v0` | rules, prompt | advisory |
| ChatGPT | Yes | No | No | `--tool chatgpt` | rules, prompt | advisory |
| Claude.ai | Yes | No | No | `--tool claude-ai` | rules, prompt | advisory |
| Gemini app | Yes | No | No | `--tool gemini-app` | rules, prompt | advisory |

Browser means the tool runs in the browser only. For Antigravity, the IDE is Antigravity's own editor. Windsurf and Devin is one folder, because Windsurf is now Devin Desktop. Its JetBrains plugin reads the rules only.

The ways, in plain words:

1. **agent.** A skill, and in most tools an auditor agent, that runs the audit with the tool's own agent features.
2. **rules.** A rules or instructions file the tool reads in every session, with the hard rules, the refusal list and the area checklists.
3. **prompt.** One pasted prompt, `prompts/HULLPROOF-AUDIT-PROMPT.md` (full) or `prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md` (short, for tools with a small instruction box). It needs no helper agents and no hook: the model plays each role in order. It writes the report only.
4. **install by chat.** You upload the pack zip into the tool and it places the files. See below.

The enforcement label is copied from each tool's `TOOL.json`. The three words mean:

| Label | Meaning |
|-------|---------|
| enforced | The tool itself blocks the action, in the setup Hullproof ships. No tool carries this label in 0.3.1. |
| partial | The tool blocks some actions, under stated conditions such as a trusted folder or audit mode on, and some paths stay open. The tool page lists both. |
| advisory | Nothing blocks anything. The tool is asked to follow the rules and a person must review every change. |

## Audit mode

The hooks and the read only settings that Hullproof ships for Codex, Antigravity, Gemini CLI, Cursor, Windsurf and Copilot would block normal development if they were on all the time. So they work as a switch. Enforcement applies only while audit mode is on. When it is off, they allow every call that is well formed.

Turn it on before an audit and off after it:

```bash
mkdir -p docs/security && touch docs/security/.audit-mode
rm docs/security/.audit-mode
```

You can also set `HULLPROOF_AUDIT=1` in the environment the tool was started from. Only you turn audit mode on and off. The agent is told not to. Keep `docs/security/.audit-mode` out of your commits, so the switch is not left on by accident. If a tool seems to refuse every write, check whether the file is still there.

While audit mode is on, some tools cannot save the report file. They print the report in chat, and you save it under `docs/security/reports/`. The tool page says which.

Claude Code is the exception to the switch: its hook is attached only to the Hullproof skills and agents, so it holds only during those runs. A few deny rules stay on all the time, because they are safe all the time: reading secret files and editing the Hullproof hook files (Claude Code, the Cursor CLI and Devin).

Every enforcement setup needs the folder to be trusted first, because the tools hold project hooks back until you accept trust. Each tool page says how.

## Install by chat

For app builders and chat tools that have no terminal. Lovable and Replit list it as a way to run. In another tool that accepts a file upload you can try the same steps, and if it refuses, use the short prompt as described below.

1. Upload the Hullproof pack zip to the chat or project. It holds `docs/hullproof/`, `editors/` and `prompts/`.
2. Paste the full text of `prompts/INSTALL-BY-CHAT.md` into the same chat.
3. The tool unzips the pack, places the files at the project root without replacing any file of yours, and replies with two lists: what it placed with each full path, and what it could not place and why. Check the first list against your file tree. A tool can claim it placed a file that it did not.
4. Say: Run the Hullproof audit using prompts/HULLPROOF-AUDIT-PROMPT.md.

The tool may refuse. Hidden folders such as `docs/hullproof/.kit-manifest`, and write locations the tool protects, are the usual causes. Then skip the install, and paste `prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md` straight into the chat. It carries the rules with it, and it works with only the docs the tool can see. To put the rules in the tool by hand, follow the steps on the tool's page. Where the tool takes pasted text, the installer writes the file to paste under `hullproof-paste/<tool>/`.

## Limits and formats

Facts below were read from the vendor documentation on 2026-10-06. Vendors change these pages, so re check before relying on a number.

| Tool | Location, format and limit | Source |
|------|----------------------------|--------|
| Claude Code | Project rules in `CLAUDE.md` and `.claude/rules/*.md`. Anthropic advises keeping a `CLAUDE.md` file under 200 lines. | https://code.claude.com/docs/en/memory |
| Codex | `AGENTS.md` at the repository root, plain markdown. The combined chain of files is read up to `project_doc_max_bytes`, 32 KiB by default, and files after the limit are not added. | https://learn.chatgpt.com/docs/agent-configuration/agents-md |
| Antigravity | `.agents/rules/*.md` and `AGENTS.md`. A rule file is cut off after 24,000 bytes. | https://antigravity.google/docs/rules |
| Cursor | `.cursor/rules/*.mdc` with `description`, `globs` and `alwaysApply` frontmatter. Cursor advises keeping a rule under 500 lines. | https://cursor.com/docs/context/rules |
| Windsurf and Devin | `.devin/rules/*.md` (preferred) or `.windsurf/rules/*.md`, with `trigger` frontmatter. A workspace rule file is limited to 12,000 characters. | https://docs.windsurf.com/windsurf/cascade/memories |
| GitHub Copilot | `.github/copilot-instructions.md`. A skill `name` is limited to 64 characters and must match its folder, and a skill `description` to 1,024 characters. | https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills |
| Lovable | Project knowledge, a plain text field limited to 10,000 characters. A root `AGENTS.md` in the repository is also read. | https://docs.lovable.dev/features/knowledge.md |
| ChatGPT | Custom instructions are limited to 1,500 characters on Free and Go and 5,000 characters on the paid plans. | https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions |
| Claude.ai | A skill `description` is limited to 200 characters and a skill `name` to 64 characters. | https://support.claude.com/en/articles/12512198-how-to-create-custom-skills |
| Gemini app | A code import takes one folder or repository, up to 5,000 files and 100 MB, as a snapshot. | https://support.google.com/gemini/answer/14903178 |

The Hullproof files stay inside these numbers: the largest Windsurf rule file is about 6,400 characters, the Lovable knowledge text is about 4,000 characters, and the Codex, Antigravity and Gemini CLI rule files are about 16 KB each.

## Notes

1. Cursor and Windsurf may change rule discovery or activation between releases. The vendor pages above are the authority.
2. The Windsurf documentation is moving to Devin pages, so check the paths again before you rely on them.
3. How closely a model follows these files varies, so test the rules in your own setup. Ask the tool to summarize its active instructions and confirm it quotes the Hullproof hard rules.

## Which areas the rules cover

The area files cover authentication and authorization, APIs (including payments, webhooks and uploads), databases, AI features, and infrastructure and CI. The always on file carries the hard rules, the refusal list and the reporting format for every file. The Claude Code set has three more scoped files: payments, file storage and client code. In the other tools the payments and upload rules sit in the API area, and the client code rules (nothing secret in client code, public environment variable prefixes, untrusted HTML) are hard rules 3 and 4 in the always on file. Neither set is complete on its own: for a release, the standard and the release checklist decide.


## Keeping the files in step

The rule bodies are the same text in every tool, so a change to the hard rules, the refusal list or an area checklist should be made in all of them. The requirement IDs they cite exist in `docs/hullproof/` as of this release. If a requirement ID changes, search these files for the old ID.

Cursor's own rules page says AI guidance should not be your only security control. The same is true here.
