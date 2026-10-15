# Install Hullproof for your tool

One command per tool. It needs Node 18 or newer and nothing else. Run it from your project folder.

```bash
node tools/hullproof/install.mjs --list
node tools/hullproof/install.mjs --tool cursor
node tools/hullproof/install.mjs --tool cursor --write
```

Replace `cursor` with your tool. The name or the display name works, in any letter case. If the name is not found, the installer suggests the closest ones. Add `--project <folder>` to install somewhere other than the current folder, and `--all` to install every tool.

## Dry run first

Without `--write` the installer changes nothing. It prints one line per file saying what it would do, then the trust note for the tool, whether the setup is enforced, partial or advisory and why, and the exact first thing to run.

| Line | Meaning |
|------|---------|
| create | The file does not exist yet and will be created. |
| append | Your file exists. A marked Hullproof block will be added at the end. |
| replace | Your file already has a Hullproof block. Only that block is replaced. |
| merge | Your JSON file exists. Hullproof settings will be merged into it. |
| skip | A different file is already there. It is left alone. |
| already installed | The file already matches. Nothing to do. |

Read the enforcement line before you rely on it. Enforced means the tool blocks the action. Partial means only some actions are blocked. Advisory means the rules guide the agent and nothing stops it.

## What happens with each kind of file

Plain files are never overwritten. If your file differs, the installer skips it and tells you.

Text files that you may already use, such as `AGENTS.md`, get a block between `<!-- hullproof:begin -->` and `<!-- hullproof:end -->`. Running the installer again replaces that block and never touches your text outside it.

JSON settings files are merged. Your keys stay, lists are combined without duplicates, and if both sides set the same value, yours is kept and the installer names the key. A copy of your file is saved first as `<file>.hullproof.bak`. If your file is not valid JSON, the installer refuses and changes nothing.

Some tools also need the read only hook script and a small adapter that sit outside the tool's own folder, in `.claude/hooks/` and `tools/hullproof/hooks/`. The installer copies those too, as plain files that are never overwritten. If a file with the same name but different content is already there, it is skipped and listed. If that file is your own copy of an older Hullproof hook, replace it with the one from the kit by hand, because the adapter calls it. In `TOOL.json` these files carry `"from": "kit"`, which means the source path starts at the kit root instead of the tool folder.

The installer only writes inside the project folder. It refuses paths that leave it and symbolic links that point outside it. If any file is refused, nothing is written for any file.

## Engine mode: --with-engine

Add `--with-engine` to also write the MCP settings that start the Hullproof engine (`hullproof mcp`) for the tool, in the file and format that tool uses. It also reports whether the `hullproof` command is on your PATH, and tells you to install the engine first when it is not. Without the flag nothing about the engine changes.

```bash
node tools/hullproof/install.mjs --tool claude-code --with-engine
node tools/hullproof/install.mjs --tool claude-code --with-engine --write
```

The MCP file follows the same rules as the other files. A JSON file that exists is merged and a backup is saved. A file that does not parse, or that already holds a different `hullproof` entry, is left alone and the entry is printed for you to add by hand. For Codex the settings are TOML, so the installer adds a marked block (`# hullproof:begin` to `# hullproof:end`) at the end of `.codex/config.toml`, replaces only that block on a rerun, and prints the table instead when the file already defines the server another way. A tool that cannot run the engine gets no MCP file, and the installer says that its audit is prompt based.

## Exit codes

0 means it worked or the dry run found changes to make. 1 means an error. 2 means there was nothing to do.


## Uninstall

Delete the files the dry run listed as create. For a marked block, delete the lines from `<!-- hullproof:begin -->` to `<!-- hullproof:end -->`. For a merged JSON file, restore `<file>.hullproof.bak`.
