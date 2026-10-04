// Held out variants. They were written in shapes that differ from the core variants, then run once
// against the rules before any tuning, so the first run result is an estimate of how the rules do on
// code they were not shaped around. Known gaps are marked expect-miss. Nothing here is product code.
import { exec, execFile, execFileSync, execSync, spawn } from 'child_process';
import * as child_process from 'child_process';
import vm from 'node:vm';
import path from 'node:path';
import { createHmac } from 'crypto';
import axios from 'axios';
import got from 'got';
import http from 'node:http';
import ejs from 'ejs';
import pug from 'pug';
import Handlebars from 'handlebars';
import { createClient } from '@supabase/supabase-js';
declare const client: any; declare const sequelize: any; declare const prisma: any; declare const knex: any; declare const db: any;
declare const sql: any; declare const req: any; declare const request: any; declare const res: any; declare const searchParams: URLSearchParams;
declare const supabase: any; declare const server: any; declare const server2: any;
declare const email: string; declare const id: string; declare const amount: string; declare const msg: string;
declare const table: string; declare const sort: string; declare const a: string; declare const expr: string;
declare const code: string; declare const name: string; declare const dir: string; declare const file: string;
declare const out: string; declare const repoUrl: string; declare const cmd: string; declare const ref: string;
declare const tpl: string; declare const title: string; declare const html: string; declare const url: string;
declare const base: string; declare const filters: string[]; declare const sortBy: string; declare const col: string;
declare const term: string; declare const uid: string; declare const fields: string; declare const secret: string | undefined;
declare const sig: string; declare const body2: string; declare const items: string[];
declare function format(t: string, ...a: unknown[]): string;
declare function createAdminClient(): any;
declare class Webhook { constructor(s: string); }

// variant: sql-1
export const hs1 = () => client.query("SELECT * FROM t WHERE id = " + req.params.id);
// variant: sql-2
export const hs2 = () => sequelize.query(`SELECT * FROM users WHERE email = '${email}'`);
// variant: sql-3
export const hs3 = () => prisma.$executeRawUnsafe("DELETE FROM t WHERE id = " + id);
// variant: sql-4
export const hs4 = () => knex.raw("SELECT * FROM t WHERE a = '" + a + "'");
// variant: sql-5
export const hs5 = async () => { const stmt = "UPDATE accounts SET balance = " + amount; await db.execute(stmt); };
// variant: sql-6
export const hs6 = () => db.query(`INSERT INTO log(msg) VALUES ('${msg}')`);
// variant: sql-7
export const hs7 = () => sql.unsafe(`SELECT * FROM ${table}`);
// variant: sql-8
export const hs8 = () => knex('t').orderByRaw(sort);
// variant: sql-9 expect-miss
export const hs9 = () => { const q = format('SELECT * FROM t WHERE a = %s', a); return client.query(q); };

// variant: eval-1
export const he1 = () => new Function('return ' + expr)();
// variant: eval-2
export const he2 = () => vm.runInNewContext(code, {});
// variant: eval-3
export const he3 = () => eval(`(${expr})`);
// variant: eval-4
export const he4 = () => require(path.join(dir, name));
// variant: eval-5
export const he5 = () => ejs.render(tpl, {});
// variant: eval-6
export const he6 = () => Handlebars.compile(tpl);
// variant: eval-7
export const he7 = () => pug.compile(tpl);
// variant: eval-8
export const he8 = () => Function.prototype.constructor('return process')();
// variant: eval-9 expect-miss
export const he9 = () => import(`../${name}`);
// variant: eval-10 expect-miss
export const he10 = (fn: any) => { setInterval(fn, 1000); };

