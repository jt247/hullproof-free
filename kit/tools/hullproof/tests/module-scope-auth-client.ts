import { createServerClient } from "@supabase/ssr";

// ruleid: hullproof-module-scope-auth-client
const shared = createServerClient(url, key, { cookies });

export async function handler() {
  // ok: hullproof-module-scope-auth-client
  const client = createServerClient(url, key, { cookies: cookieAdapter() });
  return client.auth.getUser();
}

export const arrow = async () => {
  // ok: hullproof-module-scope-auth-client
  const client = createServerClient(url, key, { cookies: cookieAdapter() });
  return client;
};
