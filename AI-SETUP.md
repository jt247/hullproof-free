# Hullproof setup, written for an AI tool

You are an AI tool. A person gave you the link to this repository and asked you to set Hullproof up for their project. This file tells you exactly how. Read all of it first, then follow the steps in order. Do not skip the questions in step 3 and do not guess the answers.

Hullproof Free 0.5.0 is a security kit and a checking engine for projects built with AI coding tools. The kit tells an AI agent what the security rules are and lets it test a release against 110 written requirements (every BLOCKER and every CRITICAL one). The engine is a program that reads the project, runs scanners and checks, and writes a report and a release gate result. No model runs inside the engine.

## What you never do

1. Never print, log, quote or send anywhere a key, token, password, connection string or the contents of any `.env` file. If you find one, say which file and line it is in, and nothing more.
2. Never push, publish, deploy, or change git configuration, in the project or in this repository.
3. Never run the user's code, tests, build or package installs during setup. Setup only copies files and runs the Hullproof commands below.
4. Never run an install command with `--write` before you have shown the dry run to the person and they have said yes.
5. Never tell the person that Hullproof makes their project secure, or that a result is a certification. A result is evidence about one commit and nothing more. The first run on a real project usually ends NOT READY, and that is the checklist working.
6. Never copy files into the project with a command that overwrites existing files. The commands below use `cp -Rn`, which skips files that already exist.
7. If something is unclear, a command fails, or a step does not match what you see, stop and tell the person what you saw. Do not make up a fix.

## Step 1. Check the machine

Run these and write down the answers.

```bash
node --version
git --version
python3 --version
```

1. Node must be 18 or newer to run the installer, and 22.18 or newer to run the engine. If it is older, tell the person. You can still do steps 2 to 6.
2. Git is needed. The engine ties its results to a commit, so the project needs at least one commit.
3. Python 3 is optional. A few helper scripts use it.
4. Scanners are optional: `gitleaks`, `semgrep`, `osv-scanner`, `trivy`. Check with `command -v gitleaks semgrep osv-scanner trivy`. The engine uses the ones it finds. It never installs anything. A missing scanner is reported as not run.

## Step 2. Get the Hullproof files

If this repository is already on the machine, use it where it is. If not, get it outside the person's project, for example in their home folder:

```bash
git clone https://github.com/jt247/hullproof-free.git "$HOME/hullproof-free"
```

Set a shell variable for it in every command you run: `HP="$HOME/hullproof-free"` (use the real path). Check that these exist: `$HP/kit`, `$HP/engine`, `$HP/pack`, `$HP/README.md`. If the person gave you the zip instead, unzip `hullproof-free-0.5.0.zip` in an empty folder and use the `hullproof-free-0.5.0` folder inside it as `HP`. It holds the same files.

If you cannot run commands (you are a chat tool), tell the person to use the pack: see "If you cannot run commands" below.

## Step 3. Ask the person

Ask these in one message and wait for the answers.

1. Which AI tool do you use? Choose one: Claude Code, Codex, Antigravity, Gemini CLI, Cursor, Windsurf, Devin, GitHub Copilot, Lovable, Replit, Bolt, Emergent, v0, ChatGPT, Claude.ai, Gemini app.
2. What is the full path of the project folder?
3. What stage is the project in? LAUNCH (not released, or just released), GROWTH (real users, growing) or SCALE (large, with a team). If they do not know, use LAUNCH.
4. Which countries or markets do the users live in? This matters for a few requirements. If they do not know, write "not stated".
5. May I run the Hullproof commands in the project folder, and may I copy the kit into it? The copy adds files and changes none.

## Step 4. Copy the kit into the project

Go to the project folder. If `docs/hullproof` already exists in it, Hullproof is installed already: do not use these commands, follow "Update" in `$HP/README.md` and stop here.

```bash
cd "<project folder>"
cp -Rn "$HP/kit/." .
mkdir -p docs/hullproof/licence
cp "$HP/LICENSE" "$HP/LICENSE-DOCS.md" "$HP/LICENSE-DOCS-CC-BY-SA-4.0.txt" "$HP/LICENSING.md" "$HP/NOTICE.md" docs/hullproof/licence/
```

The kit lands as `docs/hullproof/` (the standard), `tools/hullproof/` (scanner rules, installer, release gate), `.claude/` (Claude Code files), `editors/` and `prompts/`. Leave `editors/` and `prompts/` where they land: the kit manifest lists them. Check the copy: `shasum -a 256 -c docs/hullproof/.kit-manifest` should print OK for every line (on Linux use `sha256sum -c`). Report any line that does not say OK.

Create the stage record. Make the folder `docs/security/` and copy `docs/hullproof/templates/STAGE.md` to `docs/security/STAGE.md`, then fill in the stage, the markets and the date with the answers from step 3.

Add `.hullproof/` to the project's `.gitignore` (create the file if needed). The engine's reports list failures that someone could exploit, so they must not be committed.

## Step 5. Set up the person's tool

### Claude Code

