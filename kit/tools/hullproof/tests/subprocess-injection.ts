import { execFile, exec, execSync, spawn } from 'child_process';
import * as cp from 'child_process';
import { promisify } from 'util';
declare const input: string; declare const url: string; declare const userArgs: string[];
const execAsync = promisify(exec);

export function shellStrings(cmd: string, name: string) {
  // ruleid: hullproof-subprocess-shell-string
  exec(cmd);
  // ruleid: hullproof-subprocess-shell-string
  exec(`convert ${name} out.png`);
  // ruleid: hullproof-subprocess-shell-string
  execSync("git log " + name);
  // ruleid: hullproof-subprocess-shell-string
  cp.exec(cmd, (err) => {});
  // ruleid: hullproof-subprocess-shell-string
  execAsync(cmd);
  // ruleid: hullproof-subprocess-shell-string
  spawn(cmd, [], { shell: true });
  // ok: hullproof-subprocess-shell-string
  exec("ls -la");
  // ok: hullproof-subprocess-shell-string
  execSync("git status");
  // ok: hullproof-subprocess-shell-string
  /ab(c)/.exec(name);
  // ok: hullproof-subprocess-shell-string
  execFile("git", ["status"]);
}

export function shellInterpreter(cmd: string) {
  // ruleid: hullproof-subprocess-shell-interpreter
  execFile('sh', ['-c', cmd]);
  // ruleid: hullproof-subprocess-shell-interpreter
  spawn('/bin/bash', ['-c', `echo ${cmd}`]);
  // ruleid: hullproof-subprocess-shell-interpreter
  execFile('cmd.exe', ['/c', cmd]);
  // ok: hullproof-subprocess-shell-interpreter
  execFile('sh', ['-c', 'echo hi']);
  // ok: hullproof-subprocess-shell-interpreter
  execFile('sh', ['script.sh']);
}

export function optionInjection(name: string) {
  // ruleid: hullproof-subprocess-arg-no-separator
  execFile('git', ['ls-remote', url]);
  // ruleid: hullproof-subprocess-arg-no-separator
  spawn('curl', ['-s', url]);
  // ruleid: hullproof-subprocess-arg-no-separator
  execFile('tar', ['-xf', name]);
  // ok: hullproof-subprocess-arg-no-separator
  execFile('git', ['ls-remote', '--', url]);
  // ok: hullproof-subprocess-arg-no-separator
  execFile('git', ['status', '--short']);
}

export async function taintExamples(request: Request, req: any) {
  const { repo } = await request.json();
  // ruleid: hullproof-subprocess-request-data, hullproof-subprocess-arg-no-separator
  execFile('git', ['ls-remote', repo]);
  // ruleid: hullproof-subprocess-request-data, hullproof-subprocess-shell-string
  exec(req.query.cmd);
  // ruleid: hullproof-subprocess-request-data, hullproof-subprocess-shell-string
  exec(`ls ${req.body.dir}`);
  // ok: hullproof-subprocess-request-data
  execFile('git', ['status']);
  // ok: hullproof-subprocess-request-data
  execFile('sleep', ['--', String(Number(req.query.seconds))]);
}
