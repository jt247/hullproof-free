# Hullproof grep recipes and scan commands

These cover requirements whose Verify steps name a Semgrep rule the rule pack does not ship. Every recipe prints counts, file names or `file:line` only. None prints a matched line, so a hit can never echo a secret into a terminal, a log or an agent transcript.

Run all of them from the repository root. Each hit is a lead, not a finding. Read the code at the location and decide.

## Setup (paste once per shell, works in bash and zsh)

```bash
# sgx MODE PATTERN [DIR]   MODE is -c (count per file), -l (files with a hit), -L (files with no hit)
sgx() { grep -r "$1" -E --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' --include='*.mjs' --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=.turbo --exclude-dir=.expo --exclude-dir=.vercel --exclude-dir=.git -e "$2" "${3:-.}" | { if [ "$1" = "-c" ]; then grep -v ':0$'; else cat; fi; }; }
# sgn PATTERN [DIR]   file:line only, the matched text is cut off
sgn() { grep -r -n -E --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' --include='*.mjs' --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=.turbo --exclude-dir=.expo --exclude-dir=.vercel --exclude-dir=.git -e "$1" "${2:-.}" | cut -d: -f1,2; }
```

## Exclusions and triage

Apply these before you count anything. They are triage for the grep recipes only. The secret scan and the Semgrep pack do not use them (see the next section).

| Exclude | Why | Route a hit elsewhere |
|---------|-----|----------------------|
| `node_modules` | Third party code. Check `git ls-files node_modules` is empty first. A tracked `node_modules` is a finding. | None. |
| `.next`, `.turbo`, `.expo`, `.vercel` | Tool caches with names specific to the tool, for the grep recipes only. | Scan the shipped bundle on purpose with the secret scan below (SEC-SECRETS-001). That scan has no path exclusions. |
| `dist`, `build`, `coverage`, `design`, `designs`, `mockups` | NOT excluded. These names are also used for real source folders (a route folder named `build` is still a route), so a grep recipe that skipped them would never list it. Point the recipe at a narrower folder when generated output makes noise. | None. |
| Supabase anon JWTs (payload role `anon`) and `sb_publishable_` keys | Meant to be public. The Hullproof gitleaks config allows exactly these two shapes by content, never by variable name. | A JWT with any other role is a finding. |
| `.env.local`, agent settings, workspace state | Do not exclude. A hit here means a live secret sits where an agent can read it. | SEC-AGENT-011, not SEC-SECRETS-004. |
| Test and fixture files | Often hold fake credentials. Check that each is fake. | Real value found in a fixture goes to SEC-SECRETS-004. |

## Where scan output goes

Never write scan output to a shared, predictable path such as `/tmp/hullproof`. Use a private folder and remove it:

```bash
OUT=$(mktemp -d); chmod 700 "$OUT"; trap 'rm -rf "$OUT"' EXIT
```

Every command below prints counts, rule ids and file names only. None prints a matched line, a secret or a commit message.

## Semgrep: the kit pack, and the registry rules

```bash
tools/hullproof/helpers/run_rules.sh . 
```

The script scans a clean copy of tracked and not ignored files, ignores `nosemgrep` comments and the repository's own `.semgrepignore`, and prints counts. For the registry rule set, never use the text output, because it prints the matched source line. Send JSON to the private folder and print counts:

```bash
semgrep scan --config p/default --metrics=off --quiet --json --output "$OUT/semgrep-registry.json" .
jq -r '[.results[] | .check_id | split(".") | last] | group_by(.) | map("\(.[0]) \(length)") | .[]' "$OUT/semgrep-registry.json"
```

## Secret scans: working tree and history (SEC-SECRETS-004, SEC-SECRETS-005)

Run both with the Hullproof config and no other. The repository's own `.gitleaks.toml` and `gitleaks:allow` comments can hide findings, so name the config and turn the comments off. Run both: a clean history says nothing about the files you have now, and the reverse.

