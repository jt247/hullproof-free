# Injection payload corpus for SEC-AI-050 and SEC-AI-016

Two different test inputs are needed, and no single corpus supplies both.

| Need | Requirement | Input | Source |
|------|-------------|-------|--------|
| Attack phrasing that a model may follow: instruction overrides, role play, encoded instructions, instructions hidden in a document | SEC-AI-050 (and SEC-AI-014 for agents) | A maintained, named corpus run through the real feature | NVIDIA garak probes, below |
| Text that closes the feature's own delimiter and starts a new instruction | SEC-AI-016 | The prompt template's own delimiters, which no outside corpus can know | `tests/fixtures/injection-delimiters.txt`, shipped in this kit |

## Decision: garak for the attack phrasing corpus

The named corpus is the probe set of garak (NVIDIA), repository `NVIDIA/garak`. Use the probe modules `promptinject` (instruction override and goal hijacking payloads), `latentinjection` (instructions placed inside a document the model is asked to process, which is the indirect injection case) and `encoding` (instructions hidden in encodings).

Basis, checked on 2026-10-04 against the repository's own metadata:

| Check | Result |
|-------|--------|
| License | Apache License 2.0. The GitHub repository metadata reports the SPDX id `Apache-2.0` and the `LICENSE` file at the root is the Apache 2.0 text. The license allows use and redistribution with notice. |
| Maintained | Not archived. The latest release found was v0.17.0 (published 2026-09-09) and the default branch had a push on 2026-10-02. |
| Probe modules exist | `garak/probes/promptinject.py`, `garak/probes/latentinjection.py` and `garak/probes/encoding.py` exist on the default branch. |
| Reaches an application | Its README lists generators for the major hosted models and a REST generator, so it can be pointed at a staging endpoint of the feature, not only at a bare model. |

Hullproof does not copy garak's payload text into the kit. The owner installs it and runs it, so the corpus stays current and its license notice stays with its source. A team that cannot run it keeps the evidence requirement of SEC-AI-050 by writing the same four kinds of case by hand, and records that the corpus was not a maintained one.

### How to run it (owner, in a terminal, against staging)

Never run it against production data or a production account: it sends many hostile prompts, and some probes try to make the model call tools.

```bash
python3 -m pip install garak
python3 -m garak --list_probes | grep -E 'promptinject|latentinjection|encoding'
# Check the option names of your installed version first: python3 -m garak --help
python3 -m garak --target_type rest --spec probes.promptinject      # configure the REST generator for the staging endpoint first
python3 -m garak --target_type rest --spec probes.latentinjection
```

Keep, in the evidence folder: the garak version, the exact command, the probe names, the number of attempts per probe, the run date, the commit of the feature, and the report file garak writes. Add the report file to the Evidence hashes table of the audit report. The number of runs and the pass threshold come from SEC-AI-050, not from this page.

Reading the result: a probe hit means the model followed an injected instruction at least once. For a feature with tools, also check the tool and outbound logs for the run window, because a hit that the text output hides can still have caused an action. The garak detector is a heuristic: read the hits, do not trust a zero as proof (SEC-AI-050 asks for repeated runs for this reason).

## Why not the others

| Candidate | License found | Why not the main choice |
|-----------|---------------|-------------------------|
| Azure/PyRIT | MIT | The repository is archived (the GitHub API reports archived, last push 2026-03-25). Not maintained. |
| promptfoo | MIT | Active, and usable for a team that already runs it. Its adversarial test plugins are configured per project, so there is no single fixed corpus to name. Acceptable evidence if the plugin list and version are recorded. |
| deepset/prompt-injections (Hugging Face dataset) | Apache 2.0 (dataset card) | A small static set, last modified 2024-07-30. Useful as a quick smoke test, not maintained. |

Licenses above were read from the repositories' own metadata on the date given. Read the license again before you copy any corpus text into your own repository.

## The delimiter breakout set

`tests/fixtures/injection-delimiters.txt` holds 30 cases written for this kit (no outside text). It covers closing tags in several spellings (exact, upper case, spaced, zero width character, fullwidth brackets, split by a newline), CDATA, code fence, triple quote and JSON string breaks, HTML comment end, chat template tokens, turn labels, template placeholders, tool result and message closers, hidden Unicode tag characters and a right to left override. Each case asks the model to output a canary string. File format and the two pass checks are in the header of the file.

1. Replace `{{OPEN}}`, `{{CLOSE}}` and the other placeholders with your prompt template's real delimiters, then decode each payload (it is a JSON string).
2. Assemble the request with the payload as the untrusted value, the way production code does. Check 1 needs no model: the payload must sit wholly inside the data block, which means your code escapes or removes the closing delimiter, or uses a delimiter the payload cannot contain (for example a per request random one). A template that wraps text in a fixed tag and does nothing else fails D01.
3. Check 2 sends the assembled request to the model in staging, the number of times SEC-AI-050 sets, and looks for the canary in the output and for any tool call or write.

A team that has no delimiter at all (it pastes the document into the prompt body) fails SEC-AI-016 without running anything.
