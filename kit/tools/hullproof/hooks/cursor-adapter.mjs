#!/usr/bin/env node
// Hullproof Cursor hook adapter. Translates Cursor hook input into the input of .claude/hooks/hullproof-readonly-bash.mjs
// (profile skill), runs that hook, and answers in the Cursor format.
// Attached in .cursor/hooks.json to preToolUse, beforeShellExecution and beforeReadFile, each with failClosed true.
// Cursor input on stdin: preToolUse { hook_event_name, tool_name, tool_input }, beforeShellExecution { command }, beforeReadFile { file_path, content }.
// Cursor answer on stdout: { permission: "allow" | "deny", user_message, agent_message }. A deny also exits 2 with the reason on stderr.
// Audit mode: the adapter enforces only while docs/security/.audit-mode exists in the project root, or HULLPROOF_AUDIT=1 is set.
// Outside audit mode it allows every well formed call, so normal work is not blocked. Input that is not JSON is denied in every mode.
// In audit mode only these are allowed: shell commands and Grep or Glob calls the hook accepts, and reads of files the hook accepts.
// Writes, deletes, subagents, MCP calls and every tool not named here are denied.
// Zero dependencies. Installed at tools/hullproof/hooks/cursor-adapter.mjs, with the Claude Code hook at .claude/hooks/ in the same project root.
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const HOOK = join(ROOT, '.claude', 'hooks', 'hullproof-readonly-bash.mjs');
const MARKER = join(ROOT, 'docs', 'security', '.audit-mode');
const PROFILE = 'skill';
const MAX_INPUT = 64_000_000; // beforeReadFile carries the file content
const END = 'Only the owner turns audit mode off, by deleting docs/security/.audit-mode.';

const isStr = (v) => typeof v === 'string' && v.length > 0;
const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

function viaHook(call) {
  if (!existsSync(HOOK)) return 'the Hullproof read only hook is missing from .claude/hooks';
  const r = spawnSync(process.execPath, ['--', HOOK, PROFILE], {
    input: JSON.stringify(call), encoding: 'utf8', timeout: 15000, maxBuffer: 1_000_000,
    env: { ...process.env, CLAUDE_PROJECT_DIR: ROOT },
  });
  if (r.error) return `the read only hook could not run (${r.error.message})`;
  if (r.status === 0) return null;
  return (r.stderr || '').trim().replace(/^Hullproof read only hook blocked this call: /, '').replace(/\.+$/, '') || 'the read only hook refused this call';
}

const shell = (command) => (isStr(command) ? viaHook({ tool_name: 'Bash', tool_input: { command } }) : 'could not read the command');
const read = (file_path) => (isStr(file_path) ? viaHook({ tool_name: 'Read', tool_input: { file_path } }) : 'could not read the file path');
const search = (tool, input) => (isObj(input) ? viaHook({ tool_name: tool, tool_input: input }) : `could not read the ${tool} input`);

// Returns null to allow, or a reason text to deny. Only called in audit mode.
function decide(p) {
  const ev = p.hook_event_name;
  if (ev === 'beforeShellExecution') return shell(p.command);
  if (ev === 'beforeReadFile') return read(p.file_path);
  if (ev !== 'preToolUse') return `the ${ev} event is not covered by audit mode`;
  const ti = p.tool_input;
  switch (p.tool_name) {
    case 'Shell': return shell(isObj(ti) ? ti.command : undefined);
    case 'Read': // the beforeReadFile hook checks the path when this input names none
      return isObj(ti) && isStr(ti.file_path ?? ti.path) ? read(ti.file_path ?? ti.path) : null;
    case 'Grep': return search('Grep', ti);
    case 'Glob': return search('Glob', ti);
    default: return `the ${String(p.tool_name)} tool is not allowed in audit mode`;
  }
}

function answer(reason) {
  if (reason === null) {
    writeSync(1, JSON.stringify({ permission: 'allow' }) + '\n');
    process.exit(0);
  }
  const msg = `Hullproof audit mode blocked this call: ${reason}. ${END}`;
  writeSync(1, JSON.stringify({ permission: 'deny', user_message: msg, agent_message: msg }) + '\n');
  writeSync(2, msg + '\n');
  process.exit(2);
}

function main() {
  let reason = null;
  try {
    const raw = readFileSync(0, 'utf8');
    let p = null;
    if (raw.length <= MAX_INPUT) { try { p = JSON.parse(raw); } catch { p = null; } }
    if (!isObj(p)) reason = 'could not read the hook input';
    else if (process.env.HULLPROOF_AUDIT === '1' || existsSync(MARKER)) reason = decide(p);
  } catch (e) {
    reason = `internal error (${e && e.message ? e.message : 'unknown'})`;
  }
  answer(reason);
}
main();