```bash
CFG=tools/hullproof/gitleaks.toml
gitleaks dir . --redact --no-banner --exit-code 0 --config "$CFG" --ignore-gitleaks-allow
gitleaks git . --redact --no-banner --exit-code 0 --config "$CFG" --ignore-gitleaks-allow
```

The summary lines give the number of leaks and the bytes scanned. If a scan says `scanned ~0 bytes`, it scanned nothing: treat the requirement as NOT ASSESSED. Adjust `CFG` to where the kit sits in your repository. The config has no path allowlist for `.next`, `dist` or `build`, so the shipped bundle is scanned on purpose.

To see which files and rules, print names only. The report is written to standard output and piped, so no file is created and the commit message, author and email fields in it are dropped before anything is shown:

```bash
gitleaks dir . --redact --no-banner --exit-code 0 --config "$CFG" --ignore-gitleaks-allow -f json -r - 2>/dev/null \
  | jq -r '.[] | "\(.RuleID) \(.File):\(.StartLine)"' | sort | uniq -c
gitleaks git . --redact --no-banner --exit-code 0 --config "$CFG" --ignore-gitleaks-allow -f json -r - 2>/dev/null \
  | jq -r '.[] | "\(.RuleID) \(.File):\(.StartLine) \(.Commit[0:8])"' | sort | uniq -c
```

If a report file must be kept, strip it first. The `Message`, `Author`, `Email` and `Date` fields hold commit text and are not redacted by `--redact`. `Secret` and `Match` are redacted, drop them as well:

```bash
gitleaks git . --redact --no-banner --exit-code 0 --config "$CFG" --ignore-gitleaks-allow -f json -r - 2>/dev/null \
  | jq '[.[] | {RuleID, File, StartLine, EndLine, Commit, Fingerprint}]' > "$OUT/gitleaks-history.json"
```

Never add `-v`, `--verbose`, `--log-level`, `--redact=N` or `--no-redact`. They print neighbouring text or whole secrets.

Commit messages are not scanned by gitleaks. Search them by prefix class and print hashes only, never subjects:

```bash
git log --all --format=%h --grep='sk_live_\|ghp_\|AKIA\|sb_secret_\|pdl_live_' | wc -l
```

A history hit means the secret must be rotated even if the file is gone now (SEC-AGENT-013 for secrets seen in an agent session).

### Planted value check (a scan that cannot find a planted value is not evidence)

The config has its own tests, which plant one synthetic value per rule and fail when one is missed:

```bash
python3 -m unittest tools/hullproof/tests/test_gitleaks_config.py
```

For the build folder you are about to ship, plant a fake value in a scratch copy and confirm the count goes up by exactly one:

```bash
cp -R .next/static "$OUT/bundle"
gitleaks dir "$OUT/bundle" --redact --no-banner --exit-code 0 --config "$CFG" 2>&1 | grep -o 'leaks found: [0-9]*\|no leaks found'
printf 'var k="sk_live_%s";\n' "$(LC_ALL=C tr -dc 'a-f0-9' </dev/urandom | head -c 40)" > "$OUT/bundle/planted.js"
gitleaks dir "$OUT/bundle" --redact --no-banner --exit-code 0 --config "$CFG" 2>&1 | grep -o 'leaks found: [0-9]*\|no leaks found'
```

## Kit integrity

The kit ships a checksum list. Run it from the repository root before you rely on the hook, the skills or this folder. The list covers every file the kit ships (agents, skills, hook, rules, tools, documents, templates and editors), so any edit to a shipped kit file shows up. It is not a signature, so compare it with the copy from the release if you suspect tampering. Any line that says FAILED means a kit file changed after install:

```bash
shasum -a 256 -c docs/hullproof/.kit-manifest
```

## Dependency scan and reachability (SEC-SUPPLY-002, SEC-SUPPLY-006)

```bash
osv-scanner scan source -r --format json --output-file "$OUT/osv.json" .
python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(sorted({p['package']['name'] for r in d.get('results',[]) for p in r.get('packages',[]) if p.get('vulnerabilities')}))" "$OUT/osv.json"
```

