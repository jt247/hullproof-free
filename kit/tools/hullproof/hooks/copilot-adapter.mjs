#!/usr/bin/env node
// Hullproof GitHub Copilot hook adapter. Translates a preToolUse hook input into the input of
// .claude/hooks/hullproof-readonly-bash.mjs (profile skill), runs that hook, and answers in the Copilot format.
// Copilot CLI (.github/hooks/hullproof-cli.json): { sessionId, cwd, toolName, toolArgs }, camelCase.
// VS Code Local and the Claude Code format names (.github/hooks/hullproof-vscode.json): { hook_event_name: "PreToolUse", tool_name, tool_input }.
// toolArgs and tool_input may be an object or a JSON string. Tool names are matched without regard to case.
// Answer: exit 0 with no output lets Copilot use its normal permission flow, so the adapter never grants an allow.
// A deny prints permissionDecision deny in both formats and exits 2 with the reason on stderr (exit 2 always denies in the CLI).
// A command hook timeout is fail open in Copilot, so the adapter stops its own work after 15 seconds and the config sets 30.
// Audit mode: the adapter enforces only while docs/security/.audit-mode exists in the project root, or HULLPROOF_AUDIT=1 is set.
// Outside audit mode it allows every well formed call, so normal work is not blocked. Input that is not JSON is denied in every mode.
// In audit mode only these are allowed: bash commands, reads, grep and glob calls the hook accepts, and two tools with no side effects.
// Writes, edits, subagents, web fetches, PowerShell and every tool not named here are denied. The VS Code Local tool names are not
// documented, so a Local tool the adapter cannot name is denied.
// Zero dependencies. Installed at tools/hullproof/hooks/copilot-adapter.mjs, with the Claude Code hook at .claude/hooks/ in the same project root.
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
const SAFE_TOOLS = new Set(['ask_user', 'update_todo']);

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

function asObject(v) {
  if (typeof v === 'string') { try { v = JSON.parse(v); } catch { return null; } }
  return isObj(v) ? v : null;
}

// Returns null to allow, or a reason text to deny. Only called in audit mode.
function decide(p) {
  const name = String(p.toolName ?? p.tool_name ?? '').toLowerCase();
  const args = asObject(p.toolArgs ?? p.tool_input);
  if (SAFE_TOOLS.has(name)) return null;
  if (args === null) return 'could not read the tool arguments';
  switch (name) {
    case 'bash':
      return isStr(args.command) ? viaHook({ tool_name: 'Bash', tool_input: { command: args.command } }) : 'could not read the command';
    case 'view':
    case 'read': {
      const file_path = args.path ?? args.file_path;
      return isStr(file_path) ? viaHook({ tool_name: 'Read', tool_input: { file_path } }) : 'could not read the file path';
    }
    case 'grep':
    case 'rg': return viaHook({ tool_name: 'Grep', tool_input: args });
    case 'glob': return viaHook({ tool_name: 'Glob', tool_input: args });
    default: return `the ${name || 'unnamed'} tool is not allowed in audit mode`;
  }
}

function deny(reason) {
  const msg = `Hullproof audit mode blocked this call: ${reason}. ${END}`;
  const decision = { permissionDecision: 'deny', permissionDecisionReason: msg };
  writeSync(1, JSON.stringify({ ...decision, hookSpecificOutput: { hookEventName: 'PreToolUse', ...decision } }) + '\n');
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
  if (reason !== null) deny(reason);
  process.exit(0);
}
main();
