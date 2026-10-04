export function guard(user: any) {
  // ruleid: hullproof-user-metadata-authz
  if (user.user_metadata.role === "admin") {
    return true;
  }
  // ruleid: hullproof-user-metadata-authz
  if (user?.user_metadata?.is_admin) {
    return true;
  }
  // ok: hullproof-user-metadata-authz
  if (user.app_metadata.role === "admin") {
    return true;
  }
  // ok: hullproof-user-metadata-authz
  const display = user.user_metadata.full_name;
  return display;
}