The last command prints package names with advisories. It prints no advisory text.

Classify each name into one of three classes before assigning severity. Most hits are build only (19 of 21 and 12 of 14 in validation on two real products).

| Class | How to tell | Severity handling |
|-------|-------------|-------------------|
| Direct runtime | The name is under `dependencies` of a shipped workspace package. See the package.json recipe below. | Full advisory severity. |
| Transitive runtime | A lockfile recipe below reaches the name from a `dependencies` entry of a shipped workspace package. | Full severity when the vulnerable code path is used, otherwise one level lower with the reason recorded. |
| Dev and build only | A lockfile recipe below reaches the name only from `devDependencies`. | Record as dev only, with a one line decisions log entry, as the standard says. If the package runs in CI with secrets (SEC-SUPPLY-016, SEC-SUPPLY-017), treat it as runtime. |

The recipes read the lockfile as text. They do not run the package manager, install anything, execute a script or contact a registry. Set `NAME` to the package name first.

Direct dependencies, from the `package.json` files:

<!-- recipe:package-json-fields -->
```bash
NAME=nanoid
for f in package.json apps/*/package.json packages/*/package.json services/*/package.json; do
  [ -f "$f" ] && jq -r --arg f "$f" --arg n "$NAME" '["dependencies","devDependencies","optionalDependencies","peerDependencies"][] as $k | select((.[$k] // {}) | has($n)) | "\($f) \($k)"' "$f"
done
```

pnpm (`pnpm-lock.yaml`, lockfile versions 6 to 9): lists the workspace importers that reach the package, through any chain of dependents, with the section they reach it from. `dependencies` or `optionalDependencies` means runtime. Only `devDependencies` means dev only:

<!-- recipe:pnpm-who -->
```bash
NAME=nanoid
awk -v name="$NAME" '
function strip(s) { gsub(/^\047|\047$/, "", s); return s }
function pkgname(k,   s, i) { s = strip(k); sub(/\(.*$/, "", s); i = match(s, /@[^@]*$/); return (i > 1) ? substr(s, 1, i - 1) : s }
/^[A-Za-z]/ { top = $0; sub(/:.*$/, "", top); next }
/^  [^ ]/ { parent = $0; sub(/^  /, "", parent); sub(/:.*$/, "", parent); if (top == "snapshots" || top == "packages") parent = pkgname(parent); next }
/^    (dependencies|devDependencies|optionalDependencies|peerDependencies):/ { sec = $1; sub(/:$/, "", sec); next }
/^      [^ ]/ && (top == "importers" || top == "snapshots" || top == "packages") {
  c = $0; sub(/^      /, "", c); sub(/:.*$/, "", c); c = strip(c)
  n++; Et[n] = top; Ep[n] = parent; Ec[n] = c; Es[n] = sec
}
END {
  q[1] = name; qn = 1; seen[name] = 1
  for (i = 1; i <= qn; i++) for (e = 1; e <= n; e++) if (Ec[e] == q[i]) {
    if (Et[e] == "importers") roots[Ep[e] " (" Es[e] ")"] = 1
    else if (!(Ep[e] in seen)) { seen[Ep[e]] = 1; q[++qn] = Ep[e] }
  }
  for (r in roots) if (r ~ /\((dependencies|optionalDependencies)\)$/) rt = 1
  print (length(roots) == 0) ? "RESULT not reachable from any importer, or not in this lockfile" : (rt ? "RESULT runtime" : "RESULT dev only")
  for (r in roots) print "  " r
}' pnpm-lock.yaml
```

npm (`package-lock.json`, lockfile version 2 or 3): npm marks a package `dev: true` when it is reachable only through dev dependencies. The second command lists the direct dependents:

<!-- recipe:npm-who -->
```bash
NAME=nanoid
jq -r --arg n "$NAME" '.packages | to_entries[] | select(.key | test("(^|/)node_modules/" + $n + "$")) | "\(.key) dev=\(.value.dev // false) optional=\(.value.optional // false) peer=\(.value.peer // false)"' package-lock.json
jq -r --arg n "$NAME" '.packages | to_entries[] | select((.value.dependencies // {} | has($n)) or (.value.devDependencies // {} | has($n))) | "depended on by: \(if .key == "" then "(root package.json)" else .key end)"' package-lock.json
```

