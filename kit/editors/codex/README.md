# Hullproof for Codex

Codex reads the Hullproof rules from `AGENTS.md`, runs the audit from a skill, and has a hook that enforces a read only limit while audit mode is on.

## Where it runs

| Route | How |
|-------|-----|
| Desktop app | Open the project folder. The app uses the same files as the CLI. |
| CLI | Run `codex` in the project folder. |
| VS Code | Install the Codex extension. It shares the CLI configuration, and it does not support plugins. |

## Install

Run this from the project root:

```
node tools/hullproof/install.mjs --tool codex --write
```

It adds `AGENTS.md` (the rules and area checklists), the skill in `.agents/skills/hullproof-audit/`, `.codex/hooks.json` (the hook), and `.codex/hullproof-audit.config.toml` (the audit profile, which stays inactive until you copy it). The hook script is `tools/hullproof/hooks/codex-adapter.mjs`, and it uses the Hullproof hook in `.claude/hooks/`. Install from a terminal. Codex can refuse to write into `.agents` or `.codex` when they already exist, so do not ask the agent to install it.

## Trust the folder first

Codex loads the files in `.codex/` only when the project is trusted. Trust the folder when Codex asks. Until you do, the hook is skipped.

The hook also needs your review. Start `codex` once in the folder, type `/hooks`, check the Hullproof hook and trust it. Codex skips a hook it has not been shown, and skips it again when the hook changes.

## Switch audit mode on and off

Audit mode is a switch. Turn it on only for the audit run.

1. On: create the marker file with `mkdir -p docs/security && touch docs/security/.audit-mode`, or start the tool from a terminal where `HULLPROOF_AUDIT=1` is set.
2. Off: delete the file with `rm docs/security/.audit-mode`, or unset `HULLPROOF_AUDIT`. The tool is then back to normal work.

Only you turn audit mode on and off. The agent is told not to.

## First run

Normal work needs nothing else. Codex edits files and runs commands as usual, and the hook blocks only the always on list below.

For an audit, turn audit mode on (steps above). Then copy `.codex/hullproof-audit.config.toml` to `$CODEX_HOME/hullproof-audit.config.toml` and start Codex with that profile:

```
codex --profile hullproof-audit 'Use $hullproof-audit to audit this project.'
```

The CLI reference describes `--profile NAME` as layering `$CODEX_HOME/NAME.config.toml` on top of your user config. The profile sets `sandbox_mode = "read-only"`. If you would rather not copy a file, the same limit is available on the command line:

```
codex exec --sandbox read-only 'Use $hullproof-audit to audit this project.'
```

In the app or the CLI, you can also type `$hullproof-audit`. The report comes back in the chat. Delete the copied profile file when you no longer need it.

## What is enforced

Always, in every session: the hook blocks shell commands that name a secret file (`.env` files other than the example files, `.pem`, `id_rsa`, `id_ed25519`) and blocks edits or shell writes that touch `tools/hullproof/hooks/`, `.claude/hooks/` and the hook config files. Input the hook cannot read as JSON is blocked.

While audit mode is on, in a trusted folder with the hook reviewed, the hook also blocks file edits and every shell command that is not on a short read only list, and the audit profile or `--sandbox read-only` blocks file writes and network access for commands. That is a partial limit and not a guarantee. A different sandbox setting in your user config or on the command line takes precedence over the profile. If the hook cannot start, for example when Node is missing, Codex goes on with the call. In a folder that is not trusted nothing in `.codex/` applies. The text in `AGENTS.md` is advice that a person must still check.

With audit mode off, nothing else is blocked.

## What it cannot do

It cannot stop web search or MCP tools, cannot stop a person who loosens the sandbox or turns audit mode off, and cannot make a folder trusted. Read only here still lets Codex run read only shell commands inside the sandbox. The always on check is a text match on the command, so a determined agent can get around it, and it is not a secret scanner.

## Limits

1. `AGENTS.md` is read up to 32 KiB for the whole chain of files. The Hullproof file is about 16 KB.
2. The subagents of Codex inherit the settings of the session that started them.
