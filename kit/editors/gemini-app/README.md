# Hullproof for the Gemini app

Advisory only. The Gemini app has no hooks and no read only mode, so it can only be asked to follow the rules. A person must review every change.

## What works

1. A Gem holding INSTRUCTIONS.txt, until Google converts Gems to skills (November 2026 for personal accounts).
2. A skill folder, for after that change.

## Steps in order

1. Gem route. Open Gems, then New Gem. Name it Hullproof and paste INSTRUCTIONS.txt as the instructions.
2. Skill route. Open Settings, then Skills, then Upload, and choose the skills/hullproof folder, or a zip of it with SKILL.md in the main folder. Keep the folder name hullproof.
3. Add the code to review: on the web, choose Add files, then Import code, and upload a folder or paste a repo URL. Gemini takes up to 5,000 files and 100 MB, as a snapshot.
4. Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md and send it. Use the short prompt, because an account without an AI plan has a small context window.

## The limit that matters

The code import is a snapshot that Gemini can read but cannot write to. That is Google's limit, not a Hullproof control. The chat can still suggest edits that you apply yourself.

## What this does not do

Hullproof cannot make Gemini read only, cannot stop it from writing code you did not ask for, and cannot check code it was never given. Your instructions for Gemini in Personal context do not apply inside a Gem.

## Engine mode

The Gemini app cannot run the Hullproof engine, so the audit here is prompt based. It checks only what the model can read in the chat or the project. Hullproof ships no MCP settings for this tool.

To use engine results anyway, run `hullproof ci` from the root of your repository on your own machine or in CI. It uses no model, and it writes `report.md` and three other files into `.hullproof/ci/`. Then paste `.hullproof/ci/report.md` into the chat before you run the audit, and say: "This is the output of the Hullproof engine. Treat each finding in it as correct unless the code you can see shows otherwise, then run the audit and add what the engine cannot see." The report lists failures that someone could exploit, so paste it only into a chat that you alone can read. The engine is in the `engine/` folder of your package, or at https://github.com/jt247/hullproof-engine.
