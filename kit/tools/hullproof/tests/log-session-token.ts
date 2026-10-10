export async function handler(req: Request, session: any) {
  // ruleid: hullproof-log-session-token
  console.log("session", session.access_token);

  // ruleid: hullproof-log-session-token
  console.info(`auth header ${req.headers.get("authorization")}`);

  // ruleid: hullproof-log-session-token
  logger.debug({ authorization });

  // ruleid: hullproof-log-session-token
  console.log(session);

  // ruleid: hullproof-log-session-token
  console.error("failed", token);

  // ruleid: hullproof-log-session-token
  console.log(req.headers);

  // ok: hullproof-log-session-token
  console.log("user signed in", session.user.id);

  // ok: hullproof-log-session-token
  console.log("tokens used", tokenCount);

  // ok: hullproof-log-session-token
  console.log("session token expired");

  // ok: hullproof-log-session-token
  logger.info({ requestId, route: "/api/orders" });
}
