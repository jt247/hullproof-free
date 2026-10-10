# Findings record

Fixture for the owner packet tests.

```hullproof-findings
{
  "schema_version": "1.0.0",
  "report": {"commit": "0123456789abcdef0123456789abcdef01234567", "tree": "89abcdef0123456789abcdef0123456789abcdef", "tree_clean": true,
             "stage": "GROWTH", "profile": "standard", "scope": "full", "run_status": "complete", "agent_calls": 3, "budget": null},
  "records": [
    {"fingerprint": "SEC-AUTH-017:app/api/logout/route.ts:logout-keeps-refresh-token", "kind": "routed", "sec_ids": ["SEC-AUTH-017"],
     "title": "Logout may keep the refresh token alive", "state": "NEEDS DYNAMIC TEST", "reason": "Server revocation is in the provider",
     "owner_action": "Replay the refresh token after logout on staging", "check_card": null, "raised_by": ["hunter-1"]},
    {"fingerprint": "SEC-DB-016:supabase/migrations:backup-plan-unknown", "kind": "routed", "sec_ids": ["SEC-DB-016", "SEC-DB-017"],
     "title": "Backup plan is not in the repo", "state": "NEEDS DASHBOARD", "reason": "Plan lives in the provider",
     "owner_action": "Export the backup plan", "check_card": null, "raised_by": ["hunter-2"]},
    {"fingerprint": "OBS:next.config.js:powered-by-header-enabled", "kind": "observation", "sec_ids": [], "title": "Header on",
     "where": [{"file": "next.config.js", "line": 3, "note": "poweredByHeader"}], "note": "No boundary result.", "raised_by": ["hunter-4"]}
  ]
}
```
