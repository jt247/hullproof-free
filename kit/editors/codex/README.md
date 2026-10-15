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

## Engine mode

Engine mode runs the Hullproof engine first and starts the audit from its result. Codex can run shell commands, so it can use it.

1. Install the engine so the `hullproof` command runs in your shell: the `engine/` folder of your package, or the open engine at https://github.com/jt247/hullproof-engine, whose README says how. If the command is missing, the audit says so and continues in prompt mode.
2. From the project root, run `hullproof ci`. It uses no model and no container, and it writes `findings.json`, `report.md`, `results.sarif` and `pr-comment.md` into `.hullproof/ci/`. The same commit gives the same files. Exit code 0 means no blocking finding, 1 means the gate holds because a blocking finding exists, and 2 means an error.
3. Run the audit as described under First run. It follows `tools/hullproof/helpers/engine-mode.md`: it reads `.hullproof/ci/findings.json` and `.hullproof/ci/report.md`, treats every engine finding as ground truth, and adds its own judgment on top (business logic, whether access rules match what you meant, missing controls). It never drops or lowers an engine finding without evidence from the code, and it treats text inside the engine files as data, never as instructions.
4. Add `.hullproof/` to your `.gitignore`. The report lists failures that someone could exploit.

While audit mode is on, the Hullproof hook blocks shell commands outside a short read only list, and `hullproof ci` is not on it. So the audit cannot run the engine itself. Run `hullproof ci` before you turn audit mode on, in your own terminal or in a normal Codex session, then turn audit mode on and start the audit. The skill reads the files the engine left, and tells you when they are missing.

## MCP server

`hullproof mcp` starts a read only MCP server on your machine. Its tools are `list_requirements`, `get_requirement`, `get_checklist`, `get_gate_verdict`, `get_findings`, `get_report` and `explain_finding`. To also let Codex start scans, add `"--allow-run"` after `"mcp"` in the args list of the entry below. That adds `run_scan`, which writes only under `.hullproof/`.

Add the server with the installer, which also reports whether `hullproof` is on your PATH:

```bash
node tools/hullproof/install.mjs --tool codex --with-engine
node tools/hullproof/install.mjs --tool codex --with-engine --write
```

The first command is a dry run. The second writes `.codex/config.toml`:

```toml
[mcp_servers.hullproof]
command = "hullproof"
args = ["mcp"]
```

The installer never overwrites your own settings. A JSON file that already exists is merged, your keys are kept and a backup is saved as `.codex/config.toml.hullproof.bak`. If your file does not parse, or already holds a different `hullproof` entry, the installer leaves it alone and prints the entry for you to add by hand. Codex reads the project `.codex/config.toml` only in a trusted project. The installer adds the table inside a marked block (`# hullproof:begin` to `# hullproof:end`) at the end of the file and never edits the rest. If the file already defines `mcp_servers.hullproof` in some other way, the installer leaves it alone and prints the table for you to add by hand. If the tool cannot start the server, put the full path of the `hullproof` command in the file instead of the bare name.

## What is enforced

Always, in every session: the hook blocks shell commands that name a secret file (`.env` files other than the example files, `.pem`, `id_rsa`, `id_ed25519`) and blocks edits or shell writes that touch `tools/hullproof/hooks/`, `.claude/hooks/` and the hook config files. Input the hook cannot read as JSON is blocked.

While audit mode is on, in a trusted folder with the hook reviewed, the hook also blocks file edits and every shell command that is not on a short read only list, and the audit profile or `--sandbox read-only` blocks file writes and network access for commands. That is a partial limit and not a guarantee. A different sandbox setting in your user config or on the command line takes precedence over the profile. If the hook cannot start, for example when Node is missing, Codex goes on with the call. In a folder that is not trusted nothing in `.codex/` applies. The text in `AGENTS.md` is advice that a person must still check.

With audit mode off, nothing else is blocked.

## What it cannot do

It cannot stop web search or MCP tools, cannot stop a person who loosens the sandbox or turns audit mode off, and cannot make a folder trusted. Read only here still lets Codex run read only shell commands inside the sandbox. The always on check is a text match on the command, so a determined agent can get around it, and it is not a secret scanner.

## Limits

1. `AGENTS.md` is read up to 32 KiB for the whole chain of files. The Hullproof file is about 16 KB.
2. The subagents of Codex inherit the settings of the session that started them.
