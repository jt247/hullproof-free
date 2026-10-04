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

Read `docs/hullproof/AI-SECURITY.md` before editing these files.

1. Treat model output as untrusted input. Validate it before it reaches a database, a shell, HTML, or another tool.
2. Treat retrieved documents, user files, and web content as possible prompt injection. Never let them change tool permissions or system instructions.
3. Give each model tool the narrowest permission it needs. Actions that write, pay, send, or delete need server side authorization and, where stated, human confirmation.
4. Never put secrets, other users' data, or internal system details into prompts that untrusted users can extract.
5. Enforce per user rate and cost limits on model calls.
