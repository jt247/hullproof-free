# Hullproof for Lovable

Advisory only. Lovable reads the rules and tries to follow them. Nothing enforces them and there is no locked read only mode, so a person must review every change.

## What works

1. Paste the rules into Project knowledge. This always works and the text is always in Lovable's context.
2. Add the rules as a root AGENTS.md. Lovable reads it every session. Lovable cannot import an existing repo, so the file gets there by upload and the install prompt, not by pointing Lovable at a repo.
3. Run the audit in Plan mode with the short audit prompt.

## Steps in order

1. Open your project, then Project settings, then Knowledge. Paste the whole of KNOWLEDGE.txt (under 10,000 characters) and save.
2. Attach the Hullproof kit zip (or just AGENTS.md and the prompts folder) to the chat and paste the text of prompts/INSTALL-BY-CHAT.md. Lovable should write AGENTS.md at the project root.
3. If Lovable refuses or does not write the files, skip step 2. Step 1 already carries the rules. Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md straight into the chat when you want an audit.
4. For an audit, switch to Plan mode (the mode picker next to the chat box, or Option+P on Mac and Alt+P on Windows). Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md and send it.

To run the full kit with enforced controls, link the project to GitHub, clone the repo Lovable creates, and use Codex or Claude Code on it. See editors/codex and editors/claude-code.

## The limit that matters

Lovable creates its own private repo when you link GitHub and cannot import one you already have. So the kit goes in by upload and chat, never by repo import.

## What this does not do

Hullproof cannot stop Lovable from editing code in Build mode, cannot run commands for you and cannot scan the live site. Plan mode is Lovable's own mode and Hullproof adds no lock to it. Connector actions can still run in Chat mode with your approval. A long chat can dilute the rules, so start a fresh chat for an audit.
