# Hullproof for Claude.ai

Advisory only. Claude.ai has no hooks and no read only mode, so it can only be asked to follow the rules. A person must review every change.

## What works

1. A skill that Claude loads when the task is about security.
2. A Project holding the audit prompt, with short instructions.

## Steps in order

1. Skill route. Zip the hullproof folder so the folder itself is the root of the zip. In Claude.ai open Customize, then Skills, then the plus icon, then Create skill, then Upload a skill, and choose the zip. Skills need code execution and file creation turned on.
2. If the upload says the skill file is missing, rename skill.md to SKILL.md inside the folder, zip it again and upload.
3. Project route. Create a Project, click Set project instructions and paste PROJECT-INSTRUCTIONS.txt. Add prompts/HULLPROOF-AUDIT-PROMPT.md as a knowledge file.
4. Add the code to review: in the chat or project, click the plus icon, then Add from GitHub, and pick the folders. Claude reviews only what it can see.
5. Send: "Run the Hullproof audit on this project." Paste prompts/HULLPROOF-AUDIT-PROMPT-SHORT.md if Claude asks for the prompt.

## The limit that matters

Claude.ai does not document unpacking a ZIP of your code, so add code through GitHub or as individual files. The project plus its files must fit the context window.

## What this does not do

Hullproof cannot make Claude.ai read only, cannot stop it from writing code you did not ask for, and cannot check code it was never given.
