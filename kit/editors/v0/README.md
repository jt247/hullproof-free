# Hullproof for v0

Advisory only. v0 applies the text as an instruction you tick for a chat. Nothing enforces it, so a person must review every change.

## What works

1. A saved v0 Instruction holding the short rules.
2. The short audit prompt, run with the Plan Mode preset ticked.

## Steps in order

1. In the prompt bar, click the plus icon, then Instructions, then New Instruction. Set the title to Hullproof and paste the whole of INSTRUCTION.txt as the rule. Save it.
2. In each chat, click the plus icon and tick Hullproof. Tick Plan Mode too when you want an audit.
3. Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md and send it.
4. To run the full kit, connect the project to GitHub and use Claude Code or Codex on the repo. See editors/claude-code and editors/codex.

## The limit that matters

v0 does not read a rules file from your repo, so the instruction must be ticked in every chat where you want it.

## What this does not do

Hullproof cannot stop v0 from editing files, cannot lock a chat to read only and cannot scan a deployed app. Plan Mode is a prompt level preset, and Ask Permissions covers terminal and MCP tools only. Neither is a lock.
