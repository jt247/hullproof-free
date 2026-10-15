# Hullproof for Emergent

Advisory only. Hullproof helps you review your own project. Nothing enforces the rules, so a person must review every change.

## What works

1. Paste PROJECT-INSTRUCTION.txt as your first message in a job, or attach it as a text file.
2. Review your own project in Plan mode with the short audit prompt.

## Steps in order

1. Start or open your job. Paste the whole of PROJECT-INSTRUCTION.txt as a message, or attach it with the attachment icon.
2. For a review of your own project, switch the composer to Plan (or press Option+P). Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md and send it. Approve nothing that edits files.
3. Start every new job the same way.

## The limit that matters

Emergent has no file or setting that carries instructions from one job to the next, so you paste the text again in each new job. Plan mode is not offered in Brainstorm or E3 sessions, so use a standard session.

## What this does not do

Hullproof cannot stop Emergent from editing files when you approve a plan, cannot run commands for you and cannot carry rules between jobs. Plan mode is Emergent's own mode and Hullproof adds no lock to it.

## Engine mode

Emergent cannot run the Hullproof engine, so the audit here is prompt based. It checks only what the model can read in the chat or the project. Hullproof ships no MCP settings for this tool.

To use engine results anyway, run `hullproof ci` from the root of your repository on your own machine or in CI. It uses no model, and it writes `report.md` and three other files into `.hullproof/ci/`. Then paste `.hullproof/ci/report.md` into the chat before you run the audit, and say: "This is the output of the Hullproof engine. Treat each finding in it as correct unless the code you can see shows otherwise, then run the audit and add what the engine cannot see." The report lists failures that someone could exploit, so paste it only into a chat that you alone can read. The engine is in the `engine/` folder of your package, or at https://github.com/jt247/hullproof-engine.
