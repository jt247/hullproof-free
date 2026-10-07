# Hullproof for Claude Code

Claude Code is the home edition of Hullproof. The kit gives it rules, audit skills, auditor agents and a read only shell hook. Those files live in `.claude/` and are installed by the main kit copy, so this page covers what the installer adds on top: a project permissions deny file.

## Surfaces

| Surface | What it reads |
|---------|---------------|
| Claude Code desktop app (Code tab) | The same `.claude/` files and settings as the CLI. |
| Claude Code CLI | `.claude/` rules, skills, agents, hooks and `.claude/settings.json`. |
| Claude Code in VS Code | The same files. It shares user settings with the CLI. |
| Cloud sessions (claude.ai/code) | A fresh clone of the repository, so `.claude/` rules, skills, agents, hooks and permission rules in `.claude/settings.json` carry over. Files in `~/.claude/` do not. |

## Install

Copy the kit into your project first. That puts `.claude/rules`, `.claude/skills`, `.claude/agents` and `.claude/hooks` in place. Then add the deny rules.

```bash
node tools/hullproof/install.mjs --tool claude-code
node tools/hullproof/install.mjs --tool claude-code --write
```

The first command is a dry run and changes nothing. The second merges the deny rules into `.claude/settings.json`. If you already have that file, your keys are kept, the lists are combined and a backup is saved as `.claude/settings.json.hullproof.bak`.

| Installed file | What it is |
|----------------|------------|
| `.claude/settings.json` | `permissions.deny` rules, described below. |

The deny rules block these:

| Rule | What it stops |
|------|---------------|
| `Read(.env)`, `Read(.env.*)` with the example files carved out | Reading real environment files. `.env.example`, `.env.sample` and `.env.template` stay readable. |
| `Read(*.pem)`, `Read(id_rsa)`, `Read(id_ed25519)`, `Read(~/.ssh/**)`, `Read(~/.aws/**)` | Reading private keys and cloud credentials. |
| `Edit(/.claude/hooks/**)`, `Edit(/.claude/settings.json)`, `Edit(/tools/hullproof/hooks/**)` | Editing the Hullproof hook, the adapters and the settings file that holds these rules. |

To change one of these rules yourself, edit `.claude/settings.json` by hand.

## First run

In Claude Code, run `/hullproof-prelaunch`. The skill checks that the hook is active before it reads anything.
For a stricter read only run from the terminal, use the documented flags:

```bash
claude -p "Run a Hullproof audit of this project" --permission-mode dontAsk --tools "Read,Grep,Glob" --disallowedTools "mcp__*"
```

Always pass the permission mode yourself, because the mode a `-p` session starts in can differ between sessions.


## Trust note

Accept the workspace trust dialog in an interactive session, or the project hooks are held back. `claude -p` never shows that dialog and runs the hooks in a repository's settings and skills without it, so only run it on code you trust. It does not run the frontmatter hooks of a project subagent, so a subagent in `-p` has no hook at all. For a repository you did not write, start with `--setting-sources user`.

## What is enforced

Enforcement for Claude Code is partial. The deny rules in `.claude/settings.json` hold in every permission mode, and Claude Code does not hold deny rules back for the trust dialog. The read only hook in `.claude/hooks/hullproof-readonly-bash.mjs` is attached to the Hullproof skills and agents. It exits 2 on every problem, which blocks the call, and it blocks writes outside the report folder, shell commands outside a read only list and reads of secret files. Claude Code runs project hooks only after the trust dialog is accepted in an interactive session.

## What it cannot do

1. Rules, skill text and agent instructions are advice. Claude Code describes `CLAUDE.md` as context and not enforced configuration.
2. The hook covers the Hullproof skills. The Hullproof agents hold read only tools (Read, Grep and Glob) with no shell, so there is no shell in them to guard, and Claude Code runs their frontmatter hook only in an interactive session in a folder whose trust dialog you accepted. An agent started with another type has a full shell and no hook, and the skill tells it not to fall back to one.
3. A deny rule for one specific shell command is not a security boundary, so Hullproof ships none. Only a bare `Bash` deny stops shell use, and it would also stop your own work.
4. Plugins cannot carry permission rules or a `CLAUDE.md`, so this kit does not ship as a plugin.
5. The `dontAsk` mode is available only in the CLI. The desktop app does not offer it, and the VS Code extension ignores a project `defaultMode`.
6. `@file` references in a prompt do not call a tool, so a hook never sees them. The `Read` deny rules cover them.

## Limits

Anthropic advises keeping a `CLAUDE.md` under 200 lines. The Hullproof rules are small files in `.claude/rules/hullproof/`. Documentation: https://code.claude.com/docs/en/permissions, https://code.claude.com/docs/en/hooks and https://code.claude.com/docs/en/settings (read 2026-10-06).
