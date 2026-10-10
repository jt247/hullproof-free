"use server";

import { getUser } from "@/lib/auth";

// ruleid: hullproof-server-action-no-auth
export async function deleteProject(id: string) {
  await db.delete(id);
}

// ruleid: hullproof-server-action-no-auth
export const renameProject = async (id: string, name: string) => {
  await db.rename(id, name);
};

// ok: hullproof-server-action-no-auth
export async function updateProfile(name: string) {
  const user = await getUser();
  await db.update(user.id, name);
}

// ok: hullproof-server-action-no-auth
export const archiveProject = async (id: string) => {
  const session = await auth();
  await db.archive(session.user.id, id);
};

// A session read inside a nested block, a try block or a method chain is still an auth check.
// ok: hullproof-server-action-no-auth
export async function nestedSessionRead(id: string) {
  try {
    if (id) {
      const { data } = await supabase.auth.getUser();
      if (!data.user) throw new Error("no");
    }
  } finally {
    log();
  }
  await db.delete(id);
}

// ok: hullproof-server-action-no-auth
export const sessionInBranch = async (id: string, force: boolean) => {
  if (force) {
    const s = await getServerSession(authOptions);
    if (!s) return;
  }
  await db.archive(id);
};

// ruleid: hullproof-server-action-no-auth
export async function authorsOnly(id: string) {
  const rows = await getAuthors(id);
  return rows;
}
