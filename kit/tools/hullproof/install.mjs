#!/usr/bin/env node
// Hullproof installer. Zero dependencies, Node 18+.
// Usage: node tools/hullproof/install.mjs --tool <name> [--write] [--with-engine] [--project <dir>] [--list] [--all]
// Exit codes: 0 ok, 1 error, 2 nothing to do.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const BEGIN = '<!-- hullproof:begin -->';
const END = '<!-- hullproof:end -->';
const MODES = new Set(['never', 'append', 'json']);
const MCP_MERGES = new Set(['json', 'toml']);
const TOML_BEGIN = '# hullproof:begin';
const TOML_END = '# hullproof:end';
const ENGINE_HELP = 'https://github.com/jt247/hullproof-engine';
const LABELS = { enforced: 'ENFORCED', partial: 'PARTIAL', advisory: 'ADVISORY' };

class Fail extends Error {}

function parseArgs(argv) {
  const o = { write: false, list: false, all: false, withEngine: false, tool: null, project: null, kit: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => {
      if (i + 1 >= argv.length || argv[i + 1].startsWith('--')) throw new Fail(`${a} needs a value.`);
      return argv[++i];
    };
    if (a === '--write') o.write = true;
    else if (a === '--list') o.list = true;
    else if (a === '--all') o.all = true;
    else if (a === '--with-engine') o.withEngine = true;
    else if (a === '--tool') o.tool = val();
    else if (a === '--project') o.project = val();
    else if (a === '--kit') o.kit = val(); // addition: lets tests point at fixtures
    else if (a === '--help' || a === '-h') o.help = true;
    else throw new Fail(`Unknown option ${a}. Use --help.`);
  }
  return o;
}

const HELP = `Usage: node tools/hullproof/install.mjs --tool <name> [--write] [--with-engine] [--project <dir>]
       node tools/hullproof/install.mjs --all [--write] [--with-engine] [--project <dir>]
       node tools/hullproof/install.mjs --list

Default is a dry run. Add --write to apply. --project defaults to the current folder.
--with-engine also writes the MCP settings that start the Hullproof engine (hullproof mcp) for the tool,
and reports whether the hullproof command is on your PATH. Without it nothing about the engine changes.`;

function findKitRoot(start) {
  let dir = start;
  for (;;) {
    if (isDir(path.join(dir, 'editors'))) return dir;
    const up = path.dirname(dir);
    if (up === dir) throw new Fail('Could not find an editors folder above this script.');
    dir = up;
  }
}

function isDir(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}

function loadTools(kit) {
  const root = path.join(kit, 'editors');
  const tools = [];
  for (const name of fs.readdirSync(root).sort()) {
    const dir = path.join(root, name);
    const file = path.join(dir, 'TOOL.json');
    if (!isDir(dir) || !fs.existsSync(file)) continue;
    const t = { dir, folder: name, problems: [], data: null };
    try {
      t.data = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^﻿/, ''));
    } catch (e) {
      t.problems.push(`TOOL.json does not parse: ${e.message}`);
    }
    if (t.data) t.problems.push(...validateTool(t.data));
    t.name = (t.data && t.data.tool) || name;
    tools.push(t);
  }
  return tools;
}

