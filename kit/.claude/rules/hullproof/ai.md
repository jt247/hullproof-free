---
paths:
  - "**/ai/**"
  - "**/llm/**"
  - "**/prompts/**"
  - "**/*prompt*.*"
  - "**/rag/**"
  - "**/embeddings/**"
  - "**/tools/**"
---
# AI feature rules

Before editing these files, open the Coverage map in `docs/hullproof/AI-SECURITY.md`, find the rows for your change, then read only those requirement blocks (list them with `grep -n '^### SEC-' docs/hullproof/AI-SECURITY.md`, then Read with an offset). Do not load a whole document.

1. Treat model output as untrusted input. Validate it before it reaches a database, a shell, HTML, or another tool (SEC-API-021 and a Pro edition requirement).
2. Treat retrieved documents, user files, and web content as possible prompt injection. Never let them change tool permissions or system instructions.
3. Run each model tool as the end user with the narrowest permission it needs, never as a service role (SEC-AI-020, SEC-AI-021). Actions that write, pay, send, or delete need server side authorization and, where stated, human confirmation (SEC-AI-017).
4. Never put secrets, other users' data, or internal system details into prompts that untrusted users can extract (SEC-AI-042, SEC-AI-043).
5. Enforce per user rate and cost limits on model calls (SEC-AI-002).
