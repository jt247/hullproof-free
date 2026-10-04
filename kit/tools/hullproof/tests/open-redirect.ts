export function bad(req: any, res: any) {
  // ruleid: hullproof-open-redirect
  res.redirect(req.query.next);
}

export function badNext(request: any) {
  const next = request.nextUrl.searchParams.get("next");
  // ruleid: hullproof-open-redirect
  return NextResponse.redirect(next);
}

export function good(req: any, res: any) {
  const target = safeRedirectPath(req.query.next);
  // ok: hullproof-open-redirect
  res.redirect(target);
}

export function fixed(res: any) {
  // ok: hullproof-open-redirect
  res.redirect("/dashboard");
}
