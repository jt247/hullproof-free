import { z } from "zod";

// ruleid: hullproof-zod-privileged-field
export const updateProfile = z.object({
  name: z.string().max(80),
  role: z.enum(["user", "admin"]),
});

// ruleid: hullproof-zod-privileged-field
export const signup = z.object({
  email: z.string().email(),
  is_admin: z.boolean().optional(),
});

// ruleid: hullproof-zod-privileged-field
export const createProject = z.strictObject({
  title: z.string(),
  owner_id: z.string().uuid(),
});

// ruleid: hullproof-zod-privileged-field
export const upgrade = z.object({ plan: z.string() });

// ok: hullproof-zod-privileged-field
export const updateName = z.object({
  name: z.string().max(80),
  bio: z.string().max(500).optional(),
});

// ok: hullproof-zod-privileged-field
export const search = z.object({ q: z.string(), page: z.number().int().min(1) });
