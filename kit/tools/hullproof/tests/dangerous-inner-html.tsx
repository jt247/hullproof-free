export function Bad({ html }: { html: string }) {
  // ruleid: hullproof-dangerous-inner-html
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}

export function Literal() {
  // ok: hullproof-dangerous-inner-html
  return <div dangerouslySetInnerHTML={{ __html: "<b>static</b>" }} />;
}

export function Clean({ html }: { html: string }) {
  // ok: hullproof-dangerous-inner-html
  return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />;
}

export function dom(el: HTMLElement, v: string) {
  // ruleid: hullproof-dangerous-inner-html
  el.innerHTML = v;
}

export function Frame({ doc }: { doc: string }) {
  // ruleid: hullproof-dangerous-inner-html
  return <iframe srcDoc={doc} />;
}

export function FrameOk() {
  // ok: hullproof-dangerous-inner-html
  return <iframe srcDoc={"<p>fixed</p>"} />;
}

export function sinks(el: HTMLElement, v: string, range: Range) {
  // ruleid: hullproof-dangerous-inner-html
  el.outerHTML = v;
  // ruleid: hullproof-dangerous-inner-html
  el.insertAdjacentHTML("beforeend", v);
  // ruleid: hullproof-dangerous-inner-html
  document.write(v);
  // ruleid: hullproof-dangerous-inner-html
  document.writeln(v);
  // ruleid: hullproof-dangerous-inner-html
  range.createContextualFragment(v);
  // ruleid: hullproof-dangerous-inner-html
  el.innerHTML += v;
  // ok: hullproof-dangerous-inner-html
  el.innerHTML = DOMPurify.sanitize(v);
  // ok: hullproof-dangerous-inner-html
  el.textContent = v;
}
