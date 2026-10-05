# AI and Agent Threat Model Extension

Add these sections to a [THREAT-MODEL.md](THREAT-MODEL.md) model whenever the feature calls a model, gives a model tools, retrieves documents, keeps agent memory, connects to an MCP server, or gives a coding agent access to secrets or deploy. It satisfies a Pro edition requirement in [GOVERNANCE.md](../GOVERNANCE.md) and a Pro edition requirement in [AI-SECURITY.md](../AI-SECURITY.md). It does not replace the main template: the new assets, actors and flows go into sections 1 to 7 as normal, and the threats found here go into the threat register as TM IDs.

Requirement IDs in this extension that have no entry in your `docs/hullproof` folder are Hullproof Pro requirements; cite them by ID as written.

**An instruction to the model is never a security boundary.** This is the governing principle of AI-SECURITY.md. A system prompt, tool description or label around untrusted content can be overridden by anything the model reads, so it never counts as an existing control. A rule that exists only as prompt text is recorded as a missing control under SEC-AI-015.

## Extra assets to list in section 1

| Asset | Check against |
|-------|---------------|
| System prompt and hidden context | SEC-AI-042 and a Pro edition requirement |
| Tool definitions and the credentials each tool runs under | SEC-AI-020 and a Pro edition requirement |
| Retrieved content and the documents behind it | SEC-AI-029, SEC-AI-031 and a Pro edition requirement |
| Vector store and embeddings | SEC-AI-034, SEC-AI-035 and Pro edition requirements |
| Conversation history and agent memory | SEC-AI-045 and a Pro edition requirement |
| Model provider account, keys and data settings | SEC-AI-041 and Pro edition requirements |
| Prompt and output logs | Pro edition requirements |
| AI spend budget | SEC-AI-002 and a Pro edition requirement |

## Extra actors to list in section 2

| Actor | Why it matters |
|-------|----------------|
| Malicious end user | Direct prompt injection, jailbreaks, cost abuse through the normal UI |
| Malicious document author | Writes content the model reads later (an uploaded file, email, web page, ticket, review) and plants instructions in it |
| Other tenant | Tries to reach another tenant's data through retrieval, memory or shared context |
| Compromised or malicious MCP server or third party tool | Returns poisoned tool results or changes its tool definitions after approval (a Pro edition requirement) |
| Model provider and model supply chain | Holds the data you send, and can change model behavior between versions (Pro edition requirements) |

Treat the model itself as a process that can act with an attacker's intent once it has read untrusted content, not as a trusted component.

## Diagram rules for section 5

Draw the model call as a process, every context source (system prompt, user input, retrieved documents, web pages, tool results, memory) as a data flow into it, each tool as a flow out of it labelled with the credential it runs under, and the provider as an external entity. Mark every context source an outsider can write to.

## AI threat families

Answer each question for this feature. Every credible threat becomes a TM entry in section 9.

| Family | Question to answer | Answer | Threat IDs | SEC-AI IDs to check |
|--------|--------------------|--------|------------|---------------------|
| Prompt injection | Which context sources can an outsider write to, and what is the worst instruction planted there could do? | | | 016, 018, 019, 050 |
| Tool misuse | Can any tool run with more authority than the requesting user, act on another user's data, or take a write, pay, send or delete action without confirmation? | | | 020, 021, 022, 023, 024, 039, 063, 065 |
| Data leakage | Can the model, retrieval, memory, logs or the provider expose data the current user may not see? | | | 029, 043, 044, 045, 046 |
| Cost abuse | What stops one user, or a script, from running up spend? | | | 002, 003, 004, 024 |
| Lethal combination | Does one feature read untrusted content, reach sensitive data and have a way to act or send data out? | | | 017 |
| Output handling and security decisions | Does model output reach SQL, a shell, code execution, HTML or a security decision without a code enforced check? | | | 015, 039, 040, 062 |

## Tool inventory

| Tool | Action type | Runs as (credential) | Authorization check location | Human confirmation | SEC IDs |
|------|-------------|----------------------|------------------------------|--------------------|---------|
| | Read, write, send, pay or delete | End user, never a service role | file:line | Yes or no, and why | |

## Lethal combination check

| Feature | Reads untrusted content | Reaches sensitive data | Can act or send out | Response |
|---------|-------------------------|------------------------|---------------------|----------|
| | Yes or no | Yes or no | Yes or no | If all three are yes: remove a leg, add confirmation per SEC-AI-017, or record an accepted risk in section 11 |

## Choosing responses

Prefer responses in this order: remove the capability, narrow it, add a code enforced check after the model, add human confirmation, then detection. Prompt wording is never a control for any threat. Runtime controls are defined in AI-SECURITY.md; coding agent controls are in [AGENTIC-DEV-SECURITY.md](../AGENTIC-DEV-SECURITY.md).
