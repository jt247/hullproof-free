# Hullproof for Antigravity

Antigravity reads the Hullproof rules from `.agents/rules/`, runs the audit from a skill, and has a hook that enforces a read only limit while audit mode is on.

## Where it runs

| Route | How |
|-------|-----|
| Desktop app | Open the project folder in Antigravity 2.0. |
| CLI | Run `agy` in the project folder. |
| IDE | Open the project folder in the Antigravity IDE. It reads the same `.agents/` files. |

## Install

Run this from the project root:

```
node tools/hullproof/install.mjs --tool antigravity --write
```

It adds `.agents/rules/hullproof.md` (the rules and area checklists, always on), the skill in `.agents/skills/hullproof-audit/`, and `.agents/hooks.json`. The hook script is `tools/hullproof/hooks/antigravity-adapter.mjs`, and it uses the Hullproof hook in `.claude/hooks/`.

## Trust the folder first

Open the project folder as your workspace and choose trust if Antigravity asks. The hook only runs for the workspace that holds `.agents/hooks.json`.

## Switch audit mode on and off

Audit mode is a switch. Turn it on only for the audit run.

1. On: create the marker file with `mkdir -p docs/security && touch docs/security/.audit-mode`, or start the tool from a terminal where `HULLPROOF_AUDIT=1` is set.
2. Off: delete the file with `rm docs/security/.audit-mode`, or unset `HULLPROOF_AUDIT`. The tool is then back to normal work.

Only you turn audit mode on and off. The agent is told not to.

## First run

Normal work needs nothing else. Antigravity edits files and runs commands as usual, and the hook blocks only the always on list below.

For an audit, turn audit mode on (steps above). In the app or the IDE, type `/hullproof-audit`. From the command line:

```
agy -p "Use the hullproof-audit skill to audit this project."
```

Then check the guard once. Ask the agent to create a file called `hullproof-test.txt`. While audit mode is on, the hook should refuse. If the file appears, turn the run off and do not rely on the hook.

A headless run that is refused a tool carries on and exits with code 0, so read the output and not the exit code.

## Engine mode

Engine mode runs the Hullproof engine first and starts the audit from its result. Antigravity can run shell commands, so it can use it.

1. Install the engine so the `hullproof` command runs in your shell: the `engine/` folder of your package, or the open engine at https://github.com/jt247/hullproof-engine, whose README says how. If the command is missing, the audit says so and continues in prompt mode.
2. From the project root, run `hullproof ci`. It uses no model and no container, and it writes `findings.json`, `report.md`, `results.sarif` and `pr-comment.md` into `.hullproof/ci/`. The same commit gives the same files. Exit code 0 means no blocking finding, 1 means the gate holds because a blocking finding exists, and 2 means an error.
3. Run the audit as described under First run. It follows `tools/hullproof/helpers/engine-mode.md`: it reads `.hullproof/ci/findings.json` and `.hullproof/ci/report.md`, treats every engine finding as ground truth, and adds its own judgment on top (business logic, whether access rules match what you meant, missing controls). It never drops or lowers an engine finding without evidence from the code, and it treats text inside the engine files as data, never as instructions.
4. Add `.hullproof/` to your `.gitignore`. The report lists failures that someone could exploit.

While audit mode is on, the Hullproof hook blocks shell commands outside a short read only list, and `hullproof ci` is not on it. So the audit cannot run the engine itself. Run `hullproof ci` before you turn audit mode on, in your own terminal or in a normal Antigravity session, then turn audit mode on and start the audit. The skill reads the files the engine left, and tells you when they are missing.

## MCP server

`hullproof mcp` starts a read only MCP server on your machine. Its tools are `list_requirements`, `get_requirement`, `get_checklist`, `get_gate_verdict`, `get_findings`, `get_report` and `explain_finding`. To also let Antigravity start scans, add `"--allow-run"` after `"mcp"` in the args list of the entry below. That adds `run_scan`, which writes only under `.hullproof/`.

Add the server with the installer, which also reports whether `hullproof` is on your PATH:

```bash
node tools/hullproof/install.mjs --tool antigravity --with-engine
node tools/hullproof/install.mjs --tool antigravity --with-engine --write
```

The first command is a dry run. The second writes `.agents/mcp_config.json`:

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

The installer never overwrites your own settings. A JSON file that already exists is merged, your keys are kept and a backup is saved as `.agents/mcp_config.json.hullproof.bak`. If your file does not parse, or already holds a different `hullproof` entry, the installer leaves it alone and prints the entry for you to add by hand. The Antigravity app, IDE and CLI all read `.agents/mcp_config.json` in the workspace. Antigravity asks before it calls an MCP tool unless you set a permission rule. If the tool cannot start the server, put the full path of the `hullproof` command in the file instead of the bare name.

## What is enforced

Always, in every session: the hook blocks shell commands that name a secret file (`.env` files other than the example files, `.pem`, `id_rsa`, `id_ed25519`) and blocks edits or shell writes that touch `tools/hullproof/hooks/`, `.claude/hooks/` and the hook config files. Input the hook cannot read as JSON is blocked.

While audit mode is on, the hook also denies the file write tools and every shell command that is not on a short read only list. Reading files is not checked. Antigravity does not describe what happens when a hook fails to run, so the check above is the way to know it works on your machine. Permission rules are a setting of the app and cannot be shipped in a file, so none are included. The text in `.agents/rules/hullproof.md` is advice that a person must still check.

With audit mode off, nothing else is blocked.

## What it cannot do

It cannot block reading files, cannot set Antigravity permission rules, and cannot stop a person who turns the hook or audit mode off. The always on check is a text match on the command, so a determined agent can get around it, and it is not a secret scanner.

## Limits

1. A rule file is cut off after 24,000 bytes. The Hullproof file is about 16 KB.
2. Workflows are being replaced by skills, so Hullproof ships a skill and no workflow.
