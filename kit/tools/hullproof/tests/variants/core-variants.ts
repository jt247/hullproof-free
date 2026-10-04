// Synthetic injectable code. Every block marked "variant:" is a known bad pattern that a
// scanner should flag. These are 33 variants (26 in the
// sql, eval and html families, plus 7 in the postgrest, subprocess and outbound families).
// Run tests/test_variant_catch.py to measure the catch rate. Nothing here is product code.
import { execFile, exec } from 'child_process';
import { sql } from 'drizzle-orm';
import { evaluate } from 'mathjs';
import vm from 'node:vm';
import _ from 'lodash';
import { createClient } from '@supabase/supabase-js';
declare const db: any; declare const pool: any; declare const input: string; declare const pgp: any; declare const knex: any;
declare function sanitizeName(s: string): string;
const supabase = createClient('http://x', 'y');
const BASE = 'https://api.provider.example';

// variant: sql-1
export const s1 = () => db.prepare(`SELECT * FROM t WHERE n = '${input}'`).all();
// variant: sql-2
export const s2 = () => sql.raw(input);
// variant: sql-3
export const s3 = () => pool.query('SELECT * FROM t WHERE n = '.concat(input));
// variant: sql-4
export const s4 = () => { const q = ['SELECT * FROM t WHERE n =', input].join(' '); return pool.query(q); }
// variant: sql-5
export const s5 = () => pgp.any(`SELECT * FROM t WHERE n = '${input}'`);
// variant: sql-6
export const s6 = () => db.exec(`UPDATE t SET a = 1 WHERE n = '${input}'`);
// variant: sql-7
export const s7 = () => knex.whereRaw(`n = '${input}'`);
// variant: sql-8
export const s8 = () => pool.query(`SELECT * FROM t WHERE n = '${input}'`);

// variant: eval-1
export const e1 = () => (0, eval)(input);
// variant: eval-2
export const e2 = () => globalThis.eval(input);
// variant: eval-3
export const e3 = () => new vm.Script(input).runInThisContext();
// variant: eval-4
export const e4 = () => evaluate(input);
// variant: eval-5
export const e5 = () => import(input);
// variant: eval-6
export const e6 = () => _.template(input)({});
// variant: eval-7
export const e7 = () => setTimeout(input as any, 0);
// variant: eval-8
export const e8 = () => eval(input);
// variant: eval-9
export const e9 = () => vm.compileFunction(input);

// variant: html-1
export const h1 = (name: string) => `<p>Hello</p>${name}`;
// variant: html-2
export const h2 = (name: string) => '<p>Hello ' + name + '</p>';
// variant: html-3
export const h3 = (name: string) => `<p>Hello ${sanitizeName(name)}</p>`;
// variant: html-4
export const h4 = (name: string) => `${name}<br>`;
// variant: html-5 expect-miss
const open = '<div>'; const close = '</div>';
export const h5 = (name: string) => `${open}${name}${close}`;
// variant: html-6
export const h6 = (name: string) => `<p>Hello ${name}</p>`;
// variant: html-7
export const svg = (name: string) => `<svg xmlns="http://www.w3.org/2000/svg"><text>${name}</text></svg>`;
// variant: html-8
export const h7 = (name: string) => ['<ul>', `<li>${name}</li>`].join('');
// variant: html-9
export const h8 = (name: string) => `<p>Hi ${String(name).replace(/\n/g, '<br>')}</p>`;

// variant: postgrest-1
export async function search(q: string) {
  return supabase.from('items').select('id,name').or(`name.ilike.%${q}%,description.ilike.%${q}%`);
}
// variant: postgrest-2
export async function search2(col: string, v: string) {
  return supabase.from('items').select('id').filter(col, 'eq', v);
}

// variant: subprocess-1
export function clone(url: string) { execFile('git', ['ls-remote', url]); }
// variant: subprocess-2
export function viaSh(cmd: string) { execFile('sh', ['-c', cmd]); }
// variant: subprocess-3
export function destructured(cmd: string) { exec(cmd); }

// variant: outbound-1 expect-miss
export async function getCust(id: string) {
  return fetch(`${BASE}/v1/customers/${id}`);
}
// variant: outbound-2
export async function getPath(p: string) {
  return fetch(BASE + p);
}
