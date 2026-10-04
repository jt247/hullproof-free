declare function escapeHtml(s: string): string;
declare const res: any; declare const c: any;
declare function render(): string;
declare class NextResponse { constructor(body: string, init?: any); }

export function concat(name: string) {
  // ruleid: hullproof-html-concat
  return '<p>Hello ' + name + '</p>';
}

export function concatLeading(name: string) {
  // ruleid: hullproof-html-concat
  return name + '<br>';
}

export function concatEscaped(name: string) {
  // ok: hullproof-html-concat
  return '<p>Hello ' + escapeHtml(name) + '</p>';
}

export function concatNoHtml(name: string) {
  // ok: hullproof-html-concat
  return 'Hello ' + name;
}

export function concatComparison(a: number) {
  // ok: hullproof-html-concat
  return 'value <' + a;
}

export function responseBody(name: string) {
  // ruleid: hullproof-html-response-body
  return new Response(render(), { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

export function nextResponseBody(body: string) {
  // ruleid: hullproof-html-response-body
  return new NextResponse(body, { headers: { "Content-Type": "text/html" } });
}

export function expressBody(body: string) {
  // ruleid: hullproof-html-response-body
  res.type("html").send(body);
}

export function honoBody(body: string) {
  // ruleid: hullproof-html-response-body
  return c.html(body);
}

export function jsonBody(body: string) {
  // ok: hullproof-html-response-body
  return new Response(JSON.stringify({ a: body }), { headers: { "Content-Type": "application/json" } });
}

export function staticHtml() {
  // ok: hullproof-html-response-body
  return new Response("<h1>Not found</h1>", { headers: { "Content-Type": "text/html" } });
}

