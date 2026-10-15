import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const script = path.join(here, 'install.mjs');
const kit = path.join(here, 'tests', 'fixtures', 'install');

function tmp() { return fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'hp-install-'))); }
function run(args, project) {
  const a = [script, '--kit', kit, ...args];
  if (project) a.push('--project', project);
  const r = spawnSync(process.execPath, a, { encoding: 'utf8' });
  return { code: r.status, out: r.stdout + r.stderr };
}
const read = (p, f) => fs.readFileSync(path.join(p, f), 'utf8');
const BEGIN = '<!-- hullproof:begin -->';

test('dry run changes nothing and prints notes', () => {
  const p = tmp();
  const r = run(['--tool', 'nevertool'], p);
  assert.equal(r.code, 0);
  assert.match(r.out, /create/);
  assert.match(r.out, /Trust the folder first/);
  assert.match(r.out, /ADVISORY/);
  assert.match(r.out, /Run a Hullproof audit/);
  assert.deepEqual(fs.readdirSync(p), []);
});

test('write creates files, rerun is idempotent with exit 2', () => {
  const p = tmp();
  for (const t of ['nevertool', 'appendtool', 'jsontool']) assert.equal(run(['--tool', t, '--write'], p).code, 0);
  assert.equal(read(p, '.never/rules/a.md'), '# never rule\nbody\n');
  assert.ok(read(p, 'AGENTS.md').includes(BEGIN));
  assert.ok(fs.existsSync(path.join(p, '.cfg/settings.json')));
  for (const t of ['nevertool', 'appendtool', 'jsontool']) {
    const r = run(['--tool', t, '--write'], p);
    assert.equal(r.code, 2);
    assert.match(r.out, /already installed/);
  }
  assert.ok(!fs.existsSync(path.join(p, '.cfg/settings.json.hullproof.bak')));
});

test('tool name is case insensitive and matches display name', () => {
  assert.equal(run(['--tool', 'APPEND TOOL'], tmp()).code, 0);
});

test('never mode leaves a different existing file alone', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.never/rules'), { recursive: true });
  fs.writeFileSync(path.join(p, '.never/rules/a.md'), 'mine');
  const r = run(['--tool', 'nevertool', '--write'], p);
  assert.equal(r.code, 2);
  assert.match(r.out, /skip/);
  assert.equal(read(p, '.never/rules/a.md'), 'mine');
});

test('append block is replaced, not duplicated, and outside text is kept', () => {
  const p = tmp();
  fs.writeFileSync(path.join(p, 'AGENTS.md'), 'my top\n\n' + BEGIN + '\nold text\n<!-- hullproof:end -->\n\nmy bottom\n');
  assert.equal(run(['--tool', 'appendtool', '--write'], p).code, 0);
  const s = read(p, 'AGENTS.md');
  assert.equal(s.split(BEGIN).length - 1, 1);
  assert.ok(s.startsWith('my top\n\n'));
  assert.ok(s.endsWith('\n\nmy bottom\n'));
  assert.ok(s.includes('Hullproof rules v1') && !s.includes('old text'));
});

test('append adds a block after existing user text', () => {
  const p = tmp();
  fs.writeFileSync(path.join(p, 'AGENTS.md'), 'user rules\n');
  run(['--tool', 'appendtool', '--write'], p);
  const s = read(p, 'AGENTS.md');
  assert.ok(s.startsWith('user rules\n\n' + BEGIN));
});

test('json merge keeps user keys, merges arrays by value, writes backup', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.cfg'));
  const mine = { permissions: { deny: ['Edit', 'Mine'], allow: ['x'] }, mode: 'custom', extra: 1 };
  fs.writeFileSync(path.join(p, '.cfg/settings.json'), JSON.stringify(mine));
  const r = run(['--tool', 'jsontool', '--write'], p);
  assert.equal(r.code, 0);
  assert.match(r.out, /mode/);
  const got = JSON.parse(read(p, '.cfg/settings.json'));
  assert.deepEqual(got.permissions.deny, ['Edit', 'Mine', 'Bash(rm:*)']);
  assert.deepEqual(got.permissions.allow, ['x']);
  assert.equal(got.mode, 'custom');
  assert.equal(got.extra, 1);
  assert.deepEqual(got.hooks, ['h1']);
  assert.deepEqual(JSON.parse(read(p, '.cfg/settings.json.hullproof.bak')), mine);
  assert.equal(run(['--tool', 'jsontool', '--write'], p).code, 2);
});

