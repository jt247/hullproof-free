export function reflectDirect(req: any, res: any) {
  // ruleid: hullproof-cors-reflect-origin
  res.setHeader("Access-Control-Allow-Origin", req.headers.origin);
}

export function reflectVariable(request: Request) {
  const origin = request.headers.get("origin");
  // ruleid: hullproof-cors-reflect-origin
  return new Response("x", { headers: { "Access-Control-Allow-Origin": origin } });
}

export function allowlisted(req: any, res: any) {
  const origin = req.headers.origin;
  if (ALLOWED.includes(origin)) {
    // ok: hullproof-cors-reflect-origin
    res.setHeader("Access-Control-Allow-Origin", origin);
  }
}

export function fixed(res: any) {
  // ok: hullproof-cors-reflect-origin
  res.setHeader("Access-Control-Allow-Origin", "https://app.example.com");
}

// ruleid: hullproof-cors-origin-true
app.use(cors({ origin: true }));

// ok: hullproof-cors-origin-true
app.use(cors({ origin: ["https://app.example.com"] }));