Yarn (`yarn.lock`, classic or Berry): the lockfile has no dev marker, so find every package that depends on the name, then see which of those the `package.json` files list and in which field:

<!-- recipe:yarn-who -->
```bash
NAME=nanoid
ANC=$(awk -v name="$NAME" '
function dname(d,   i) { gsub(/^"|"$/, "", d); i = match(d, /@[^@]*$/); return (i > 1) ? substr(d, 1, i - 1) : d }
/^[^ #]/ { s = $0; sub(/:$/, "", s); split(s, ds, /, ?/); cur = dname(ds[1]); next }
/^  (dependencies|optionalDependencies):/ { indeps = 1; next }
/^  [^ ]/ { indeps = 0; next }
/^    [^ ]/ && indeps { c = $1; sub(/:$/, "", c); gsub(/"/, "", c); n++; P[n] = cur; C[n] = c }
END {
  q[1] = name; qn = 1; seen[name] = 1
  for (i = 1; i <= qn; i++) for (e = 1; e <= n; e++) if (C[e] == q[i] && !(P[e] in seen)) { seen[P[e]] = 1; q[++qn] = P[e] }
  for (k in seen) print k
}' yarn.lock </dev/null | sort -u)
for f in package.json apps/*/package.json packages/*/package.json services/*/package.json; do
  [ -f "$f" ] && jq -r --arg f "$f" --arg anc "$ANC" '($anc | split("\n")) as $a | ["dependencies","devDependencies","optionalDependencies"][] as $k | (.[$k] // {} | keys[]) | select(. as $x | $a | index($x)) | "\($f) \($k) \(.)"' "$f"
done
```

A line with `dependencies` in the output means runtime. Only `devDependencies` lines mean dev only. No output means the package is not reached from a listed manifest.

OSV cannot see vendored copies. Look for them by hand for SEC-SUPPLY-006: `find . -path ./node_modules -prune -o \( -name '*.min.js' -o -type d -name vendor \) -print | head -20` lists candidates by path only.

## Report provenance recipes

These fill the provenance fields of `templates/AUDIT-REPORT.md` (Adopted on, Audited tree, Evidence hashes, Pull request refs fetched). The first block holds the commands the skills and agents run: every line is allowed by the read only hook for the auditor profile, and a test runs each one through the hook. The second block is for the owner's own terminal, because the hook blocks `git fetch`, `for-each-ref` and `shasum` on evidence files.

Run by the skill or agent:

<!-- hookcmd -->
```
git rev-parse HEAD
git log -1 --no-textconv --no-ext-diff --format=%H%x20%T HEAD
git log --no-textconv --no-ext-diff --reverse --diff-filter=A --name-status --format=%H%x20%cI -- docs/hullproof/STANDARD.md
git diff --no-textconv --no-ext-diff --name-only 1a2b3c4 HEAD
git ls-files -s docs/security/evidence/2026-01-31/semgrep.json
```

1. `%T` is the tree id of the audited commit. Write it in the trailer. In a delta audit also write the tree id of the base commit and the number of paths the `--name-only` line prints.
2. The `--reverse --diff-filter=A` line prints the commit and committer date of the first commit that added `STANDARD.md`. The first line of its output is the Adopted on value. If it prints nothing, write "not in git history". A rewritten history changes this date, so compare it with the first push date shown by the hosting platform.
3. `git ls-files -s <path>` prints the blob id of a file committed to git, which is the hash kind to write for committed evidence. An evidence file that is not committed has no hash the agent can compute: use the owner's `shasum` output.
4. A shallow clone sees one commit. Look for the file `.git/shallow` with Glob. If it exists, the history scan did not cover history, so say so in the Tool output section.

Run by the owner in their own terminal:

