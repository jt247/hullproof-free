// ruleid: hullproof-hardcoded-signing-secret
const webhookSecret = "a9f3c1e57b2d4086a1c3e5f70912b4d6"; // gitleaks:allow

// ruleid: hullproof-hardcoded-signing-secret
export const JWT_SECRET = "Zm9vYmFyYmF6cXV4MTIzNDU2Nzg5MA=="; // gitleaks:allow

export const config = {
  // ruleid: hullproof-hardcoded-signing-secret
  signingKey: "k3y9a8b7c6d5e4f3a2b1c0d9e8f7a6b5", // gitleaks:allow
  // ok: hullproof-hardcoded-signing-secret
  publicKey: "pk9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4", // gitleaks:allow
};

// ok: hullproof-hardcoded-signing-secret
const secret = process.env.WEBHOOK_SECRET;

// ok: hullproof-hardcoded-signing-secret
const apiToken = "your-api-token-goes-here-1234"; // gitleaks:allow

// ok: hullproof-hardcoded-signing-secret
const sessionCookieName = "session-token-cookie-v2-name"; // gitleaks:allow

// ok: hullproof-hardcoded-signing-secret
const secretLabel = "Secret";

// ok: hullproof-hardcoded-signing-secret
const cacheKey = "orders-list-cache-key-2024"; // gitleaks:allow

// ok: hullproof-hardcoded-signing-secret
const token = "short1";
