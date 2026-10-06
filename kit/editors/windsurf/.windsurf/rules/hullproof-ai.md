---
trigger: glob
globs: **/ai/**, **/llm/**, **/prompts/**, **/*prompt*.*, **/rag/**, **/embeddings/**, **/tools/**, **/agents/**, **/mcp/**
---
# Hullproof: AI features, prompts, retrieval and tools

Advisory text for Windsurf and Devin, not enforced. Read AI-SECURITY.md in docs/hullproof/ before editing these files. Start at the Coverage map and read only the requirement you need. The stage comes from docs/security/STAGE.md. Every BLOCKER applies from LAUNCH.

## Before you write code in this area

1. LAUNCH. Enforce security decisions in code, never by the model or the prompt (SEC-AI-015). Put no secrets in hidden context (SEC-AI-042).
2. LAUNCH. Run tools as the end user, never as a service role (SEC-AI-020), check authorization at every tool call (SEC-AI-021), and allow no outbound action without a user confirmation in a feature that reads untrusted input and sensitive data (SEC-AI-017).
3. LAUNCH. Retrieval: authorization inside the retrieval query (SEC-AI-029), row level security on embedding tables (SEC-AI-034), similarity search functions that run with the caller's rights (SEC-AI-035), and user contributed content kept out of shared sets until reviewed (SEC-AI-031).
4. LAUNCH. The model context holds only data the current user may see (SEC-AI-043). Conversation history and memory are isolated per user and tenant (SEC-AI-045).
5. LAUNCH. Treat model output as untrusted. Model generated code runs only in an isolated sandbox (SEC-AI-040), and model written SQL runs as a read only role under row level security (SEC-AI-062).
6. LAUNCH. Provider and vector store keys stay on the server (SEC-AI-041). Enforce a per user usage budget in the app (SEC-AI-002).
7. GROWTH adds. Rerun the AI security test set on every model, prompt or source change, make approval and policy checks fail closed, and delete chunks and embeddings on deletion.

## Refuse

- Using the system prompt as the access control.
- Letting retrieved text or user files change tool permissions or instructions.
- Passing model output to a database, shell, HTML renderer or another tool without validation.
- Giving a model tool a broader credential than the user holds.

If a control blocks you, stop and report it with the ASSUMPTION, VERIFIED or SUSPECTED labels and a severity from docs/hullproof/STANDARD.md.