function validateTool(d) {
  const p = [];
  if (typeof d.tool !== 'string' || !d.tool) p.push('"tool" must be a non empty string');
  if (typeof d.displayName !== 'string' || !d.displayName) p.push('"displayName" must be a non empty string');
  if (!Array.isArray(d.files) || d.files.length === 0) p.push('"files" must be a non empty array');
  else {
    d.files.forEach((f, i) => {
      if (!f || typeof f.src !== 'string' || !f.src) p.push(`files[${i}].src must be a string`);
      if (!f || typeof f.dest !== 'string' || !f.dest) p.push(`files[${i}].dest must be a string`);
      if (!f || !MODES.has(f.merge)) p.push(`files[${i}].merge must be never, append or json`);
      if (f && f.from !== undefined && f.from !== 'kit') p.push(`files[${i}].from must be "kit" when present`);
    });
  }
  if (!LABELS[d.enforcement]) p.push('"enforcement" must be enforced, partial or advisory');
  if (typeof d.enforcementNote !== 'string' || !d.enforcementNote) p.push('"enforcementNote" must be a string');
  if (typeof d.firstRun !== 'string' || !d.firstRun) p.push('"firstRun" must be a string');
  if (d.surfaces !== undefined && !Array.isArray(d.surfaces)) p.push('"surfaces" must be an array');
  if (d.ways !== undefined && !Array.isArray(d.ways)) p.push('"ways" must be an array');
  if (d.engine !== undefined) p.push(...validateEngine(d.engine));
  return p;
}

function validateEngine(e) {
  const p = [];
  if (!isObj(e)) return ['"engine" must be an object'];
  if (typeof e.canRun !== 'boolean') p.push('engine.canRun must be true or false');
  const m = e.mcp;
  if (!isObj(m) || typeof m.supported !== 'boolean') return [...p, 'engine.mcp.supported must be true or false'];
  if (m.supported) {
    if (typeof m.src !== 'string' || !m.src) p.push('engine.mcp.src must be a string');
    if (typeof m.dest !== 'string' || !m.dest) p.push('engine.mcp.dest must be a string');
    if (!MCP_MERGES.has(m.merge)) p.push('engine.mcp.merge must be json or toml');
  }
  return p;
}

