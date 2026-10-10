export async function resultThrownAway(req: Request) {
  const body = await req.text();
  // ruleid: hullproof-verify-result-unused
  verifySignature(body, sig, secret);
  return handle(body);
}

export async function resultAwaitedAndDropped(req: Request) {
  // ruleid: hullproof-verify-result-unused
  await crypto.timingSafeEqual(a, b);
  return handle();
}

export async function resultStoredNeverRead(req: Request) {
  const body = await req.text();
  // ruleid: hullproof-verify-result-unused
  const ok = verifySignature(body, sig, secret);
  console.log("checked");
  return handle(body);
}

export async function resultStoredOnlyAssigned(req: Request) {
  // ruleid: hullproof-verify-result-unused
  const valid = isValidSignature(body, sig);
  return handle(body);
}

export async function rejectsOnFalse(req: Request) {
  const body = await req.text();
  // ok: hullproof-verify-result-unused
  const ok = verifySignature(body, sig, secret);
  if (!ok) return new Response("invalid", { status: 401 });
  return handle(body);
}

export async function rejectsInsideTry(req: Request) {
  // ok: hullproof-verify-result-unused
  const ok = isValidSignature(body, sig);
  try {
    if (!ok) {
      throw new Error("invalid signature");
    }
  } catch (e) {
    return new Response("invalid", { status: 401 });
  }
  return handle(body);
}

export async function usesResultInReturn(req: Request) {
  // ok: hullproof-verify-result-unused
  const ok = await crypto.timingSafeEqual(a, b);
  return ok ? handle() : deny();
}

export async function throwsByItself(req: Request) {
  // ok: hullproof-verify-result-unused
  stripe.webhooks.constructEvent(body, sig, secret);
  return handle(body);
}
