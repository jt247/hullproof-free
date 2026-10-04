# Two user and two tenant tests with curl

A starting point for the tests that no scanner can run: one user reaching another user's record, one tenant reaching another tenant's data, and a client writing columns it must not write. They settle SEC-AUTHZ-003, SEC-AUTHZ-013, SEC-AUTHZ-014, SEC-DB-033 and SEC-DATA-020. The staging window in `docs/hullproof/templates/STAGING-TEST-WINDOW.md` lists the full session. This file is the scaffold for its Parts 2, 3 and 8.

Run these against a staging copy of the audited commit, never against production data. They send a handful of requests each, and some of them write. Every helper below prints a status code and a size only, so a token or a response body never reaches your terminal history or a log. The read only hook allows only GET, HEAD and OPTIONS requests, so an agent cannot run the writes. You run them and save the output in the evidence folder.

## Setup

Paste once per shell. Read the tokens with `read -s` so they stay out of shell history. The names are examples, use the ones your product has.

```bash
BASE=https://staging.example.com            # your staging app
SB=https://PROJECT.supabase.co              # the Data API base, for Supabase style products only
read -s KEY                                 # the publishable key, if you test the Data API
read -s TA; read -s TB; read -s TC          # access tokens: user A and user B (tenant X), user C (tenant Y)
A_ID=...; B_ID=...; B_ITEM=...; B_FILE=...; Y_ORG=...   # ids that user A must not reach (placeholders)

# call TOKEN METHOD URL [JSON_BODY]   prints "status size". Never the body.
call() {
  local t="$1" m="$2" u="$3" b="${4:-}"
  local args=(-s -o /dev/null -w '%{http_code} %{size_download}\n' -X "$m" -H "Authorization: Bearer $t")
  [ -n "${KEY:-}" ] && args+=(-H "apikey: $KEY")
  [ -n "$b" ] && args+=(-H 'Content-Type: application/json' --data "$b")
  curl "${args[@]}" "$u"
}
```

## SEC-AUTHZ-003: user A reaches user B's record

Repeat for every resource type, and include a parent id in the path with another user's child id.

```bash
for m in GET PATCH DELETE; do printf 'A on B item, %s: ' "$m"; call "$TA" "$m" "$BASE/api/items/$B_ITEM" '{"name":"probe"}'; done
```

Expect 401, 403 or 404 on every line. A 200 or 204 is a FAIL. Read the record back as user B, or with a server credential, and confirm nothing changed.

## SEC-AUTHZ-013 and SEC-AUTHZ-014: tenant X reaches tenant Y

```bash
printf 'A reads Y list: ';   call "$TA" GET  "$BASE/api/orgs/$Y_ORG/items"
printf 'A writes into Y: ';  call "$TA" POST "$BASE/api/items" "{\"org_id\":\"$Y_ORG\",\"name\":\"probe\"}"
printf 'A adds self to Y: '; call "$TA" POST "$BASE/api/orgs/$Y_ORG/members" "{\"user_id\":\"$A_ID\"}"
```

Expect a refusal on each. Repeat through the Data API for tenant tables (`$SB/rest/v1/<table>`), with the filter for Y's tenant id and with no filter at all.

## SEC-DB-033: a client writes billing, role or credential columns

```bash
printf 'A sets own privileged columns: '; call "$TA" PATCH "$SB/rest/v1/profiles?id=eq.$A_ID" '{"role":"admin","plan":"pro","credits":99999,"verified":true}'
printf 'A sets B privileged columns: ';   call "$TA" PATCH "$SB/rest/v1/profiles?id=eq.$B_ID" '{"role":"admin"}'
```

Use your own table and column names. A 204 is not a pass, because the Data API answers 204 when a filter matches no row. Read the rows back with a server credential and confirm no privileged value changed. Also send every column of the table that is not on the editable list, taken from the live column list.

## SEC-DATA-020: user A reaches user B's stored file

```bash
printf 'A downloads B file: '; call "$TA" GET    "$BASE/api/files/$B_FILE/download"
printf 'A deletes B file: ';   call "$TA" DELETE "$BASE/api/files/$B_FILE"
```

Expect a refusal on each, and also when A presents B's storage key in an upload or move request. Every result goes into the evidence folder with the commit, the date and who ran it.
