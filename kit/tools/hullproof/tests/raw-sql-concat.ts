import { sql } from 'drizzle-orm';
declare const pool: any; declare const knex: any; declare const prisma: any;

export async function bad(db: any, id: string) {
  // ruleid: hullproof-raw-sql-concat, hullproof-sql-string-built-in-variable
  await db.query(`SELECT * FROM users WHERE id = '${id}'`);
  // ruleid: hullproof-raw-sql-concat
  await db.query("SELECT * FROM users WHERE id = '" + id + "'");
  // ruleid: hullproof-raw-sql-concat
  await pool.query('SELECT * FROM t WHERE n = '.concat(id));
  // ruleid: hullproof-raw-sql-concat
  await pool.query(['SELECT * FROM t WHERE n =', id].join(' '));
  // ruleid: hullproof-raw-sql-concat
  await knex.whereRaw("n = '" + id + "'");
  // ruleid: hullproof-raw-sql-concat, hullproof-sql-string-built-in-variable
  await prisma.$queryRawUnsafe(`SELECT * FROM t WHERE n = ${id}`);
}

export async function good(db: any, sql: any, id: string) {
  // ok: hullproof-raw-sql-concat
  await db.query("SELECT * FROM users WHERE id = $1", [id]);
  // ok: hullproof-raw-sql-concat
  await sql`SELECT * FROM users WHERE id = ${id}`;
  // ok: hullproof-raw-sql-concat
  await prisma.$queryRaw`SELECT * FROM t WHERE n = ${id}`;
  // ok: hullproof-raw-sql-concat
  await pool.query("SELECT 1");
}

export function builtInVariable(id: string) {
  // ruleid: hullproof-sql-string-built-in-variable
  const q = `SELECT name FROM users WHERE id = ${id}`;
  return q;
}

export function notSql(id: string) {
  // ok: hullproof-sql-string-built-in-variable
  const label = `User ${id} selected from the list`;
  return label;
}
