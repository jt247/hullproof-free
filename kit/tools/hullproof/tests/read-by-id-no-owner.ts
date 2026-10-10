export async function a(id: string) {
  // ruleid: hullproof-read-by-id-no-owner
  const { data } = await supabase.from("orders").select("*").eq("id", id).single();
  return data;
}
export async function b(id: string, user: any) {
  // ok: hullproof-read-by-id-no-owner
  const { data } = await supabase.from("orders").select("*").eq("id", id).eq("user_id", user.id).single();
  return data;
}
export async function c(id: string) {
  // ruleid: hullproof-read-by-id-no-owner
  return prisma.order.findUnique({ where: { id } });
}
export async function d(id: string, user: any) {
  // ok: hullproof-read-by-id-no-owner
  return prisma.order.findFirst({ where: { id, userId: user.id } });
}
export async function e(id: string) {
  // ruleid: hullproof-read-by-id-no-owner
  return db.select().from(orders).where(eq(orders.id, id));
}
export async function f(id: string, user: any) {
  // ok: hullproof-read-by-id-no-owner
  return db.select().from(orders).where(and(eq(orders.id, id), eq(orders.userId, user.id)));
}
export async function g(session: any) {
  // ok: hullproof-read-by-id-no-owner
  return prisma.user.findUnique({ where: { id: session.user.id } });
}
