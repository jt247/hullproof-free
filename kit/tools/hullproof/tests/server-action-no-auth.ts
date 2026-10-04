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
