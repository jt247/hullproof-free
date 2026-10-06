# Hullproof for GitHub Copilot

Hullproof gives Copilot the Hullproof hard rules and area checklists as repository instructions, an audit skill, a read only auditor agent and hook files that block unsafe actions while an audit is running.

## Surfaces

| Surface | What it reads |
|---------|---------------|
| VS Code, Copilot chat | `.github/copilot-instructions.md`, the skill, the agent, and the hook files (Local agent). |
| Copilot CLI | The same instructions, skill and agent, and `.github/hooks/hullproof-cli.json`. |
| Copilot cloud agent and code review | Repository instructions. The cloud agent also reads the skill, the agent and the hook files. |

## Install

Copy the kit into your project first, then run the installer from the project folder.

```bash
node tools/hullproof/install.mjs --tool copilot
node tools/hullproof/install.mjs --tool copilot --write
```

The first command is a dry run and changes nothing. The second writes the files. If you already have `.github/copilot-instructions.md`, the Hullproof text is added as a marked block at the end and your text is left alone.

| Installed file | What it is |
|----------------|------------|
| `.github/copilot-instructions.md` | Hard rules, refusal list, reporting format and the five area checklists. |
| `.github/skills/hullproof-audit/SKILL.md` | The audit skill. Points at `prompts/HULLPROOF-AUDIT-PROMPT.md`. |
| `.github/agents/hullproof-auditor.agent.md` | Auditor agent limited to the `read` and `search` tools. |
| `.github/hooks/hullproof-cli.json` | `preToolUse` hook in the Copilot CLI and cloud agent format (`version` 1, `bash`). |
| `.github/hooks/hullproof-vscode.json` | `PreToolUse` hook in the VS Code Local format (`command`). |

Both hook files run `tools/hullproof/hooks/copilot-adapter.mjs`. The adapter and the hook it calls in `.claude/hooks/` come with the kit copy. Do not delete them while the hook files are installed. Hullproof does not ship a prompt file, because prompt files are deprecated for Copilot sessions on the Agent Host and the skill replaces them.

## First run

1. Open the folder in VS Code and trust it.
2. Turn audit mode on: `mkdir -p docs/security && touch docs/security/.audit-mode`
3. In Copilot chat, run `/hullproof-audit`. In the CLI, ask Copilot to use the `hullproof-audit` skill.
4. When the audit ends, turn audit mode off: `rm docs/security/.audit-mode`

To check the instructions loaded, ask Copilot to summarize the active instructions and confirm it quotes the Hullproof hard rules.

## Audit mode

The hook is a switch. While `docs/security/.audit-mode` exists, or `HULLPROOF_AUDIT=1` is set in the environment Copilot was started from, the adapter enforces the read only limit. When neither is set, it allows every call, so your normal work is not blocked. Only you turn audit mode on and off. The agent is told not to.

## Trust note

The VS Code Local agent runs hooks only when the setting `chat.useHooks` is on, which is the default, and the workspace is trusted. Trust the folder before you start an audit.

## What is enforced

Enforcement for Copilot is partial. While audit mode is on, the `preToolUse` hook denies file creation and edits, subagents, web fetches, PowerShell, any tool the adapter cannot name, and every bash command outside the Hullproof read only list, and it denies reads of secret files. In the CLI a crash or a non zero exit of the hook denies the call. When audit mode is off, nothing is blocked.

## What it cannot do

1. A hook that times out lets the call through in Copilot, and a user can turn hooks off with `disableAllHooks`. An administrator can set hooks as policy, and those cannot be turned off that way.
2. The names of the tools in the VS Code Local agent are not published, so the adapter denies a Local tool it cannot name. A Local audit can therefore be blocked more than you expect. Read the agent debug log to see the names.
3. Repository instructions, the skill and the auditor agent are advice. The agent limits its own tools, and a user can switch to another agent.
4. The hook does not block anything when audit mode is off, and it does not stop a person from editing files.
5. While audit mode is on the agent cannot write the report file. It prints the report in chat and you save it under `docs/security/reports/`.

## Limits

The vendor pages state no size limit for repository instructions, and the Hullproof file is about 16 KB. A skill `name` must match its folder and a `description` is limited to 1,024 characters. Copilot documentation: https://docs.github.com/en/copilot/reference/hooks-reference and https://code.visualstudio.com/docs/copilot/customization/hooks (read 2026-10-06).
