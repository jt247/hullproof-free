#!/usr/bin/env node
// Hullproof Gemini CLI hook adapter. Translates the Gemini CLI BeforeTool hook input into the input of
// .claude/hooks/hullproof-readonly-bash.mjs (profile reviewer, read only), runs that hook, and answers in the Gemini CLI format.
// Gemini input on stdin: { tool_name, tool_input, cwd, ... }. run_shell_command carries tool_input.command.
// Answer: exit 0 with no output allows. Exit 2 with the reason on stderr blocks. Gemini CLI treats any other non zero exit as a warning and continues, so every failure path exits 2.
// Audit mode: the adapter enforces read only only while docs/security/.audit-mode exists in the project root, or HULLPROOF_AUDIT=1 is set.
// Outside audit mode it allows every well formed call, so normal work is not blocked, except the always on denies below.
// Always on denies (any mode): shell commands that name a secret file (.env files other than the example files, .pem, id_rsa, id_ed25519),
// and edits or shell writes that touch the Hullproof hook and adapter files or the hook config of the tools. Input that is not valid JSON is denied in every mode.
// In audit mode only shell commands that the hook accepts are allowed. Every other tool this hook is attached to (the write tools) is denied.
// Zero dependencies. Installed at tools/hullproof/hooks/gemini-adapter.mjs, with the Claude Code hook at .claude/hooks/ in the same project root.
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const HOOK = join(ROOT, '.claude', 'hooks', 'hullproof-readonly-bash.mjs');
const MARKER = join(ROOT, 'docs', 'security', '.audit-mode');
const PROFILE = 'reviewer';
const MAX_INPUT = 2_000_000;
const SHELL_TOOL = 'run_shell_command';
const END = 'Only the owner turns audit mode off, by deleting docs/security/.audit-mode.';
const BOUNDARY = '(^|[\\s\'"=:/\\\\(])';
const SECRET = new RegExp(BOUNDARY + '(\\.env(\\.(?!example\\b|sample\\b|template\\b)[\\w.-]+)?|[\\w.-]*\\.pem|id_rsa|id_ed25519)(?=$|[\\s\'";|&)<>])');
const PROTECTED = new RegExp(BOUNDARY + '(tools[\\\\/]hullproof[\\\\/]hooks[\\\\/]|\\.claude[\\\\/]hooks[\\\\/]|\\.claude[\\\\/]settings\\.json|\\.codex[\\\\/]hooks\\.json|\\.agents[\\\\/]hooks\\.json|\\.gemini[\\\\/]settings\\.json)');
const SHELL_WRITE = />|\btee\b|\bsed\s+-\w*i|\bperl\s+-\w*i|\brm\b|\bmv\b|\bcp\b|\bchmod\b|\bln\b|\btruncate\b|\bdd\b|\binstall\b|\bpython3?\b|\bnode\b|\bgit\s+(checkout|restore|stash|reset|clean)\b/;

const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

function viaHook(command) {
  if (!existsSync(HOOK)) return 'the Hullproof read only hook is missing from .claude/hooks';
  const r = spawnSync(process.execPath, ['--', HOOK, PROFILE], {
    input: JSON.stringify({ tool_name: 'Bash', tool_input: { command } }),
    encoding: 'utf8', timeout: 15000, maxBuffer: 1_000_000, env: { ...process.env, CLAUDE_PROJECT_DIR: ROOT },
  });
  if (r.error) return `the read only hook could not run (${r.error.message})`;
  if (r.status === 0) return null;
  return (r.stderr || '').trim().replace(/^Hullproof read only (hook|guard) blocked this call: /, '').replace(/\.+$/, '') || 'the read only hook refused this call';
}

function extract(p) {
  const tool = p.tool_name;
  if (typeof tool !== 'string') return 'tool_name is missing';
  const ti = p.tool_input;
  const call = { tool, command: '', text: JSON.stringify(ti ?? null) };
  if (tool === 'run_shell_command') {
    const c = ti && ti.command;
    if (typeof c !== 'string') return 'could not read the command';
    call.command = c;
  }
  return call;
}

// Returns a reason text when the call is always denied, whatever the mode, or null.
function alwaysDeny({ tool, command, text }) {
  if (tool === SHELL_TOOL) {
    if (SECRET.test(command)) return 'shell commands may not name secret files';
    if (PROTECTED.test(command) && SHELL_WRITE.test(command)) return 'the Hullproof hook files may not be changed';
    return null;
  }
  return PROTECTED.test(text) ? 'the Hullproof hook files may not be changed' : null;
}

// Returns null to allow, or a reason text to deny.
function decide(raw) {
  if (raw.length > MAX_INPUT) return 'the hook input is too large';
  let p = null;
  try { p = JSON.parse(raw); } catch { p = null; }
  if (!isObj(p)) return 'could not read the hook input';
  const call = extract(p);
  if (typeof call === 'string') return call;
  const fixed = alwaysDeny(call);
  if (fixed) return fixed;
  if (process.env.HULLPROOF_AUDIT !== '1' && !existsSync(MARKER)) return null;
  const why = call.tool === SHELL_TOOL ? viaHook(call.command) : `the ${call.tool} tool is not allowed in audit mode`;
  return why && `${why}. ${END}`;
}

const say = (reason) => `Hullproof guard blocked this call: ${reason.replace(/\.+$/, '')}.`;

function deny(reason) {
  try { writeSync(2, `${say(reason)}\n`); } catch { /* nothing to do */ }
  process.exit(2);
}
function allow() { process.exit(0); }

function main() {
  process.on('uncaughtException', (e) => deny(`internal error (${e && e.message ? e.message : 'unknown'})`));
  let reason;
  try { reason = decide(readFileSync(0, 'utf8')); } catch (e) { reason = `internal error (${e && e.message ? e.message : 'unknown'})`; }
  if (reason) deny(reason);
  allow();
}
main();
