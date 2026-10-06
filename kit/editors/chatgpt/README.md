# Hullproof for ChatGPT

Advisory only. ChatGPT has no hooks and no read only mode, so it can only be asked to follow the rules. A person must review every change.

## What works

A Project holding the rules and the audit prompt as files, with a short instruction pointing at them.

## Steps in order

1. Create a Project. Open Project settings and paste PROJECT-INSTRUCTIONS.txt into the instructions box.
2. Add these files to the Project: HULLPROOF-RULES.md and prompts/HULLPROOF-AUDIT-PROMPT.md (add the short version too if you have the room). Upload them as separate files, not a ZIP. A Project holds 5 files on Free, 25 on Go and Plus, and 40 on Pro, Business, Enterprise and Edu.
3. Add the code to review as files, or connect GitHub in Settings, Plugins. ChatGPT reviews only what it can see.
4. Send: "Read HULLPROOF-AUDIT-PROMPT.md and run it."

The short rules fit the Custom Instructions box on Free and Go (1,500 characters) if you want them in every chat.

## The limit that matters

ChatGPT does not document a way to unpack a ZIP, so the files go in flat. Hullproof ships no ChatGPT skill because the skill file layout is not documented.

## What this does not do

Hullproof cannot make ChatGPT read only, cannot stop it from writing code you did not ask for, and cannot check code it was never given.
