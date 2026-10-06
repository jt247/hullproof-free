# Hullproof for Windsurf and Devin

Windsurf is now Devin Desktop. It has two agents: Cascade, and Devin Local, which shares its engine with the Devin CLI. Hullproof ships files for both. It gives them the Hullproof hard rules, five area checklists, an audit skill, a read only auditor agent and hook files that block unsafe actions while an audit is running.

## Surfaces

| Surface | What it reads |
|---------|---------------|
| Devin Desktop, Cascade | `.devin/rules` (or `.windsurf/rules`), the skill, and the hooks in `.devin/hooks.json`. |
| Devin Desktop, Devin Local | Rules, skill, agent, `.devin/config.json` permissions and the hooks in `.devin/hooks.v1.json`. |
| Devin CLI (`devin`) | The same files as Devin Local. |
| JetBrains plugin | Rules in `.windsurf/rules`. It does not read the other files. |

## Install

Copy the kit into your project first, then run the installer from the project folder.

```bash
node tools/hullproof/install.mjs --tool windsurf
node tools/hullproof/install.mjs --tool windsurf --write
```

The first command is a dry run and changes nothing. The second writes the files. Your own files are kept: JSON files are merged and a backup is saved.

| Installed file | What it is |
|----------------|------------|
| `.devin/rules/hullproof*.md` | Hard rules (always on) and five area checklists (glob). Preferred location. |
| `.windsurf/rules/hullproof*.md` | The same six files for older Windsurf and the JetBrains plugin. If you only use Devin tools, delete this folder. |
| `.devin/skills/hullproof-audit/SKILL.md` | The audit skill. Points at `prompts/HULLPROOF-AUDIT-PROMPT.md`. |
| `.devin/agents/hullproof-auditor.md` | Auditor agent for Devin Local and the CLI, limited to the read, grep and glob tools. |
| `.devin/hooks.json` | Cascade hooks: `pre_read_code`, `pre_write_code`, `pre_run_command`, `pre_mcp_tool_use`. |
| `.devin/hooks.v1.json` | Devin Local and CLI hook: `PreToolUse`. |
| `.devin/config.json` | Permission deny rules for Devin Local and the CLI: secret files and the Hullproof hook files. |
| `.devin/hullproof-audit.config.json` | Strict audit profile that denies the edit tool, the exec tool and all MCP tools. Used only when you pass it with `--config`. |

All hook commands run `tools/hullproof/hooks/windsurf-adapter.mjs` followed by `|| exit 2`, so a crash or a missing adapter blocks the call. The adapter and the hook it calls in `.claude/hooks/` come with the kit copy. Do not delete them while the hook files are installed. The commands are written for macOS and Linux shells.

## First run

1. Open the folder in Devin Desktop and accept workspace trust.
2. Turn audit mode on: `mkdir -p docs/security && touch docs/security/.audit-mode`
3. Ask the agent to run the `hullproof-audit` skill.
4. When the audit ends, turn audit mode off: `rm docs/security/.audit-mode`

For a strict run from the terminal: `devin --config .devin/hullproof-audit.config.json -p "Run the hullproof-audit skill"`. Print mode cannot show the trust prompt, so open the folder once in the desktop app or in an interactive `devin` session and accept trust first. Do not pass `--respect-workspace-trust false` for an audit, because it removes that check.

## Audit mode

The hooks are a switch. While `docs/security/.audit-mode` exists, or `HULLPROOF_AUDIT=1` is set in the environment the agent was started from, the adapter enforces the read only limit. When neither is set, it allows every call, so your normal work is not blocked. Only you turn audit mode on and off. The agent is told not to.

## Trust note

Hooks do not load or run while a workspace is open in Restricted Mode, and agents are disabled there. Trust the folder first. Use `/hooks` in the Devin CLI to see which hook files loaded.

## What is enforced

Enforcement for Windsurf and Devin is partial. While audit mode is on and the workspace is trusted, the hooks block file writes, MCP calls, subagents, web fetches, tools they do not know and every shell command outside the Hullproof read only list, in Cascade through `.devin/hooks.json` and in Devin Local and the CLI through `.devin/hooks.v1.json`, and they block reads of secret files. Always on, `.devin/config.json` denies Devin Local and the CLI from reading secret files and from writing the Hullproof hook files. When audit mode is off, the hooks block nothing.

## What it cannot do

1. It does not block anything through the hooks when audit mode is off, and it does not stop a person from editing files.
2. The rules, the skill and the agent instructions are advice. The model can forget them or be talked out of them.
3. Cascade has no repository file for permissions, so in Cascade only the hooks enforce anything.
4. The JetBrains plugin reads the rules only. The hook files are not shipped for it.
5. Plugin hooks fail open in Devin, so Hullproof ships its hooks as repository files and not as a plugin.
6. While audit mode is on the agent cannot write the report file. It prints the report in chat and you save it under `docs/security/reports/`.

## Limits

A rule file is limited to 12,000 characters, and the largest Hullproof rule file is about 6,400. Rules use the `trigger` frontmatter: `always_on` for the hard rules and `glob` for the area files. Documentation: https://docs.windsurf.com/windsurf/cascade/memories, https://docs.windsurf.com/windsurf/cascade/hooks and https://docs.devin.ai/cli/extensibility/hooks/overview (read 2026-10-06). The Windsurf documentation is moving to Devin pages, so check the paths again before a release.