test('bad json is refused and left untouched', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.cfg'));
  fs.writeFileSync(path.join(p, '.cfg/settings.json'), '{ nope');
  const r = run(['--tool', 'jsontool', '--write'], p);
  assert.equal(r.code, 1);
  assert.match(r.out, /does not parse/);
  assert.equal(read(p, '.cfg/settings.json'), '{ nope');
});

function badKit(dest) {
  const k = tmp();
  const d = path.join(k, 'editors', 'bad');
  fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(d, 'f.txt'), 'x');
  fs.writeFileSync(path.join(d, 'TOOL.json'), JSON.stringify({
    tool: 'bad', displayName: 'Bad', files: [{ src: 'f.txt', dest, merge: 'never' }],
    enforcement: 'advisory', enforcementNote: 'n', firstRun: 'f',
  }));
  return k;
}
function runKit(k, p) {
  const r = spawnSync(process.execPath, [script, '--kit', k, '--tool', 'bad', '--write', '--project', p], { encoding: 'utf8' });
  return { code: r.status, out: r.stdout + r.stderr };
}

test('traversal and absolute destinations are refused', () => {
  for (const dest of ['../escape.txt', 'a/../../escape.txt', '..\\escape.txt', '/etc/hullproof.txt', 'C:\\x\\y.txt']) {
    const p = tmp();
    const r = runKit(badKit(dest), p);
    assert.equal(r.code, 1, dest);
    assert.match(r.out, /Refused/);
    assert.deepEqual(fs.readdirSync(p), []);
  }
});

test('symlink escape is refused', (t) => {
  const p = tmp();
  const outside = tmp();
  try { fs.symlinkSync(outside, path.join(p, 'link'), 'dir'); } catch { t.skip('symlinks not available'); return; }
  const r = runKit(badKit('link/x.txt'), p);
  assert.equal(r.code, 1);
  assert.match(r.out, /symbolic link/);
  assert.deepEqual(fs.readdirSync(outside), []);
});

test('unknown tool gives an error with suggestions', () => {
  const r = run(['--tool', 'apend'], tmp());
  assert.equal(r.code, 1);
  assert.match(r.out, /Unknown tool "apend"/);
  assert.match(r.out, /appendtool/);
});

test('list prints surfaces, ways and enforcement', () => {
  const r = run(['--list']);
  assert.equal(r.code, 0);
  assert.match(r.out, /appendtool \(Append Tool\)/);
  assert.match(r.out, /surfaces:\s+desktop, cli/);
  assert.match(r.out, /ways:\s+agent, rules/);
  assert.match(r.out, /enforcement: ENFORCED/);
});

test('all installs every tool', () => {
  const p = tmp();
  assert.equal(run(['--all', '--write'], p).code, 0);
  assert.ok(fs.existsSync(path.join(p, 'AGENTS.md')) && fs.existsSync(path.join(p, '.cfg/settings.json')));
});

test('from kit copies files that live outside the tool folder, rerun is idempotent', () => {
  const p = tmp();
  assert.equal(run(['--tool', 'kittool', '--write'], p).code, 0);
  assert.equal(read(p, '.claude/hooks/fixture-hook.mjs'), '// fixture hook\n');
  assert.equal(read(p, 'tools/hullproof/hooks/kittool-adapter.mjs'), '// fixture adapter\n');
  assert.equal(run(['--tool', 'kittool', '--write'], p).code, 2);
});

test('from kit never overwrites a different user file', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.claude/hooks'), { recursive: true });
  fs.writeFileSync(path.join(p, '.claude/hooks/fixture-hook.mjs'), 'mine');
  const r = run(['--tool', 'kittool', '--write'], p);
  assert.equal(r.code, 0);
  assert.match(r.out, /skip/);
  assert.equal(read(p, '.claude/hooks/fixture-hook.mjs'), 'mine');
});

function fromKit(src, from) {
  const k = tmp();
  const d = path.join(k, 'editors', 'bad');
  fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(d, 'TOOL.json'), JSON.stringify({
    tool: 'bad', displayName: 'Bad', files: [{ src, dest: 'x.txt', merge: 'never', from }],
    enforcement: 'advisory', enforcementNote: 'n', firstRun: 'f',
  }));
  return k;
}

