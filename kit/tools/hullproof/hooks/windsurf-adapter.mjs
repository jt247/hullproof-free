#!/usr/bin/env node
// Hullproof Windsurf and Devin hook adapter. Translates hook input from both agents into the input of
// .claude/hooks/hullproof-readonly-bash.mjs (profile skill), runs that hook, and blocks with exit 2.
// Cascade (Devin Desktop), .devin/hooks.json: { agent_action_name, tool_info } for pre_read_code (tool_info.file_path),
//   pre_run_command (tool_info.command_line), pre_write_code and pre_mcp_tool_use. Exit 2 blocks, any other exit lets the action run.
// Devin CLI and Devin Local, .devin/hooks.v1.json: { hook_event_name: "PreToolUse", tool_name, tool_input }. Exit 2 or { decision: "block" } blocks.
// The config files run this adapter as "node <adapter> || exit 2", so a crash or a missing adapter also blocks.
// Audit mode: the adapter enforces only while docs/security/.audit-mode exists in the project root, or HULLPROOF_AUDIT=1 is set.
// Outside audit mode it allows every well formed call, so normal work is not blocked. Input that is not JSON is denied in every mode.
// In audit mode only these are allowed: shell commands, reads, Grep and Glob calls the hook accepts, and a few tools with no side effects.
// Writes, edits, subagents, web fetches, MCP calls and every tool not named here are denied.
// Zero dependencies. Installed at tools/hullproof/hooks/windsurf-adapter.mjs, with the Claude Code hook at .claude/hooks/ in the same project root.
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const HOOK = join(ROOT, '.claude', 'hooks', 'hullproof-readonly-bash.mjs');
const MARKER = join(ROOT, 'docs', 'security', '.audit-mode');
const PROFILE = 'skill';
const MAX_INPUT = 2_000_000;
const END = 'Only the owner turns audit mode off, by deleting docs/security/.audit-mode.';
const SAFE_DEVIN_TOOLS = new Set(['get_output', 'todo_write', 'exit_plan_mode', 'skill']);

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

function cascade(p) {
  const ti = isObj(p.tool_info) ? p.tool_info : {};
  switch (p.agent_action_name) {
    case 'pre_read_code': return read(ti.file_path);
    case 'pre_run_command': return shell(ti.command_line);
    case 'pre_write_code': return 'file writes are not allowed in audit mode';
    case 'pre_mcp_tool_use': return 'MCP tools are not allowed in audit mode';
    default: return `the ${String(p.agent_action_name)} event is not covered by audit mode`;
  }
}

function devin(p) {
  const ti = p.tool_input;
  switch (p.tool_name) {
    case 'exec': return shell(isObj(ti) ? ti.command : undefined);
    case 'read': return isObj(ti) ? read(ti.file_path ?? ti.path) : 'could not read the file path';
    case 'grep': return search('Grep', ti);
    case 'glob': return search('Glob', ti);
    default: return SAFE_DEVIN_TOOLS.has(p.tool_name) ? null : `the ${String(p.tool_name)} tool is not allowed in audit mode`;
  }
}

// Returns null to allow, or a reason text to deny. Only called in audit mode.
function decide(p) {
  if (typeof p.agent_action_name === 'string') return cascade(p);
  if (p.hook_event_name === 'PreToolUse') return devin(p);
  return 'the hook event is not covered by audit mode';
}

function block(reason, asDevin) {
  const msg = `Hullproof audit mode blocked this call: ${reason}. ${END}`;
  if (asDevin) writeSync(1, JSON.stringify({ decision: 'block', reason: msg }) + '\n');
  writeSync(2, msg + '\n');
  process.exit(2);
}

function main() {
  let reason = null;
  let asDevin = false;
  try {
    const raw = readFileSync(0, 'utf8');
    let p = null;
    if (raw.length <= MAX_INPUT) { try { p = JSON.parse(raw); } catch { p = null; } }
    if (!isObj(p)) reason = 'could not read the hook input';
    else {
      asDevin = typeof p.hook_event_name === 'string';
      if (process.env.HULLPROOF_AUDIT === '1' || existsSync(MARKER)) reason = decide(p);
    }
  } catch (e) {
    reason = `internal error (${e && e.message ? e.message : 'unknown'})`;
  }
  if (reason !== null) block(reason, asDevin);
  process.exit(0);
}
main();
