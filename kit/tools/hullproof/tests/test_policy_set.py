import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "helpers"))
import policy_set  # noqa: E402

MIG = os.path.join(HERE, "policy_set", "migrations")
FIRST = os.path.join(MIG, "0001_init.sql")


def codes(flags):
    return {(f[2], f[3]) for f in flags}


class PolicySetTest(unittest.TestCase):
    def setUp(self):
        self.st, self.files, self.flags = policy_set.build([MIG])
        self.c = codes(self.flags)

    def test_files_read_in_order(self):
        self.assertEqual([os.path.basename(f) for f in self.files],
                         ["0001_init.sql", "0002_fixes.sql", "0003_more.sql"])

    def test_removed_objects_are_gone(self):
        names = {k[1] for k in self.st.policies}
        for gone in ("old_policy", "notes_all", "meta_admin"):
            self.assertNotIn(gone, names)
        self.assertNotIn("public.scratch", self.st.tables)

    def test_alter_policy_adds_check(self):
        p = self.st.policies[("public.notes", "notes_owner_update")]
        self.assertTrue(p["check"])
        self.assertNotIn(("UPDATE_NO_WITH_CHECK", "notes.notes_owner_update"), self.c)

    def test_update_without_check_is_low_hygiene(self):
        self.assertIn(("UPDATE_NO_WITH_CHECK", "profiles.profiles_update"), self.c)
        sev = {f[0] for f in self.flags if f[2] == "UPDATE_NO_WITH_CHECK"}
        self.assertEqual(sev, {"LOW"})

    def test_final_set_has_no_role_or_metadata_flags(self):
        self.assertFalse([c for c in self.c if c[0] in ("POLICY_NO_ROLE", "POLICY_USES_USER_METADATA")])

    def test_definer_search_path(self):
        for fn in ("get_secret()", "grant_credits(uuid,int)", "admin_tool(uuid)"):
            self.assertNotIn(("DEFINER_NO_SEARCH_PATH", fn), self.c)

    def test_definer_exec_by_client(self):
        self.assertIn(("DEFINER_EXEC_ANON_OR_PUBLIC", "admin_tool(uuid)"), self.c)
        self.assertNotIn(("DEFINER_EXEC_ANON_OR_PUBLIC", "get_secret()"), self.c)
        self.assertNotIn(("DEFINER_EXEC_ANON_OR_PUBLIC", "grant_credits(uuid,int)"), self.c)
        self.assertIn(("DEFINER_EXEC_AUTHENTICATED", "grant_credits(uuid,int)"), self.c)

    def test_sensitive_columns(self):
        hit = {f[3]: f for f in self.flags if f[2] == "CLIENT_WRITABLE_SENSITIVE_COLUMNS"}
        self.assertIn("profiles", hit)
        self.assertNotIn("accounts", hit)  # credits protected by a column grant
        for col in ("role", "plan", "is_verified"):
            self.assertIn(col, hit["profiles"][4])
        self.assertEqual(hit["profiles"][0], "CRITICAL")

    def test_rls_enabled_by_last_migration(self):
        self.assertFalse([c for c in self.c if c[0] == "RLS_NOT_ENABLED"])

    def test_first_migration_alone(self):
        _, _, flags = policy_set.build([FIRST])
        c = codes(flags)
        self.assertIn(("RLS_NOT_ENABLED", "orders"), c)
        self.assertIn(("POLICY_NO_ROLE", "notes.notes_all"), c)
        self.assertIn(("POLICY_USES_USER_METADATA", "notes.meta_admin"), c)
        self.assertIn(("DEFINER_NO_SEARCH_PATH", "get_secret()"), c)
        self.assertIn(("DEFINER_EXEC_ANON_OR_PUBLIC", "get_secret()"), c)
        sev = [f[0] for f in flags if f[2] == "RLS_NOT_ENABLED"][0]
        self.assertEqual(sev, "CRITICAL")

    def test_no_platform_defaults_lowers_rls_severity(self):
        _, _, flags = policy_set.build([FIRST], platform_defaults=False)
        sev = [f[0] for f in flags if f[2] == "RLS_NOT_ENABLED"][0]
        self.assertEqual(sev, "HIGH")

    def test_cli_output_has_no_expressions(self):
        script = os.path.join(HERE, "..", "helpers", "policy_set.py")
        out = subprocess.run([sys.executable, script, MIG], capture_output=True, text=True, check=True).stdout
        self.assertIn("COUNTS", out)
        self.assertNotIn("auth.uid()", out)
        self.assertNotIn("select 'x'", out)


if __name__ == "__main__":
    unittest.main()
