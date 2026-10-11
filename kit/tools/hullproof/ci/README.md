# Hullproof CI tools

Small Node scripts for the owner and for CI. They use Node built ins only (Node 22 is the target), make no network calls, and never run or import anything they read from an input file.

Agents never run these tools. The audit skill and its agents only read the repository and write text. You run the tools, or your CI does, from the project root.

## What is here

| File | What it does |
|------|--------------|
| `hullproof-gate.mjs` | Reads the controls file and a results table and exits 1 when any BLOCKER or CRITICAL item in scope is FAIL or NOT ASSESSED. With the two record flags it also validates the findings record and the surface ledger and cross checks them. It prints counts only. |
| `validate-findings.mjs` | Checks the structure and self consistency of a `<report>.findings.md` file. |
| `validate-surface-ledger.mjs` | Checks a `<report>.surface-ledger.md` file, and with `--findings` checks it against the findings record. |
| `hullproof-records-common.mjs` | Shared reading, parsing and message code for the three tools above. |

The JSON Schema files `docs/hullproof/findings.schema.json` and `docs/hullproof/surface-ledger.schema.json` are written by the validators themselves.

## Run commands

Run each command from the project root. `<REPORT>` is the report name, `SECURITY-AUDIT-REPORT` by default.

```bash
node tools/hullproof/ci/validate-findings.mjs docs/security/reports/<REPORT>.findings.md --controls docs/hullproof/security-controls.json
node tools/hullproof/ci/validate-surface-ledger.mjs docs/security/reports/<REPORT>.surface-ledger.md --findings docs/security/reports/<REPORT>.findings.md
node tools/hullproof/ci/hullproof-gate.mjs --controls docs/hullproof/security-controls.json --results docs/security/reports/<REPORT>.md --findings docs/security/reports/<REPORT>.findings.md --surface docs/security/reports/<REPORT>.surface-ledger.md
```

Without `--controls`, the findings validator skips the severity rules and prints one notice line saying so. The structure rules still run.

The gate on its own, with no record files:

```bash
node tools/hullproof/ci/hullproof-gate.mjs --controls docs/hullproof/security-controls.json --results docs/security/reports/PRE-LAUNCH-RESULTS-<date>.md [--scope prelaunch|all]
```

To print a schema:

```bash
node tools/hullproof/ci/validate-findings.mjs --print-schema
node tools/hullproof/ci/validate-surface-ledger.mjs --print-schema
```

## Exit codes

| Code | Validators | Gate |
|------|------------|------|
| 0 | No errors. Warnings do not change the code. | Checklist items settled and the run can support READY. This is not a READY verdict. |
| 1 | Errors found in the file. | Open BLOCKER or CRITICAL items, or a run that cannot support READY. |
| 2 | Usage error, or the input file or controls file could not be found or opened. | Usage error, a record file with errors, an input problem, or a cross check failure. |

A run cannot support READY when its run status is incomplete, when it used the quick profile, when its scope is partial, or (when `--surface` is given) when at least one unit is deferred. The gate then prints `RESULT: run cannot support READY (<reason>)` and exits 1 even if every checklist item is settled. Without `--surface` the gate cannot see deferred units, and the findings counts line says the surface ledger was not supplied.

For a quick or partial run the gate prints one `scope:` line that says how many gated requirements lie outside the run's scope and have no row. It does not list them. The run still ends `RESULT: NOT READY` with the same note and exit code.

Exit code 0 from the gate is never a READY verdict. Gate conditions G-1, G-2, G-6, G-7 and G-8 stay with the person reading the report.

## What the output looks like

The validators print a counts line, then numbered messages. Each message holds a tier letter (E for an error, W for a warning), a rule id, a place and a fixed sentence. For example:

```
hullproof findings: records 6 (fail 3, routed 1, refuted 1, observation 1), errors 1, warnings 0
1. E F10 record 3 (finding) boundary is required for class finding
```

The place names the record by its position in the file, with its kind or class in brackets, and then the field path. Messages never repeat a title, note, reason or any other text from a record. At most 100 errors and 100 warnings are printed. After that the tool prints how many more there were.

The gate prints counts only. It never prints evidence, notes or record text.

## How input is treated

Every input file is treated as hostile, because audit files can be edited by anyone with access to the repository.

1. A file is read only when it is a regular file. Links, pipes, devices and folders are refused. The file is opened without following a link.
2. The size is checked before anything is read. The validators accept at most 1,048,576 bytes. The gate accepts at most 16,777,216 bytes for each file it reads, because the controls file is large.
3. The text must be valid UTF 8. One leading byte order mark is allowed. Windows line endings are allowed.
4. The tools look for exactly one fenced block with the right tag, and the block must be closed. Fences with other tags are ignored.
5. The block is scanned once, before parsing, for nesting depth. More than 32 levels is an error, so a deeply nested file cannot overflow the JSON parser.
6. When the JSON is bad, the tool prints only the position of the problem. It never prints the parser message, because that message can quote the input.
7. Every text value must hold visible text and must not hold control characters, bidirectional controls, zero width or other format characters, tag characters or lone surrogates. Paths must be repository relative with no leading slash, no `..` segment, no backslash, no colon and no `~`.
8. Anything printed about an input is escaped for a terminal and cut to a short length.

Unknown keys are errors at every depth, so a file cannot carry hidden extra fields.

## Limits

The validators check structure and self consistency only. They cannot show that a file was read, that a trace is true, or that the attack surface was fully derived. A clean run means the records are well formed and agree with each other and with the report table.
