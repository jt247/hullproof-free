import { sql } from 'drizzle-orm';
declare const db: any; declare const pool: any; declare const pgp: any; declare const knex: any;
declare const prisma: any; declare const Prisma: any; declare const column: string;

export function rawHelpers(input: string) {
  // ruleid: hullproof-sql-raw-non-literal
  sql.raw(input);
  // ruleid: hullproof-sql-raw-non-literal
  knex.orderByRaw(column);
  // ruleid: hullproof-sql-raw-non-literal
  Prisma.raw(input);
  // ok: hullproof-sql-raw-non-literal
  sql.raw("now()");
  // ok: hullproof-sql-raw-non-literal
  knex.whereRaw("a = b");
}

export function taggedMisuse(name: string) {
  // ruleid: hullproof-sql-tagged-template-misuse
  sql(`SELECT * FROM t WHERE n = ${name}`);
  // ruleid: hullproof-sql-tagged-template-misuse
  prisma.$queryRaw(`SELECT * FROM t WHERE n = ${name}`);
  // ruleid: hullproof-sql-tagged-template-misuse, hullproof-sql-raw-non-literal
  sql`SELECT * FROM t WHERE n = ${sql.raw(name)}`;
  // ok: hullproof-sql-tagged-template-misuse
  sql`SELECT * FROM t WHERE n = ${name}`;
  // ok: hullproof-sql-tagged-template-misuse
  prisma.$queryRaw`SELECT * FROM t WHERE n = ${name}`;
}

export function viaVariable(input: string) {
  const q = ['SELECT * FROM t WHERE n =', input].join(' ');
  // ruleid: hullproof-sql-built-string-reaches-query
  return pool.query(q);
}

export function viaConcatVariable(input: string) {
  const q = "select * from t where a = " + input;
  // ruleid: hullproof-sql-built-string-reaches-query
  return pool.query(q);
}

export function viaOtherMethods(input: string) {
  // ruleid: hullproof-sql-built-string-reaches-query
  return db.prepare(`SELECT * FROM t WHERE n = '${input}'`).all();
}

export function viaPgp(input: string) {
  // ruleid: hullproof-sql-built-string-reaches-query
  return pgp.any(`SELECT * FROM t WHERE n = '${input}'`);
}

export function execLike(input: string) {
  // ruleid: hullproof-sql-built-string-reaches-query
  return db.exec(`UPDATE t SET a = 1 WHERE n = '${input}'`);
}

export function safeAmbiguous(key: string, map: Map<string, string>) {
  // ok: hullproof-sql-built-string-reaches-query
  return map.get(`user:${key}`);
}

export function safeParameterised(name: string) {
  // ok: hullproof-sql-built-string-reaches-query
  return db.prepare('SELECT * FROM t WHERE n = ?').all(name);
}

declare const z: any; declare const express: any; declare const sequelize: any;
export function notSql(n: number) {
  // ok: hullproof-sql-raw-non-literal
  const phase = z.literal(n);
  // ok: hullproof-sql-raw-non-literal
  const parser = express.raw({ type: 'application/json' });
  // ruleid: hullproof-sql-raw-non-literal
  return sequelize.literal(String(n));
}
