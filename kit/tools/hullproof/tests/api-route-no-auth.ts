// ruleid: hullproof-api-route-no-auth
export async function GET(req: Request) {
  const rows = await supabase.from("orders").select("*");
  return Response.json(rows);
}

// ruleid: hullproof-api-route-no-auth
export const POST = async (req: Request) => {
  const body = await req.json();
  const row = await prisma.invoice.findMany({ where: { status: body.status } });
  return Response.json(row);
};

// ok: hullproof-api-route-no-auth
export async function PUT(req: Request) {
  const { data } = await supabase.auth.getUser();
  if (!data.user) return new Response("unauthorized", { status: 401 });
  const rows = await supabase.from("orders").select("*");
  return Response.json(rows);
}

// ok: hullproof-api-route-no-auth
export async function PATCH(req: Request) {
  const session = await getServerSession(authOptions);
  if (!session) return new Response("unauthorized", { status: 401 });
  const rows = await db.query("select 1");
  return Response.json(rows);
}

// ok: hullproof-api-route-no-auth
export async function DELETE(req: Request) {
  return Response.json({ ok: true });
}

// A helper that is not a route handler is not checked.
// ok: hullproof-api-route-no-auth
export async function loadOrders() {
  return supabase.from("orders").select("*");
}
