import axios from 'axios';
declare function assertPublicUrl(u: string): Promise<void>;
declare function safeFetch(u: string): Promise<Response>;
declare const BASE: string; declare const API_BASE: string;

export async function direct(request: Request) {
  const { url } = await request.json();
  // ruleid: hullproof-ssrf-request-data-to-url
  return fetch(url);
}

export async function viaSearchParams(request: Request) {
  const target = new URL(request.url).searchParams.get('u');
  // ruleid: hullproof-ssrf-request-data-to-url
  return axios.get(target!);
}

export async function viaReqBody(req: any) {
  // ruleid: hullproof-ssrf-request-data-to-url
  return fetch(req.body.callbackUrl);
}

export async function viaTemplate(req: any) {
  // ruleid: hullproof-ssrf-request-data-to-url
  return fetch(`https://${req.query.host}/hook`);
}

export async function urlBaseOverride(req: any) {
  // ruleid: hullproof-ssrf-request-data-to-url
  const u = new URL(req.query.path, 'https://api.example.com');
  return u;
}

export async function guarded(request: Request) {
  const { url } = await request.json();
  await assertPublicUrl(url);
  // ok: hullproof-ssrf-request-data-to-url
  return fetch(url);
}

export async function guardedWrapper(request: Request) {
  const { url } = await request.json();
  // ok: hullproof-ssrf-request-data-to-url
  return safeFetch(url);
}

export async function pathEncoded(req: any) {
  // ok: hullproof-ssrf-request-data-to-url
  return fetch(`https://api.example.com/v1/items/${encodeURIComponent(req.params.id)}`);
}

export async function numeric(req: any) {
  // ok: hullproof-ssrf-request-data-to-url
  return fetch(`https://api.example.com/v1/items/${Number(req.params.id)}`);
}

export async function constantUrl() {
  // ok: hullproof-ssrf-request-data-to-url
  return fetch('https://api.example.com/status');
}

export async function concatenated(id: string) {
  // ruleid: hullproof-ssrf-url-built-from-base
  return fetch(BASE + id);
}

export async function concatenatedEncoded(id: string) {
  // ok: hullproof-ssrf-url-built-from-base
  return fetch(API_BASE + encodeURIComponent(id));
}

export async function concatenatedConstant() {
  // ok: hullproof-ssrf-url-built-from-base
  return fetch(API_BASE + '/status');
}

export async function responseIsNotRequestData(req: any) {
  const first = await fetch('https://api.example.com/items', { method: 'POST', body: JSON.stringify(req.body) });
  const created = (await first.json()) as { id?: string };
  // ok: hullproof-ssrf-request-data-to-url
  return fetch(`https://api.example.com/items/${created.id}/send`);
}

export function redirectWithFixedPath(request: Request) {
  // ok: hullproof-ssrf-request-data-to-url
  return new URL('/sign-in', request.url);
}

export async function deliver(endpoint: { url: string }) {
  // ruleid: hullproof-ssrf-stored-url
  return fetch(endpoint.url, { method: 'POST' });
}

export async function notAUrlProperty(endpoint: { name: string }, response: { url: string }) {
  // ok: hullproof-ssrf-stored-url
  return fetch(response.url);
}
