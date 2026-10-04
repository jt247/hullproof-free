# Requirement Template

Every requirement uses exactly this structure. Do not add or drop fields without a CHANGELOG entry.

```markdown
### SEC-[DOMAIN]-[NUMBER]: [Requirement name]

| Field | Value |
|-------|-------|
| Severity | BLOCKER, CRITICAL, HIGH, MEDIUM or LOW |
| Stage | LAUNCH, GROWTH or SCALE: the earliest stage at which it applies |
| Applies To | System types from the list below, with a stack qualifier only when the requirement is stack specific |
| Automation | FULL, PARTIAL or MANUAL |
| Verification method | One or more values from the list below |
| Control type | AI-SECURITY.md only: one or more of Application security, AI specific, Agent specific, Model provider |

**Requirement.** One or two testable sentences using MUST, MUST NOT, SHOULD, or MAY.

**Why.** The attack, failure, or engineering risk this prevents.

**Implementation.** Practical guidance. Framework specific notes only where necessary, labelled with the stack.

**Verify.** Numbered, concrete steps a reviewer, test, or tool performs.

**Evidence.** What proves compliance: the artifact, test result, configuration, or record.

**Exceptions.** When the requirement does not apply, and what must be recorded if it is waived. BLOCKER requirements have no waiver.

**References.** Authoritative sources with their own control IDs and Hullproof source IDs, for example `OWASP ASVS 5.0.0 v5.0.0-8.2.1 [SRC-010]`.

**AI Agent Instruction.** What an AI coding agent must do, check, or refuse when this requirement applies.
```

## Allowed values

**Control type** (AI-SECURITY.md only): Application security (a control any web app needs, applied to the AI path), AI specific (exists because a model is in the loop), Agent specific (exists because the model can call tools or act), Model provider (depends on what the model provider offers or does with data). A requirement may list more than one. An instruction to the model is never a control on its own.

**Applies To:** SaaS, Web, API, Backend, Mobile, Database, Serverless, Cloud, AI features, Agentic workflow. Add a stack qualifier in brackets only for stack specific requirements, for example `Database (Supabase)`.

**Stage:** a requirement applies at its stage and every later stage. BLOCKER requirements are always LAUNCH.

| Stage | The project is at this stage when |
|-------|-----------------------------------|
| LAUNCH | Real users or real data are in the system, even in a private beta. |
| GROWTH | It takes payments, has a team with shared access, or holds data for business customers. |
| SCALE | It sells to enterprises, faces security questionnaires or audits, or operates under sector regulation. |

**Verification method:** AUTOMATED TEST, STATIC ANALYSIS, DEPENDENCY SCAN, SECRET SCAN, CONFIG REVIEW, CODE REVIEW, DOCUMENT REVIEW, MANUAL TEST, DYNAMIC TEST. DOCUMENT REVIEW covers runbooks, policies, and records such as a DPIA.

**Automation:**

| Value | Meaning |
|-------|---------|
| FULL | A tool or agent can verify it with no human judgment. |
| PARTIAL | A tool finds candidates and a human confirms. |
| MANUAL | Needs human review of design, configuration, or behavior. |

The edition (free or Pro) is shown by the document set a requirement ships in, not repeated in each requirement block.

## Writing rules

1. One requirement, one testable behavior. If it needs "and" to describe two controls, split it.
2. No filler. Every requirement traces to at least one authoritative reference, or is labelled `Hullproof original` with the closest indirect anchor.
3. Never copy text from a source. Write original statements.
4. Plain English. No em dashes, en dashes, or hyphens used as punctuation.
5. Never claim that meeting a requirement makes a system secure. Requirements reduce risk and make it verifiable.
