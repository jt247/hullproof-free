# Hullproof for Bolt

Advisory only. Bolt reads agents.md once it is attached in chat. Nothing enforces the rules, so a person must review every change.

## What works

1. Attach agents.md in chat so Bolt uses it as project instructions.
2. Run the audit in Plan Mode with the short audit prompt.

## Steps in order

1. In the chat box, click the plus icon, then Attach file, and choose agents.md. Send: "Add this file to the project as agents.md and follow it in every task."
2. Open Code view and check agents.md is in the project. If it is not, create it there and paste the contents.
3. For an audit, click Plan in the chat box (it turns blue). Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md and send it. Click Plan again to go back to Build Mode.
4. If you prefer, paste the contents of agents.md into Project settings, Knowledge as well.

## The limit that matters

Bolt does not pick up agents.md on its own. It has to be attached in chat, and the chat box does not take ZIP files, so attach the files one at a time.

## What this does not do

Hullproof cannot stop Bolt from editing files in Build Mode, cannot run commands for you and cannot scan the live site. Plan Mode is Bolt's own mode and Hullproof adds no lock to it. Use Lock file in Code view to protect files you do not want touched. Bolt has its own project security audit in the Publish menu on paid plans.
