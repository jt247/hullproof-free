# Hullproof for Cursor

Hullproof gives Cursor the Hullproof hard rules, five area checklists, an audit skill, a read only auditor agent and hook files that block unsafe actions while an audit is running.

## Surfaces

| Surface | What it reads |
|---------|---------------|
| Cursor desktop app (editor and Agents Window) | Rules, the skill, the agent and the hooks. |
| Cursor CLI (`agent`) | The same rules system, plus `.cursor/cli.json` permissions. |
| Cloud agents | Rules, skills and agents from the repository. Project hooks also run there. |

## Install

Copy the kit into your project first, then run the installer from the project folder.

```bash
node tools/hullproof/install.mjs --tool cursor
node tools/hullproof/install.mjs --tool cursor --write
```

The first command is a dry run and changes nothing. The second writes the files. Your own files in `.cursor/` are kept: JSON files are merged and a backup is saved.

| Installed file | What it is |
|----------------|------------|
| `.cursor/rules/hullproof.mdc` | Hard rules, refusal list and reporting format. Always on. |
| `.cursor/rules/hullproof-auth.mdc`, `-api`, `-database`, `-ai`, `-infrastructure` | Area checklists, attached by file pattern. |
| `.cursor/skills/hullproof-audit/SKILL.md` | The audit skill. Points at `prompts/HULLPROOF-AUDIT-PROMPT.md`. |
| `.cursor/agents/hullproof-auditor.md` | Read only auditor agent (`readonly: true`). |
| `.cursor/hooks.json` | Runs `tools/hullproof/hooks/cursor-adapter.mjs` with `failClosed: true` on `preToolUse`, `beforeShellExecution` and `beforeReadFile`. |
| `.cursor/cli.json` | Permission deny rules for the CLI: secret files and the Hullproof hook files. |
| `.cursor/hullproof-audit/sandbox.json` | Read only sandbox profile. Not active until you copy it to `.cursor/sandbox.json`. |
| `.cursor/hullproof-audit/cli.json` | Strict CLI deny rules for an audit run. Not active until you copy it to `.cursor/cli.json`. |

The adapter in `tools/hullproof/hooks/` and the hook it calls in `.claude/hooks/` come with the kit copy. Do not delete them while `.cursor/hooks.json` is installed, because a missing adapter blocks every call.

## First run

1. Open the folder in Cursor and accept workspace trust.
2. Turn audit mode on: `mkdir -p docs/security && touch docs/security/.audit-mode`
3. In Cursor chat, run `/hullproof-audit`.
4. When the audit ends, turn audit mode off: `rm docs/security/.audit-mode`

To check the rules loaded, ask Cursor to summarize the active rules and confirm it quotes the Hullproof hard rules.

## Audit mode

The hook is a switch. While `docs/security/.audit-mode` exists, or `HULLPROOF_AUDIT=1` is set in the environment Cursor was started from, the hook enforces the read only limit. When neither is set, it allows every call, so your normal work is not blocked. Only you turn audit mode on and off. The agent is told not to.

## Trust note

Cursor does not run project hooks in a workspace that is not trusted. Open the folder, accept trust, then check the Hooks tab in Customize and the Hooks output channel to see that the three hooks loaded.

## What is enforced

Enforcement for Cursor is partial. While audit mode is on and the workspace is trusted, the hook blocks file writes, deletes, subagents, MCP calls, tools it does not know and every shell command outside the Hullproof read only list, and it blocks reads of secret files. Each hook has `failClosed: true`, so a crash or timeout of the hook blocks the call. Input that is not valid JSON is blocked in every mode. When audit mode is off, nothing is blocked.

## What it cannot do

1. It does not block anything when audit mode is off, and it does not stop a person from editing files.
2. The rules, the skill and the agent instructions are advice. The model can forget them or be talked out of them.
3. The hook is written for agent chat. For CLI runs, rely on `.cursor/cli.json`, and for a strict audit copy `.cursor/hullproof-audit/cli.json` over it and run `agent -p --mode=ask --sandbox enabled "..."`.
4. The sandbox profile covers terminal commands. It does not cover the agent's own file edit tool, so use it together with the hook.
5. Team and enterprise settings in Cursor override these local files.
6. While audit mode is on the agent cannot write the report file. It prints the report in chat and you save it under `docs/security/reports/`.

## Limits

Rule files must end in `.mdc`, and a plain `.md` file in `.cursor/rules/` is ignored. Cursor advises keeping a rule under 500 lines, and the largest Hullproof rule is about 70 lines. Cursor documentation: https://cursor.com/docs/context/rules and https://cursor.com/docs/hooks (read 2026-10-06).
