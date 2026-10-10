// ruleid: hullproof-next-public-secret-name
const adminKey = process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY;

// ruleid: hullproof-next-public-secret-name
const stripeSecret = process.env["NEXT_PUBLIC_STRIPE_SECRET_KEY"];

export const config = {
  env: {
    // ruleid: hullproof-next-public-secret-name
    NEXT_PUBLIC_SERVICE_ROLE: process.env.SERVICE_ROLE,
  },
};

// ok: hullproof-next-public-secret-name
const url = process.env.NEXT_PUBLIC_SUPABASE_URL;

// ok: hullproof-next-public-secret-name
const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// ok: hullproof-next-public-secret-name
const serverOnly = process.env.SUPABASE_SERVICE_ROLE_KEY;

// ok: hullproof-next-public-secret-name
const publishable = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
