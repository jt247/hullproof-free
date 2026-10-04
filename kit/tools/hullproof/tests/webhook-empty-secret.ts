import crypto, { createHmac } from 'crypto';
declare const stripe: any; declare const body: string; declare const sig: string; declare const req: any;
declare function verify(o: any): boolean;
declare class Webhook { constructor(s: string); }

export function bad() {
  // ruleid: hullproof-webhook-empty-secret-fallback
  const h = createHmac('sha256', process.env.WEBHOOK_SECRET ?? '').update(body).digest('hex');
  // ruleid: hullproof-webhook-empty-secret-fallback
  const h2 = crypto.createHmac('sha256', process.env.SIGNING_KEY || '').update(body).digest('hex');
  // ruleid: hullproof-webhook-empty-secret-fallback
  const w = new Webhook(process.env.SVIX_SECRET ?? '');
  // ruleid: hullproof-webhook-empty-secret-fallback
  stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET || '');
  // ruleid: hullproof-webhook-empty-secret-fallback
  verify({ secret: process.env.HOOK_SECRET ?? '', body, sig });
  // ruleid: hullproof-webhook-empty-secret-fallback
  const secret = process.env.PAYMENT_WEBHOOK_SECRET ?? '';
  // ruleid: hullproof-webhook-empty-secret-fallback
  const k = createHmac('sha256', String(process.env.WEBHOOK_SECRET));
}

export function good() {
  const secret = process.env.WEBHOOK_SECRET;
  if (!secret) throw new Error('WEBHOOK_SECRET is not set');
  // ok: hullproof-webhook-empty-secret-fallback
  const h = createHmac('sha256', secret).update(body).digest('hex');
  // ok: hullproof-webhook-empty-secret-fallback
  const mode = process.env.NODE_ENV ?? '';
  // ok: hullproof-webhook-empty-secret-fallback
  const label = process.env.APP_LABEL || '';
}

export function compare() {
  // ruleid: hullproof-secret-compare-env
  if (req.headers['x-webhook-secret'] !== process.env.WEBHOOK_SECRET) return false;
  // ruleid: hullproof-secret-compare-env
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) return false;
  // ok: hullproof-secret-compare-env
  if (process.env.NODE_ENV === 'production') return true;
  // ok: hullproof-secret-compare-env
  if (req.headers.authorization === 'Bearer abc') return true;
}
