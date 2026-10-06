#!/usr/bin/env node
// Hullproof installer. Zero dependencies, Node 18+.
// Usage: node tools/hullproof/install.mjs --tool <name> [--write] [--project <dir>] [--list] [--all]
// Exit codes: 0 ok, 1 error, 2 nothing to do.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const BEGIN = '<!-- hullproof:begin -->';
const END = '<!-- hullproof:end -->';
const MODES = new Set(['never', 'append', 'json']);
const LABELS = { enforced: 'ENFORCED', partial: 'PARTIAL', advisory: 'ADVISORY' };

class Fail extends Error {}

function parseArgs(argv) {
  const o = { write: false, list: false, all: false, tool: null, project: null, kit: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => {
      if (i + 1 >= argv.length || argv[i + 1].startsWith('--')) throw new Fail(`${a} needs a value.`);
      return argv[++i];
    };
    if (a === '--write') o.write = true;
    else if (a === '--list') o.list = true;
    else if (a === '--all') o.all = true;
    else if (a === '--tool') o.tool = val();
    else if (a === '--project') o.project = val();
    else if (a === '--kit') o.kit = val(); // addition: lets tests point at fixtures
    else if (a === '--help' || a === '-h') o.help = true;
    else throw new Fail(`Unknown option ${a}. Use --help.`);
  }
  return o;
}

const HELP = `Usage: node tools/hullproof/install.mjs --tool <name> [--write] [--project <dir>]
       node tools/hullproof/install.mjs --all [--write] [--project <dir>]
       node tools/hullproof/install.mjs --list

Default is a dry run. Add --write to apply. --project defaults to the current folder.`;

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

function planFile(tool, f, projectReal, kit) {
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
        throw new Fail(`Refused to merge into ${rel} because it does not parse as JSON (${err.message}). Fix or move that file, then run again.`);
      }
      const notes = [];
      const merged = deepMerge(cur, add, notes);
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

export function main(argv, out = console.log, err = console.error) {
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
    const plans = chosen.map((t) => ({ t, items: planTool(t, projectReal, kit) }));
    const doing = plans.flatMap((p) => p.items).filter((i) => i.write !== null);

    out(o.write ? `Installing into ${projectReal}` : `Dry run for ${projectReal} (nothing is written)`);
    for (const { t, items } of plans) {
      const d = t.data;
      out(`\n${d.displayName || t.name}`);
      for (const i of items) out(`  ${i.rel}: ${i.msg}`);
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