```
# Pull request and fork refs, so the history scan sees commits that never reached a branch (GitHub, then GitLab)
git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'
git fetch origin '+refs/merge-requests/*/head:refs/remotes/origin/mr/*'
git for-each-ref refs/remotes/origin/pr refs/remotes/origin/mr | wc -l
# Hashes of the evidence files, written next to them and pasted into the report unchanged
(cd docs/security/evidence/2026-01-31 && shasum -a 256 * > SHA256SUMS)
# Later, a new run can check the same files
(cd docs/security/evidence/2026-01-31 && shasum -a 256 -c SHA256SUMS)
```

The fetch brings in the pull request refs the host still serves. A commit that a force push or a deleted branch left reachable only by its hash is not fetched this way: the owner asks the host (or lists it from the push events) and gives the hashes to fetch. Write the ref count the owner reports in the Pull request refs fetched row, then run `gitleaks git` again. The skills run `gitleaks git .` with all refs, so refs fetched into the clone are scanned.

## Recipes for requirements with no shipped rule

Each line says what a hit means. `sgx -L` lists files that lack the call, which is usually the finding.

- **SEC-AUTHZ-002, SEC-API-001**: Route handlers with no auth call.
  `sgx -L '(getUser|requireUser|requireAuth|getSession|auth\(|authorize)' app/api`

- **SEC-AUTHZ-020**: Admin files with no admin guard.
  `sgx -L '(requireAdmin|assertAdmin|isAdmin|requireRole)' app/admin`

- **SEC-API-002**: `select *` in API code.
  `sgx -c "select\\((['\"])\\*\\1\\)|select \\*" app`

- **SEC-API-010**: Route files with no schema parse.
  `sgx -L '(\.parse\(|\.safeParse\()' app/api`

- **SEC-API-102, SEC-DATA-009**: Plain comparison of signatures or secrets.
  `sgx -c '(signature|digest|hmac|secret|sig)[[:alnum:]_]*[[:space:]]*[!=]==?' .`

- **SEC-API-125**: Checkout code reading price from the request.
  `sgx -c '(body|json\(\)|formData).*(amount|price|currency|discount)' app`

- **SEC-API-126**: Writes to entitlement tables, then drop the webhook path.
  `sgn "from\\(['\"](subscriptions|entitlements|credits|plans)['\"]\\)[[:space:]]*\\.(update|upsert|insert)" . | grep -v -i webhook`

- **SEC-API-020**: Shell calls.
  `sgx -c '(child_process|execSync|spawnSync|exec\(|shell:[[:space:]]*true)' .`

- **SEC-API-034**: Outbound calls built from request data.
  `sgx -c '(fetch|axios|got)\(.*(req|request|params|searchParams|body)' .`

- **SEC-AUTH-001**: Home grown password or token crypto.
  `sgx -c '(bcrypt|argon2|scrypt|pbkdf2|createHash|createHmac)' .`

- **SEC-AUTH-002**: Token decode without verify, session reads on the server.
  `sgx -c '(jwt\.decode|decodeJwt|auth\.getSession)\(' .`

- **SEC-AUTH-031**: Weak OAuth flow settings.
  `sgx -c "(usePKCE:[[:space:]]*false|codeChallengeMethod:[[:space:]]*['\"]plain|responseType:[[:space:]]*['\"]token)" .`

- **SEC-AUTHZ-003, SEC-AUTHZ-015**: Tenant or owner id taken from the request.
  `sgn '(tenant_id|org_id|organization_id|owner_id).*(params|searchParams|body|headers)' app`

- **SEC-AUTHZ-004**: Request body passed straight into a write.
  `sgn '\.(insert|update|upsert)\((await[[:space:]]+)?(\.\.\.)?(body|data|input|payload|[a-z]+\.json\(\))' .`

- **SEC-DATA-003**: Cipher modes.
  `sgx -c "(createCipheriv|ecb|cbc|ctr|cfb|ofb)" .`