// variant: html-1
export const hh1 = () => res.send('<h1>' + title + '</h1>');
// variant: html-2
export const hh2 = () => res.send(`<div>${msg}</div>`);
// variant: html-3
export const hh3 = (el: HTMLElement) => { el.innerHTML = msg; };
// variant: html-4
export const hh4 = () => { document.write('<p>' + msg + '</p>'); };
// variant: html-5
export const hh5 = () => new Response(html, { headers: { 'Content-Type': 'text/html' } });
// variant: html-6
export const hh6 = () => `<a href="${url}">link</a>`;
// variant: html-7
export const hh7 = () => `<tr><td>${name}</td></tr>`;
// variant: html-8
export const hh8 = () => { let h = ''; for (const i of items) { h = h + '<li>' + i + '</li>'; } return h; };
// variant: html-9
export const hh9 = () => { let h = ''; for (const i of items) { h += `<li>${i}</li>`; } return h; };
// variant: html-10
export const hh10 = () => '<b>' + name.trim() + '</b>';
// variant: html-11 expect-miss
export const hh11 = () => [`<ul>`, ...items.map((i) => `<li>`.concat(i, `</li>`)), `</ul>`].join('');

// variant: postgrest-1
export const hp1 = () => supabase.from('t').select('*').or(`id.eq.${id},owner.eq.${uid}`);
// variant: postgrest-2
export const hp2 = () => supabase.from('t').select('*').or(filters.join(','));
// variant: postgrest-3
export const hp3 = () => supabase.from('t').select('*').order(sortBy);
// variant: postgrest-4
export const hp4 = () => supabase.from('t').select('*').filter(`${col}`, 'ilike', term);
// variant: postgrest-5
export const hp5 = () => supabase.from('t').select(fields);
// variant: postgrest-6
export const hp6 = () => supabase.from('t').select('*').textSearch(col, term);
// variant: postgrest-7 expect-miss
export const hp7 = (q: any) => q.match(JSON.parse(term));

// variant: subprocess-1
export const hc1 = () => spawn('ffmpeg', ['-i', file, out]);
// variant: subprocess-2
export const hc2 = () => execSync(`tar -xf ${file}`);
// variant: subprocess-3
export const hc3 = () => execFileSync('convert', [file, out]);
// variant: subprocess-4
export const hc4 = () => spawn(cmd, [], { shell: true });
// variant: subprocess-5
export const hc5 = () => exec('rm -rf ' + dir);
// variant: subprocess-6
export const hc6 = () => child_process.exec(cmd);
// variant: subprocess-7
export const hc7 = () => execFile('/bin/sh', ['-c', cmd]);
// variant: subprocess-8
export const hc8 = async () => { const o = child_process.execSync(`git log ${ref}`); return o; };
// variant: subprocess-9 expect-miss
export const hc9 = (args: string[]) => execFile('git', args);

// variant: outbound-1
export const ho1 = () => fetch(req.body.url);
// variant: outbound-2
export const ho2 = () => axios.get(searchParams.get('u')!);
// variant: outbound-3
export const ho3 = () => fetch(`http://${req.query.host}/`);
// variant: outbound-4
export const ho4 = () => new URL(req.query.next, base);
// variant: outbound-5
export const ho5 = () => got(request.nextUrl.searchParams.get('target')!);
// variant: outbound-6
export const ho6 = async () => { const body = await req.json(); return fetch(body.webhookUrl); };
// variant: outbound-7 expect-miss
export const ho7 = (target: string) => fetch(target);
// variant: outbound-8 expect-miss
export const ho8 = (target: string) => http.get(target);

// variant: webhook-1
export const hw1 = () => createHmac('sha256', process.env.PAYMENTS_HOOK_SECRET || '').update(body2).digest('hex');
// variant: webhook-2
export const hw2 = () => sig !== process.env.WEBHOOK_SECRET;
// variant: webhook-3
export const hw3 = () => new Webhook(process.env.SVIX_SIGNING_SECRET ?? '');
// variant: webhook-4 expect-miss
export const hw4 = () => { if (!secret) { return true; } return false; };

// variant: tool-1
server.tool('a', {}, async (args: any) => { const c = createClient('http://x', process.env.SUPABASE_SERVICE_ROLE_KEY!); return c.from('t').select('*'); });
// variant: tool-2
server.tool('b', {}, async (args: any) => { return createAdminClient().from('t').delete().eq('id', args.id); });
// variant: tool-3 expect-miss
server2.tool('c', {}, async (args: any, extra: any) => { return createAdminClient().from('t').delete().eq('id', args.id); });
