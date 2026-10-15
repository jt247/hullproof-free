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

## Engine mode

Engine mode runs the Hullproof engine first and starts the audit from its result. Gemini CLI can run shell commands, so it can use it.

1. Install the engine so the `hullproof` command runs in your shell: the `engine/` folder of your package, or the open engine at https://github.com/jt247/hullproof-engine, whose README says how. If the command is missing, the audit says so and continues in prompt mode.
2. From the project root, run `hullproof ci`. It uses no model and no container, and it writes `findings.json`, `report.md`, `results.sarif` and `pr-comment.md` into `.hullproof/ci/`. The same commit gives the same files. Exit code 0 means no blocking finding, 1 means the gate holds because a blocking finding exists, and 2 means an error.
3. Run the audit as described under First run. It follows `tools/hullproof/helpers/engine-mode.md`: it reads `.hullproof/ci/findings.json` and `.hullproof/ci/report.md`, treats every engine finding as ground truth, and adds its own judgment on top (business logic, whether access rules match what you meant, missing controls). It never drops or lowers an engine finding without evidence from the code, and it treats text inside the engine files as data, never as instructions.
4. Add `.hullproof/` to your `.gitignore`. The report lists failures that someone could exploit.

While audit mode is on, the Hullproof hook blocks shell commands outside a short read only list, and `hullproof ci` is not on it. So the audit cannot run the engine itself. Run `hullproof ci` before you turn audit mode on, in your own terminal or in a normal Gemini CLI session, then turn audit mode on and start the audit. The skill reads the files the engine left, and tells you when they are missing.

## MCP server

`hullproof mcp` starts a read only MCP server on your machine. Its tools are `list_requirements`, `get_requirement`, `get_checklist`, `get_gate_verdict`, `get_findings`, `get_report` and `explain_finding`. To also let Gemini CLI start scans, add `"--allow-run"` after `"mcp"` in the args list of the entry below. That adds `run_scan`, which writes only under `.hullproof/`.

Add the server with the installer, which also reports whether `hullproof` is on your PATH:

```bash
node tools/hullproof/install.mjs --tool gemini-cli --with-engine
node tools/hullproof/install.mjs --tool gemini-cli --with-engine --write
```

The first command is a dry run. The second writes `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "hullproof": {
      "command": "hullproof",
      "args": ["mcp"]
    }
  }
}
```

The installer never overwrites your own settings. A JSON file that already exists is merged, your keys are kept and a backup is saved as `.gemini/settings.json.hullproof.bak`. If your file does not parse, or already holds a different `hullproof` entry, the installer leaves it alone and prints the entry for you to add by hand. The `mcpServers` entry is merged into your `.gemini/settings.json` next to the Hullproof hook settings. Gemini CLI does not connect MCP servers from an untrusted folder, so trust the folder first. If the tool cannot start the server, put the full path of the `hullproof` command in the file instead of the bare name.

## What is enforced

Always, in every session: the hook blocks shell commands that name a secret file (`.env` files other than the example files, `.pem`, `id_rsa`, `id_ed25519`) and blocks edits or shell writes that touch `tools/hullproof/hooks/`, `.claude/hooks/` and the hook config files. Input the hook cannot read as JSON is blocked.

While audit mode is on, in a trusted folder, the hook blocks `write_file`, `replace` and every shell command that is not on a short read only list, and plan mode blocks file edits. In an untrusted folder none of this applies. Gemini CLI continues the call when a hook exits with any code other than 2, for example when Node is missing. The text in `GEMINI.md` is advice that a person must still check.

With audit mode off, nothing else is blocked.

## What it cannot do

It cannot ship policy files, because Gemini CLI does not load policy files from a project folder. It cannot block reading files, and it cannot stop a person who changes the settings or turns audit mode off. The always on check is a text match on the command, so a determined agent can get around it, and it is not a secret scanner.

## Limits

1. Gemini CLI does not read `AGENTS.md` unless `context.fileName` lists it, so Hullproof ships `GEMINI.md`.
2. The page for `GEMINI.md` states no size limit, and the Hullproof file is about 16 KB.