test('from must be kit, and a kit source cannot leave the kit', () => {
  let r = runKit(fromKit('a.txt', 'home'), tmp());
  assert.equal(r.code, 1);
  assert.match(r.out, /from must be "kit"/);
  r = runKit(fromKit('../../outside.txt', 'kit'), tmp());
  assert.equal(r.code, 1);
  assert.match(r.out, /outside the kit/);
  r = runKit(fromKit('missing.txt', 'kit'), tmp());
  assert.equal(r.code, 1);
  assert.match(r.out, /missing from the kit/);
});

test('runs when the script is reached through a symbolic link', (t) => {
  const link = path.join(tmp(), 'linked-install.mjs');
  try { fs.symlinkSync(script, link); } catch { t.skip('symlinks not available'); return; }
  const p = tmp();
  const r = spawnSync(process.execPath, [link, '--kit', kit, '--tool', 'nevertool', '--write', '--project', p], { encoding: 'utf8' });
  assert.equal(r.status, 0);
  assert.match(r.stdout, /Done\./);
  assert.equal(read(p, '.never/rules/a.md'), '# never rule\nbody\n');
});

// ---- --with-engine ----
const MCP_JSON = { mcpServers: { hullproof: { command: 'hullproof', args: ['mcp'] } } };
function runEngine(args, project, pathValue = '') {
  const a = [script, '--kit', kit, ...args];
  if (project) a.push('--project', project);
  const r = spawnSync(process.execPath, a, { encoding: 'utf8', env: { ...process.env, PATH: pathValue } });
  return { code: r.status, out: r.stdout + r.stderr };
}

test('without --with-engine no MCP file is planned or written', () => {
  const p = tmp();
  const r = run(['--tool', 'mcpjson', '--write'], p);
  assert.equal(r.code, 0);
  assert.ok(!fs.existsSync(path.join(p, '.mcpjson')));
  assert.doesNotMatch(r.out, /MCP settings|Engine/);
});

test('with --with-engine a dry run lists the MCP file and writes nothing', () => {
  const p = tmp();
  const r = runEngine(['--tool', 'mcpjson', '--with-engine'], p);
  assert.equal(r.code, 0);
  assert.match(r.out, /\.mcpjson\/mcp\.json \(MCP settings\): create/);
  assert.match(r.out, /was not found on your PATH/);
  assert.deepEqual(fs.readdirSync(p), []);
});

test('with --with-engine write creates the JSON file, rerun exits 2', () => {
  const p = tmp();
  assert.equal(runEngine(['--tool', 'mcpjson', '--with-engine', '--write'], p).code, 0);
  assert.deepEqual(JSON.parse(read(p, '.mcpjson/mcp.json')), MCP_JSON);
  const r = runEngine(['--tool', 'mcpjson', '--with-engine', '--write'], p);
  assert.equal(r.code, 2);
  assert.match(r.out, /already installed/);
});

test('an existing JSON MCP file is merged with a backup and the user server is kept', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.mcpjson'));
  fs.writeFileSync(path.join(p, '.mcpjson/mcp.json'), JSON.stringify({ mcpServers: { mine: { command: 'x' } } }));
  assert.equal(runEngine(['--tool', 'mcpjson', '--with-engine', '--write'], p).code, 0);
  const got = JSON.parse(read(p, '.mcpjson/mcp.json'));
  assert.deepEqual(got.mcpServers.mine, { command: 'x' });
  assert.deepEqual(got.mcpServers.hullproof, MCP_JSON.mcpServers.hullproof);
  assert.ok(fs.existsSync(path.join(p, '.mcpjson/mcp.json.hullproof.bak')));
});

test('a JSON MCP file that does not parse is left alone and the snippet is printed', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.mcpjson'));
  fs.writeFileSync(path.join(p, '.mcpjson/mcp.json'), '{ // comment\n}');
  const r = runEngine(['--tool', 'mcpjson', '--with-engine', '--write'], p);
  assert.equal(r.code, 0);
  assert.match(r.out, /does not parse as JSON/);
  assert.match(r.out, /"command": "hullproof"/);
  assert.equal(read(p, '.mcpjson/mcp.json'), '{ // comment\n}');
});

test('a different existing hullproof server is never overwritten, the snippet is printed', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.mcpjson'));
  const mine = { mcpServers: { hullproof: { command: 'npx', args: ['other'] } } };
  fs.writeFileSync(path.join(p, '.mcpjson/mcp.json'), JSON.stringify(mine));
  const r = runEngine(['--tool', 'mcpjson', '--with-engine', '--write'], p);
  assert.match(r.out, /different value/);
  assert.deepEqual(JSON.parse(read(p, '.mcpjson/mcp.json')), mine);
  assert.ok(!fs.existsSync(path.join(p, '.mcpjson/mcp.json.hullproof.bak')));
});