function distance(a, b) {
  const m = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 0; j <= b.length; j++) m[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      m[i][j] = Math.min(m[i - 1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return m[a.length][b.length];
}

function findTool(tools, query) {
  const q = query.trim().toLowerCase();
  const hit = tools.find((t) => t.name.toLowerCase() === q || t.folder.toLowerCase() === q ||
    (t.data && String(t.data.displayName || '').toLowerCase() === q));
  if (hit) return hit;
  const scored = tools
    .map((t) => {
      const names = [t.name, t.data && t.data.displayName].filter(Boolean).map((n) => String(n).toLowerCase());
      const d = Math.min(...names.map((n) => (n.includes(q) || q.includes(n) ? 0 : distance(q, n))));
      return { t, d };
    })
    .sort((a, b) => a.d - b.d)
    .slice(0, 3);
  const names = scored.map((s) => s.t.name).join(', ');
  throw new Fail(`Unknown tool "${query}".${names ? ` Closest names: ${names}.` : ''} Run with --list to see every tool.`);
}

function within(root, p) {
  const rel = path.relative(root, p);
  return rel === '' || (rel !== '..' && !rel.startsWith('..' + path.sep) && !path.isAbsolute(rel));
}

// Returns the absolute destination. Rejects absolute paths, traversal and symlink escapes.
function safeDest(projectReal, dest) {
  if (dest.includes('\0')) throw new Fail(`Refused unsafe destination "${dest}".`);
  if (/^[a-zA-Z]:/.test(dest) || dest.startsWith('/') || dest.startsWith('\\')) {
    throw new Fail(`Refused absolute destination "${dest}". Destinations must be inside the project.`);
  }
  const parts = dest.split(/[\\/]+/).filter((s) => s && s !== '.');
  if (parts.length === 0 || parts.includes('..')) throw new Fail(`Refused destination "${dest}" because it leaves the project.`);
  const abs = path.join(projectReal, ...parts);
  if (!within(projectReal, abs)) throw new Fail(`Refused destination "${dest}" because it leaves the project.`);
  let cur = abs;
  while (!fs.existsSync(cur) && !isLink(cur)) cur = path.dirname(cur);
  if (isLink(abs)) throw new Fail(`Refused "${dest}" because it is a symbolic link.`);
  if (!within(projectReal, fs.realpathSync(cur))) throw new Fail(`Refused "${dest}" because a symbolic link points outside the project.`);
  return abs;
}

function isLink(p) {
  try { return fs.lstatSync(p).isSymbolicLink(); } catch { return false; }
}

function deepMerge(base, add, notes, trail = '') {
  if (Array.isArray(base) && Array.isArray(add)) {
    const seen = new Set(base.map((v) => JSON.stringify(v)));
    return [...base, ...add.filter((v) => !seen.has(JSON.stringify(v)))];
  }
  if (isObj(base) && isObj(add)) {
    const out = { ...base };
    for (const [k, v] of Object.entries(add)) {
      out[k] = k in base ? deepMerge(base[k], v, notes, trail + '.' + k) : v;
    }
    return out;
  }
  if (JSON.stringify(base) !== JSON.stringify(add)) notes.push(trail.slice(1) || '(root)');
  return base; // your value wins
}

const isObj = (v) => v && typeof v === 'object' && !Array.isArray(v);
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);

function planFile(tool, f, projectReal, kit, soft = false) {
  // "from":"kit" reads the source relative to the kit root, for files that live outside the tool folder (hook scripts).
  const base = f.from === 'kit' ? kit : tool.dir;
  const src = path.resolve(base, f.src);
  if (!within(base, src)) throw new Fail(`${tool.name}: source "${f.src}" is outside the ${f.from === 'kit' ? 'kit' : 'tool folder'}.`);
  if (!fs.existsSync(src) || !fs.statSync(src).isFile()) throw new Fail(`${tool.name}: source file "${f.src}" is missing from the kit.`);
  const dest = safeDest(projectReal, f.dest);
  const rel = f.dest.replace(/\\/g, '/');
  const exists = fs.existsSync(dest);
  const item = { rel, dest, kind: 'skip', msg: '', write: null, backup: false };

  if (f.merge === 'never') {
    const data = fs.readFileSync(src);
    if (!exists) Object.assign(item, { kind: 'create', msg: 'create', write: data });
    else if (fs.readFileSync(dest).equals(data)) Object.assign(item, { kind: 'same', msg: 'already installed' });
    else Object.assign(item, { kind: 'skip', msg: 'skip, a different file already exists here and was left untouched' + (f.from === 'kit' ? '. Hullproof hooks call this file, so copy the kit version over it by hand if the hook does not run' : '') });
  } else if (f.merge === 'append') {
    const text = fs.readFileSync(src, 'utf8').replace(/^﻿/, '').trim();
    const block = `${BEGIN}\n${text}\n${END}`;
    if (!exists) Object.assign(item, { kind: 'create', msg: 'create with a marked block', write: block + '\n' });
    else {
      const cur = fs.readFileSync(dest, 'utf8');
      const b = cur.indexOf(BEGIN);
      const e = cur.indexOf(END, b + 1);
      let next;
      if (b !== -1 && e !== -1) next = cur.slice(0, b) + block + cur.slice(e + END.length);
      else next = cur.replace(/\s*$/, '') + (cur.trim() ? '\n\n' : '') + block + '\n';
      if (next === cur) Object.assign(item, { kind: 'same', msg: 'already installed' });
      else if (b !== -1 && e !== -1) Object.assign(item, { kind: 'replace', msg: 'replace the marked Hullproof block, text outside it is untouched', write: next });
      else Object.assign(item, { kind: 'append', msg: 'append a marked Hullproof block, existing text is untouched', write: next });
    }
  } else {
    let add;
    try { add = JSON.parse(fs.readFileSync(src, 'utf8').replace(/^﻿/, '')); }
    catch (err) { throw new Fail(`${tool.name}: kit file "${f.src}" is not valid JSON: ${err.message}`); }
    if (!exists) Object.assign(item, { kind: 'create', msg: 'create', write: JSON.stringify(add, null, 2) + '\n' });
    else {
      let cur;
      try { cur = JSON.parse(fs.readFileSync(dest, 'utf8').replace(/^﻿/, '')); }
      catch (err) {
        if (soft) return printItem(rel, dest, `left untouched because it does not parse as JSON (${err.message})`, JSON.stringify(add, null, 2));
        throw new Fail(`Refused to merge into ${rel} because it does not parse as JSON (${err.message}). Fix or move that file, then run again.`);
      }
      const notes = [];
      const merged = deepMerge(cur, add, notes);
      if (soft && (!isObj(cur) || !covers(merged, add))) {
        return printItem(rel, dest, 'left untouched because it already holds a different value for the same setting', JSON.stringify(add, null, 2));
      }
      if (eq(merged, cur)) Object.assign(item, { kind: 'same', msg: 'already installed' });
      else Object.assign(item, {
        kind: 'merge', backup: true,
        msg: `merge into the existing file, your keys are kept, backup written to ${rel}.hullproof.bak`,
        write: JSON.stringify(merged, null, 2) + '\n',
      });
      if (notes.length) item.msg += `. Kept your value for: ${notes.join(', ')}`;
    }
  }
  return item;
}

// True when everything in add is present in base with the same value (arrays: every item of add is in base).
function covers(base, add) {
  if (Array.isArray(add)) return Array.isArray(base) && add.every((v) => base.some((b) => eq(b, v)));
  if (isObj(add)) return isObj(base) && Object.entries(add).every(([k, v]) => k in base && covers(base[k], v));
  return eq(base, add);
}

// An item that changes nothing and tells the reader what to add by hand.
function printItem(rel, dest, why, snippet) {
  return { rel, dest, kind: 'print', msg: `${why}. Add this by hand:`, write: null, backup: false, snippet };
}

// MCP settings in TOML (Codex config.toml). No TOML parser here, so the only edits are a marked block we own,
// or nothing: if the file already defines the server another way, print the snippet instead.
function planToml(tool, f, projectReal, kit) {
  const src = path.resolve(tool.dir, f.src);
  if (!within(tool.dir, src)) throw new Fail(`${tool.name}: source "${f.src}" is outside the tool folder.`);
  if (!fs.existsSync(src) || !fs.statSync(src).isFile()) throw new Fail(`${tool.name}: source file "${f.src}" is missing from the kit.`);
  const dest = safeDest(projectReal, f.dest);
  const rel = f.dest.replace(/\\/g, '/');
  const text = fs.readFileSync(src, 'utf8').replace(/^﻿/, '').trim();
  const block = `${TOML_BEGIN}\n${text}\n${TOML_END}`;
  const item = { rel, dest, kind: 'skip', msg: '', write: null, backup: false };
  if (!fs.existsSync(dest)) return Object.assign(item, { kind: 'create', msg: 'create with a marked block', write: block + '\n' });
  const cur = fs.readFileSync(dest, 'utf8');
  const b = cur.indexOf(TOML_BEGIN);
  const e = b === -1 ? -1 : cur.indexOf(TOML_END, b + 1);
  if (b !== -1 && e !== -1) {
    const next = cur.slice(0, b) + block + cur.slice(e + TOML_END.length);
    if (next === cur) return Object.assign(item, { kind: 'same', msg: 'already installed' });
    return Object.assign(item, { kind: 'replace', msg: 'replace the marked Hullproof block, text outside it is untouched', write: next });
  }
  if (/^\s*mcp_servers\s*=/m.test(cur) || /mcp_servers\s*\.\s*["']?hullproof/.test(cur)) {
    return printItem(rel, dest, 'left untouched because it already defines MCP servers in a way this installer does not edit', text);
  }
  const next = cur.replace(/\s*$/, '') + (cur.trim() ? '\n\n' : '') + block + '\n';
  return Object.assign(item, { kind: 'append', msg: 'append a marked Hullproof block, existing text is untouched', write: next });
}

// items are the tool's own planned files. When one of them is the same JSON file as the MCP settings (Gemini CLI keeps its hook settings and
// its MCP servers in .gemini/settings.json), the MCP settings are merged into that planned content, so one write holds both and nothing is lost.
function planEngine(tool, projectReal, kit, items) {
  const m = tool.data.engine && tool.data.engine.mcp;
  if (!m || !m.supported) return [];
  const f = { src: m.src, dest: m.dest, merge: m.merge };
  const same = m.merge === 'json' && items.find((i) => i.dest === safeDest(projectReal, m.dest) && i.write !== null);
  if (same) {
    let add;
    try { add = JSON.parse(fs.readFileSync(path.resolve(tool.dir, m.src), 'utf8').replace(/^﻿/, '')); }
    catch (err) { throw new Fail(`${tool.name}: kit file "${m.src}" is not valid JSON: ${err.message}`); }
    same.write = JSON.stringify(deepMerge(JSON.parse(same.write), add, []), null, 2) + '\n';
    same.msg += ', and the MCP settings are merged into the same file';
    return [{ rel: same.rel, dest: same.dest, kind: 'merge', msg: 'merged into the file above', write: null, backup: false }];
  }
  return [m.merge === 'toml' ? planToml(tool, f, projectReal, kit) : planFile(tool, f, projectReal, kit, true)];
}

// Looks for an executable called name in PATH without running anything.
export function findOnPath(name, env = process.env) {
  const dirs = (env.PATH || '').split(path.delimiter).filter(Boolean);
  const exts = process.platform === 'win32' ? (env.PATHEXT || '.EXE;.CMD;.BAT').split(';') : [''];
  for (const d of dirs) {
    for (const x of exts) {
      const p = path.join(d, name + x);
      try {
        if (!fs.statSync(p).isFile()) continue;
        fs.accessSync(p, fs.constants.X_OK);
        return p;
      } catch { /* not here */ }
    }
  }
  return null;
}

function apply(item) {
  if (!item.write) return;
  fs.mkdirSync(path.dirname(item.dest), { recursive: true });
  if (item.backup) fs.copyFileSync(item.dest, item.dest + '.hullproof.bak');
  fs.writeFileSync(item.dest, item.write);
}

function planTool(tool, projectReal, kit) {
  if (tool.problems.length) throw new Fail(`${tool.name}: TOOL.json problems: ${tool.problems.join('; ')}.`);
  return tool.data.files.map((f) => planFile(tool, f, projectReal, kit));
}

function printEngineStatus(projectReal, env, out) {
  const found = findOnPath('hullproof', env);
  if (!found) {
    out(`\nEngine: the hullproof command was not found on your PATH. Install the engine first (the engine folder of your package, or ${ENGINE_HELP}, whose README says how). The MCP settings below start that command, so they work only once it is installed.`);
    return;
  }
  let real = found;
  try { real = fs.realpathSync(found); } catch { /* keep the PATH entry */ }
  out(`\nEngine: the hullproof command is on your PATH at ${found}.`);
  if (within(projectReal, real)) out('Note: that command is inside this project. Hullproof audits do not run an engine that comes from the audited project, so install the engine outside the project.');
}

function printEngineItems(d, items, out) {
  const e = d.engine;
  if (!e || !e.canRun) {
    out('  Engine mode: this tool cannot run the engine, so its audit is prompt based. Run hullproof ci on your own machine or in CI, then paste .hullproof/ci/report.md into the chat.');
    return;
  }
  out('  Engine mode: this tool can run the engine. Run hullproof ci from the project root before the audit. Steps: tools/hullproof/helpers/engine-mode.md.');
  if (!e.mcp || !e.mcp.supported) {
    out('  MCP: add the server to your tool\'s MCP settings with command hullproof and argument mcp.');
    return;
  }
  for (const i of items) {
    out(`  ${i.rel} (MCP settings): ${i.msg}`);
    if (i.snippet) out(i.snippet.split('\n').map((l) => `      ${l}`).join('\n'));
  }
}

function printList(tools, out) {
  for (const t of tools) {
    const d = t.data || {};
    out(`${t.name}${d.displayName ? ` (${d.displayName})` : ''}${d.edition ? ` [${d.edition}]` : ''}`);
    out(`  surfaces:    ${(d.surfaces || []).join(', ') || 'none listed'}`);
    out(`  ways:        ${(d.ways || []).join(', ') || 'none listed'}`);
    out(`  enforcement: ${LABELS[d.enforcement] || 'not set'}`);
    if (t.problems.length) out(`  TOOL.json problems: ${t.problems.join('; ')}`);
  }
}

export function main(argv, out = console.log, err = console.error, env = process.env) {
  try {
    const o = parseArgs(argv);
    if (o.help || (!o.list && !o.all && !o.tool)) { out(HELP); return o.help ? 0 : 1; }
    const kit = o.kit ? path.resolve(o.kit) : findKitRoot(path.dirname(fileURLToPath(import.meta.url)));
    const tools = loadTools(kit);
    if (tools.length === 0) throw new Fail('No tools found in the editors folder.');
    if (o.list) { printList(tools, out); return 0; }
    if (o.all && o.tool) throw new Fail('Use either --tool or --all, not both.');

    const project = path.resolve(o.project || process.cwd());
    if (!isDir(project)) throw new Fail(`Project folder not found: ${project}`);
    const projectReal = fs.realpathSync(project);
    const chosen = o.all ? tools : [findTool(tools, o.tool)];

    // Plan everything first so a refusal changes nothing.
    const plans = chosen.map((t) => {
      const items = planTool(t, projectReal, kit);
      return { t, items, engine: o.withEngine ? planEngine(t, projectReal, kit, items) : [] };
    });
    // Two tools can write the same file with the same content (Claude Code and Copilot share .mcp.json): count and write that once.
    const seen = new Set();
    const doing = plans.flatMap((p) => [...p.items, ...p.engine]).filter((i) => i.write !== null && !seen.has(i.dest + '\0' + i.write) && seen.add(i.dest + '\0' + i.write));

    out(o.write ? `Installing into ${projectReal}` : `Dry run for ${projectReal} (nothing is written)`);
    if (o.withEngine) printEngineStatus(projectReal, env, out);
    for (const { t, items, engine } of plans) {
      const d = t.data;
      out(`\n${d.displayName || t.name}`);
      for (const i of items) out(`  ${i.rel}: ${i.msg}`);
      if (o.withEngine) printEngineItems(d, engine, out);
      if (d.trustNote) out(`\nTrust note: ${d.trustNote}`);
      out(`\nEnforcement: ${LABELS[d.enforcement]}`);
      out(d.enforcementNote);
      out(`\nFirst run:\n  ${d.firstRun}`);
    }

    if (doing.length === 0) { out('\nNothing to do.'); return 2; }
    if (o.write) {
      doing.forEach(apply);
      out(`\nDone. ${doing.length} file${doing.length === 1 ? '' : 's'} written.`);
    } else {
      out('\nNothing was written. Run again with --write to apply.');
    }
    return 0;
  } catch (e) {
    if (e instanceof Fail) { err(`Error: ${e.message}`); return 1; }
    err(`Error: ${e && e.message ? e.message : e}`);
    return 1;
  }
}

// Compare real paths: a script reached through a symbolic link (macOS /var/folders, a linked tools folder) must still run.
const isMain = (() => {
  try { return !!process.argv[1] && fs.realpathSync(process.argv[1]) === fs.realpathSync(fileURLToPath(import.meta.url)); } catch { return false; }
})();
if (isMain) {
  process.exitCode = main(process.argv.slice(2));
}
