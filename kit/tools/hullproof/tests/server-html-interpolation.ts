declare function escapeHtml(s: string): string;
declare function sanitizeName(s: string): string;
declare function html(strings: TemplateStringsArray, ...v: unknown[]): string;

export function welcomeEmail(name: string) {
  // ruleid: hullproof-server-html-interpolation
  return `<p>Hello ${name}, welcome.</p>`;
}

export function interpolationBeforeTag(name: string) {
  // ruleid: hullproof-server-html-interpolation
  return `${name}<br>`;
}

export function trimOnlyWrapper(name: string) {
  // ruleid: hullproof-server-html-interpolation
  return `<p>Hello ${sanitizeName(name)}</p>`;
}

export function closingTagOnly(name: string) {
  // ruleid: hullproof-server-html-interpolation
  return `${name}</td>`;
}

export function safeEmail(name: string) {
  // ok: hullproof-server-html-interpolation
  return `<p>Hello ${escapeHtml(name)}, welcome.</p>`;
}

export function plain(name: string) {
  // ok: hullproof-server-html-interpolation
  return `Hello ${name}`;
}

export function taggedTemplate(name: string) {
  // ok: hullproof-server-html-interpolation
  return html`<p>Hello ${name}</p>`;
}

export function noInterpolation() {
  // ok: hullproof-server-html-interpolation
  return `<p>Hello there</p>`;
}

export function comparison(a: number, b: number) {
  // ok: hullproof-server-html-interpolation
  return `the check ${a} < ${b} failed`;
}