test('TOML MCP settings are created, appended after user text, replaced in place, and never duplicated', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.mcptoml'));
  fs.writeFileSync(path.join(p, '.mcptoml/config.toml'), 'model = "x"\n\n[mcp_servers.mine]\ncommand = "y"\n');
  assert.equal(runEngine(['--tool', 'mcptoml', '--with-engine', '--write'], p).code, 0);
  const s = read(p, '.mcptoml/config.toml');
  assert.ok(s.startsWith('model = "x"\n\n[mcp_servers.mine]\ncommand = "y"\n\n# hullproof:begin\n'));
  assert.equal(s.split('# hullproof:begin').length - 1, 1);
  assert.equal(runEngine(['--tool', 'mcptoml', '--with-engine', '--write'], p).code, 2);
  assert.equal(read(p, '.mcptoml/config.toml'), s);
});

test('a TOML file that already defines the hullproof server is left alone and the snippet is printed', () => {
  const p = tmp();
  fs.mkdirSync(path.join(p, '.mcptoml'));
  const mine = '[mcp_servers.hullproof]\ncommand = "npx"\n';
  fs.writeFileSync(path.join(p, '.mcptoml/config.toml'), mine);
  const r = runEngine(['--tool', 'mcptoml', '--with-engine', '--write'], p);
  assert.match(r.out, /already defines MCP servers/);
  assert.match(r.out, /command = "hullproof"/);
  assert.equal(read(p, '.mcptoml/config.toml'), mine);
});

test('a tool that cannot run the engine says so and writes no MCP file', () => {
  const p = tmp();
  const r = runEngine(['--tool', 'chattool', '--with-engine', '--write'], p);
  assert.equal(r.code, 0);
  assert.match(r.out, /cannot run the engine, so its audit is prompt based/);
  assert.match(r.out, /paste \.hullproof\/ci\/report\.md/);
  assert.deepEqual(fs.readdirSync(p).sort(), ['chattool-rules.md']);
});

test('the PATH report names the hullproof command when it is found, and warns when it is inside the project', () => {
  const bin = tmp();
  fs.writeFileSync(path.join(bin, 'hullproof'), '#!/bin/sh\n', { mode: 0o755 });
  const r = runEngine(['--tool', 'mcpjson', '--with-engine'], tmp(), bin);
  assert.match(r.out, /on your PATH at/);
  const inside = tmp();
  fs.mkdirSync(path.join(inside, 'bin'));
  fs.writeFileSync(path.join(inside, 'bin/hullproof'), '#!/bin/sh\n', { mode: 0o755 });
  const w = runEngine(['--tool', 'mcpjson', '--with-engine'], inside, path.join(inside, 'bin'));
  assert.match(w.out, /inside this project/);
});

test('a bad engine block in TOOL.json is reported', () => {
  const k = tmp();
  fs.cpSync(kit, k, { recursive: true });
  const f = path.join(k, 'editors/mcpjson/TOOL.json');
  const d = JSON.parse(fs.readFileSync(f, 'utf8'));
  d.engine.mcp.merge = 'yaml';
  fs.writeFileSync(f, JSON.stringify(d));
  const r = spawnSync(process.execPath, [script, '--kit', k, '--tool', 'mcpjson', '--project', tmp()], { encoding: 'utf8' });
  assert.equal(r.status, 1);
  assert.match(r.stdout + r.stderr, /engine\.mcp\.merge must be json or toml/);
});

test('MCP settings that share a file with the tool settings are merged into one write, nothing is lost', () => {
  const p = tmp();
  const r = runEngine(['--tool', 'sharedmcp', '--with-engine', '--write'], p);
  assert.equal(r.code, 0);
  const got = JSON.parse(read(p, '.shared/settings.json'));
  assert.deepEqual(got.hooks, { x: [1] });
  assert.deepEqual(got.mcpServers, MCP_JSON.mcpServers);
  assert.equal(runEngine(['--tool', 'sharedmcp', '--with-engine', '--write'], p).code, 2);
});

test('the count of files written is reported once per file', () => {
  const p = tmp();
  const r = runEngine(['--tool', 'mcpjson', '--with-engine', '--write'], p);
  assert.match(r.out, /Done\. 2 files written/);
});
