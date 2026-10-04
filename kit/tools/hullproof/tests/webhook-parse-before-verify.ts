export async function bad(req: Request) {
  // ruleid: hullproof-webhook-parse-before-verify
  const body = await req.json();
  const event = stripe.webhooks.constructEvent(JSON.stringify(body), sig, secret);
  return event;
}

export async function good(req: Request) {
  // ok: hullproof-webhook-parse-before-verify
  const raw = await req.text();
  const event = stripe.webhooks.constructEvent(raw, sig, secret);
  return JSON.parse(raw);
}

export async function unrelated(req: Request) {
  // ok: hullproof-webhook-parse-before-verify
  const body = await req.json();
  return save(body);
}
