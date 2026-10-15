# Hullproof for Replit

Advisory only. Agent reads replit.md on every request and a skill when its description matches. Nothing enforces either, so a person must review every change.

## What works

1. replit.md in the project root. Agent reads it on every request.
2. A project skill at .agents/skills/hullproof/SKILL.md (skills need a paid plan).
3. The short audit prompt, run in Plan mode.

## Steps in order

1. Open the file tree. If replit.md exists, add the Hullproof rules to the end. If not, create it at the root with the contents of replit.md from this folder. It must be in the root.
2. Turn on Show Hidden Files, create .agents/skills/hullproof/SKILL.md and paste the skill file contents.
3. To let Agent do steps 1 and 2, attach the kit files in chat and paste the text of prompts/INSTALL-BY-CHAT.md. If Agent declines to write them, create the two files by hand as above.
4. For an audit, turn on the Plan toggle at the bottom right of the chat box. Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md and send it. Replit also has its own Agent security scan in the Security Center if you want a second opinion.

## The limit that matters

Chat attachments are context, not an import, and a ZIP import creates a new project. So add the files by hand in the file tree, or ask Agent to write them from an attachment.

## What this does not do

Hullproof cannot stop Agent from editing files in Build mode, cannot run commands for you and cannot scan a deployed app. Plan mode is Replit's own mode and Hullproof adds no lock to it. Keep replit.md short, because Agent summarises a long one.

## Engine mode

Replit cannot run the Hullproof engine, so the audit here is prompt based. It checks only what the model can read in the chat or the project. Hullproof ships no MCP settings for this tool.

To use engine results anyway, run `hullproof ci` from the root of your repository on your own machine or in CI. It uses no model, and it writes `report.md` and three other files into `.hullproof/ci/`. Then paste `.hullproof/ci/report.md` into the chat before you run the audit, and say: "This is the output of the Hullproof engine. Treat each finding in it as correct unless the code you can see shows otherwise, then run the audit and add what the engine cannot see." The report lists failures that someone could exploit, so paste it only into a chat that you alone can read. The engine is in the `engine/` folder of your package, or at https://github.com/jt247/hullproof-engine.