- **SEC-DATA-004**: Weak hashes, include SQL migrations.
  `sgx -c '(md5|md4|sha1|SHA-1|crc32)' .` and `grep -rciE 'md5\(' supabase/migrations | grep -v ':0$'`

- **SEC-DATA-007**: Literal keys in crypto calls. Count only, never print..
  `sgx -c "(createCipheriv|createHmac|importKey)\\([^)]*['\"][A-Za-z0-9+/=]{16,}['\"]" .`

- **SEC-DATA-016**: TLS verification off.
  `sgx -c '(rejectUnauthorized:[[:space:]]*false|NODE_TLS_REJECT_UNAUTHORIZED|strictSSL:[[:space:]]*false|sslmode=(disable|allow|prefer))' .`

- **SEC-DATA-027**: Personal fields inside URLs.
  `sgn '(searchParams|URLSearchParams).*(email|phone|dob)' .`

- **SEC-WEB-002**: Link targets from data.
  `sgn '(href|src|action)=\{[^}]*(req|request|params|searchParams|data|props)' .`

- **SEC-WEB-003**: Headers built from data.
  `sgn '(setHeader|headers\.set)\(.*(req|request|params|searchParams|body)' .`

- **SEC-WEB-004, SEC-LOG-001**: Logger calls that receive request bodies or secret named values.
  `sgx -c '(console|logger|log)\.[a-z]+\(.*(req\.body|headers|token|secret|password|authorization)' .`

- **SEC-WEB-014**: `postMessage` with a wildcard, message listeners.
  `sgn "(postMessage\\(.*['\"]\\*['\"]|addEventListener\\(['\"]message)" .`

- **SEC-WEB-025**: GET handlers that also change state.
  `sgx -l 'export (async )?function GET' app | xargs grep -lE '\.(insert|update|upsert|delete)\(|\.rpc\('`

- **SEC-WEB-033**: Markdown with raw HTML enabled.
  `sgx -c '(rehype-raw|allowDangerousHtml|skipHtml=\{false)' .`

- **SEC-WEB-040**: JSONP.
  `sgn '(jsonp|callback)[[:space:]]*=|searchParams.get\(.callback.\)' app`

- **SEC-LOG-002**: Personal fields in log calls.
  `sgx -c '(console|logger|log)\.[a-z]+\(.*(email|phone|nin|bvn)' .`

- **SEC-LOG-017**: Error text returned to the client.
  `sgn 'json\(.*(error|err)\.(message|stack)' app`

- **SEC-LOG-019**: Single line empty catch.
  `sgx -c 'catch[[:space:]]*(\([^)]*\))?[[:space:]]*\{[[:space:]]*\}' .`

- **SEC-MOBILE-003**: SecureStore writes with no ThisDeviceOnly option.
  `sgx -l 'setItemAsync' . | xargs grep -L ThisDeviceOnly`

- **SEC-MOBILE-007**: WebView with no origin allowlist.
  `sgx -l '<WebView' . | xargs grep -L originWhitelist`

- **SEC-MOBILE-008**: Console or analytics calls with token named values.
  `sgx -c '(console|Sentry|posthog)\.[A-Za-z]+\(.*(token|session|password)' .`

- **SEC-MOBILE-020**: Writes to shared storage.
  `sgx -c '(MediaLibrary\.(saveToLibraryAsync|createAssetAsync)|Sharing\.shareAsync)' .`

- **SEC-DB-003**: Default privilege revoke present in migrations.
  `grep -rciE 'alter default privileges' supabase/migrations | grep -v ':0$'` (no output means none)

Notes.

1. The patterns use POSIX classes so they run on macOS and Linux grep. Quotes around patterns that contain a single quote use double quotes, so escape with care.
2. `sgx -L` lists file names only. A listed file with no business reading the auth call, such as a public health route, is a legitimate result. Keep a short public allowlist as SEC-API-001 asks.
3. Where a recipe and a rule in `rules/` cover the same ID, the rule is the primary check and the recipe is the cross check.
4. Bounded scope. These recipes find leads in text. They do not prove a control exists. The Verify steps in each requirement still apply.
