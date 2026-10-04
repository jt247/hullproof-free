// No top level directive, so exports are ordinary functions.
// ok: hullproof-server-action-no-auth
export async function helper(id: string) {
  await db.delete(id);
}
