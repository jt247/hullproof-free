declare const server: any; declare const z: any; declare function tool(o: any): any;
declare function createAdminClient(): any; declare function createUserClient(t: string): any;
declare const supabaseAdmin: any; declare const CallToolRequestSchema: any;

server.tool("list_orders", { status: z.string() }, async (args: any) => {
  // ruleid: hullproof-tool-handler-admin-client-no-scope
  const db = createAdminClient();
  return db.from("orders").select("*").eq("status", args.status);
});

server.tool("delete_user", { id: z.string() }, async (args: any) => {
  // ruleid: hullproof-tool-handler-admin-client-no-scope
  return supabaseAdmin.auth.admin.deleteUser(args.id);
});

server.tool("ping_db", {}, async () => {
  // ruleid: hullproof-tool-handler-admin-client-no-scope
  const db = createAdminClient();
  return db.from("health").select("*");
});

server.registerTool("export_all", { description: "x" }, async (args: any) => {
  // ruleid: hullproof-tool-handler-admin-client-no-scope
  const db = createAdminClient();
  return db.from("orders").select("*");
});

const exportTool = tool({
  description: "export",
  execute: async (args: any) => {
    // ruleid: hullproof-tool-handler-admin-client-no-scope
    const db = createAdminClient();
    return db.from("orders").select("*");
  },
});

server.setRequestHandler(CallToolRequestSchema, async (request: any) => {
  // ruleid: hullproof-tool-handler-admin-client-no-scope
  const db = createAdminClient();
  return db.from("orders").select("*");
});

server.tool("read_profile", { id: z.string() }, async (args: any, extra: any) => {
  // ok: hullproof-tool-handler-admin-client-no-scope
  const db = createUserClient(extra.authInfo.token);
  return db.from("profiles").select("*");
});

server.tool("read_note", { id: z.string() }, async (args: any, extra: any) => {
  // ok: hullproof-tool-handler-admin-client-no-scope
  const db = createAdminClient();
  return db.from("notes").select("*").eq("owner_id", extra.authInfo.userId);
});

server.tool("ping", {}, async () => {
  // ok: hullproof-tool-handler-admin-client-no-scope
  return { content: [{ type: "text", text: "pong" }] };
});

function notATool() {
  // ok: hullproof-tool-handler-admin-client-no-scope
  return createAdminClient();
}

export function createServerFor(user: { id: string }) {
  const s: any = {};
  s.tool("mine", {}, async (args: any) => {
    // ok: hullproof-tool-handler-admin-client-no-scope
    const db = createAdminClient();
    return db.from("orders").select("*").eq("owner_id", user.id);
  });
  return s;
}
