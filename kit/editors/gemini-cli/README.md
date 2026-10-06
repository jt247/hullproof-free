# Hullproof for Gemini CLI

Gemini CLI reads the Hullproof rules from `GEMINI.md`, runs the audit from a skill, and has a hook that enforces a read only limit while audit mode is on.

Google has said that unpaid tier and Google One users moved from Gemini CLI to Antigravity CLI on 18 June 2026. If that is you, use the Antigravity page instead.

## Where it runs

| Route | How |
|-------|-----|
| Desktop app | None. |
| CLI | Run `gemini` in the project folder. |
| VS Code | Gemini Code Assist agent mode reads `GEMINI.md`. Google documents only the settings file in your home folder for it, so the settings and hook in `.gemini/` should be treated as advice there. |

## Install

Run this from the project root:

```
node tools/hullproof/install.mjs --tool gemini-cli --write
```

It adds `GEMINI.md` (the rules and area checklists), the skill in `.gemini/skills/hullproof-audit/`, `.gemini/settings.json` (the hook), and `.gemini/hullproof-audit.settings.json` (strict settings that stay inactive). The hook script is `tools/hullproof/hooks/gemini-adapter.mjs`, and it uses the Hullproof hook in `.claude/hooks/`.

## Trust the folder first

Gemini CLI loads the project `.gemini/settings.json` only when the folder is trusted. Trust the folder when Gemini CLI asks. In an untrusted folder the settings and the hook are not loaded. Gemini CLI also warns the first time it sees a project hook or after the hook changes, so approve it when it asks.

## Switch audit mode on and off

Audit mode is a switch. Turn it on only for the audit run.

1. On: create the marker file with `mkdir -p docs/security && touch docs/security/.audit-mode`, or start the tool from a terminal where `HULLPROOF_AUDIT=1` is set.
2. Off: delete the file with `rm docs/security/.audit-mode`, or unset `HULLPROOF_AUDIT`. The tool is then back to normal work.

Only you turn audit mode on and off. The agent is told not to.

## First run

Normal work needs nothing else. Gemini CLI edits files and runs commands as usual, and the hook blocks only the always on list below.

For an audit, turn audit mode on (steps above) and start Gemini CLI in plan mode:

```
gemini --approval-mode=plan
```

Then ask: `Use the hullproof-audit skill to audit this project.` Gemini CLI asks you to confirm before it activates the skill.

Then check the guard once. Ask Gemini CLI to create a file called `hullproof-test.txt`. It should be refused. Plan mode is also available as a setting. To make it the default for this project, copy the `general` entry from `.gemini/hullproof-audit.settings.json` into `.gemini/settings.json`, and remove it again after the audit. The same file holds `tools.exclude` for the `write_file` and `replace` tools and `security.disableYoloMode`, which you can copy the same way.

## What is enforced

Always, in every session: the hook blocks shell commands that name a secret file (`.env` files other than the example files, `.pem`, `id_rsa`, `id_ed25519`) and blocks edits or shell writes that touch `tools/hullproof/hooks/`, `.claude/hooks/` and the hook config files. Input the hook cannot read as JSON is blocked.

While audit mode is on, in a trusted folder, the hook blocks `write_file`, `replace` and every shell command that is not on a short read only list, and plan mode blocks file edits. In an untrusted folder none of this applies. Gemini CLI continues the call when a hook exits with any code other than 2, for example when Node is missing. The text in `GEMINI.md` is advice that a person must still check.

With audit mode off, nothing else is blocked.

## What it cannot do

It cannot ship policy files, because Gemini CLI does not load policy files from a project folder. It cannot block reading files, and it cannot stop a person who changes the settings or turns audit mode off. The always on check is a text match on the command, so a determined agent can get around it, and it is not a secret scanner.

## Limits

1. Gemini CLI does not read `AGENTS.md` unless `context.fileName` lists it, so Hullproof ships `GEMINI.md`.
2. The page for `GEMINI.md` states no size limit, and the Hullproof file is about 16 KB.