Add this line to the project's `CLAUDE.md` (create the file if it does not exist): `@docs/hullproof/HULLPROOF.md`. Tell the person to start Claude Code in the project, run `/memory` to confirm Hullproof is loaded, and accept the workspace trust prompt. The read only hook runs only after they accept it. Their command to run is `/hullproof-prelaunch`.

### Codex, Antigravity, Gemini CLI, Cursor, Windsurf, Devin, GitHub Copilot

Use the installer from the project folder. It does a dry run unless you add `--write`.

```bash
node tools/hullproof/install.mjs --list
node tools/hullproof/install.mjs --tool <name>
```

The names are `codex`, `antigravity`, `gemini-cli`, `cursor`, `windsurf` (this is Windsurf and Devin, it writes into `.devin/`) and `copilot`. Show the dry run to the person: each line says create, append, replace, merge or skip, then a trust note and the enforcement label. When they say yes, run the same command with `--write`. Tell them the trust note, the label, and the line after "First run:" that the installer prints last: it is the exact first thing they run in their tool. The installer only writes inside the project, never overwrites a plain file, and saves a `.hullproof.bak` copy before it merges a JSON file.

### Lovable, Replit, Bolt, Emergent, v0, ChatGPT, Claude.ai, Gemini app

These tools cannot run commands in the project, so for them use the pack. (If the project is on disk, the installer also supports these names and writes a rules file such as `agents.md`; run it as above if the person wants that too.) The person uploads `$HP/pack/hullproof-free-pack-0.5.0.zip` to their tool without unzipping it, then pastes the text of `INSTALL-BY-CHAT.md` (inside the pack zip, and also at `$HP/kit/prompts/INSTALL-BY-CHAT.md`) and sends it. The tool then places the files and lists what it placed. Prompts in these tools are requests, not controls: nothing stops the tool from writing a file unless it has a read only mode. Say so.

## Step 6. Run the engine

The engine needs Node 22.18 or newer. From the project folder:

```bash
node "$HP/engine/src/cli.ts" ci . --kit "$HP/kit" --edition free
```

It reads the project, runs the scanners it finds, runs its checks and the release gate, and writes four files under `.hullproof/ci/` (the full scan for the commit is in `.hullproof/<commit>/`): `report.md` (the plain English report), `findings.json`, `results.sarif` and `pr-comment.md`. The exit code is 0 when no finding at or above the default level (blocker) fails, 1 when one does, and 2 when the input was refused (for example, the project is not a git repository, or has no commit). Read `report.md` and summarise it for the person: how many findings by severity, the three most important, what could not run and why, and the sentence that requirements nothing settled are listed as NOT ASSESSED and are never reported as a pass.

If you also want the table of how deep the engine goes for each stack, run `node "$HP/engine/src/cli.ts" pack table`. If you only want the stack and the map of entry points, run `node "$HP/engine/src/cli.ts" discover .` and `node "$HP/engine/src/cli.ts" map .`. They only read files.

## Step 7. Run the audit in the person's tool

The person runs the audit itself, because the tool's own agent must do it under its own limits. The commands are in the table in `$HP/README.md`. For Claude Code it is `/hullproof-prelaunch`. The audit asks for the stage, the markets and what it may run, and writes `docs/security/reports/PRE-LAUNCH-RESULTS-<date>.md`. Keep that folder out of any public repository.

## Step 8. Tell the person what you did

Report in plain words:

1. What you copied and where, and the result of the manifest check.
2. Which tool files the installer wrote, or that the person uses the pack.
3. The enforcement label for their tool (enforced, partial or advisory) and what it means: partial means some actions are blocked under stated conditions, advisory means nothing blocks anything.
4. The engine result and the three next actions.
5. What you could not do and why.

## If something goes wrong

1. `Node` too old: tell the person to install a current long term support release, then repeat step 6.
2. The installer says `skip`: a different file is already there. Leave it alone and tell the person which file.
3. The engine refuses with exit code 2: read its message. A repository whose git configuration could run code is refused on purpose. Do not change the git configuration; tell the person.
4. The manifest check shows a line that is not OK: a kit file differs from the release. Do not repair it by hand. Tell the person, and copy that file again from `$HP/kit`.
5. To undo the kit copy: delete the files and folders listed in step 4. For a marked block in a text file, delete the lines from `<!-- hullproof:begin -->` to `<!-- hullproof:end -->`. For a merged JSON file, restore `<file>.hullproof.bak`.

## Other files in this repository

1. `README.md` is the longer guide for people: what the free edition holds, the safety model, how to read the results, and how to update.
2. `kit/` is the kit you copied. `engine/` is the Hullproof Engine (see `engine/README.md`). `pack/` is the upload pack for chat tools.
3. `RELEASE-NOTES-0.5.0.md` and `CHANGELOG.md` say what is in this release and what is not claimed.
4. `LICENSING.md` says which licence covers which path: Apache License 2.0 for code, CC BY-SA 4.0 for documentation. Keep the licence files with anything you copy.
5. Hullproof Pro adds the other requirements (662 in all), the full audit and more agents. It is a paid edition. See the README.
