# Route, handler and gate enumeration recipes

Tested recipes that list every entry point of a product (HTTP handlers, server actions) and answer the applicability gate questions from the code and the data model instead of from a word list. They back the lists that SEC-AUTHZ-002, SEC-API-001, SEC-LOG-003 and the gates depend on, and they replace single folder searches that print nothing in a monorepo.

Rules for every recipe here:

1. They search from the repository root, so a workspace folder (`apps/*`, `packages/*`, `services/*`) and a `src/` folder are covered. Only `node_modules`, `.git`, `.next`, `.turbo`, `.vercel` and `.expo` are skipped. `dist` and `build` are not skipped, because those names are also used for real source folders. Compiled output then shows up as a duplicate: read the file list and discount it.
2. They print counts, file names and HTTP method names only. They never print a matched line or a value.
3. A list is a lead, not a proof. An empty list for a framework you use means the recipe does not know your layout: widen it and say so, never conclude "none". Hand written protocol handlers (a route that dispatches on a `method` field) are listed by the gate recipes below.
4. A person runs them in a terminal, from the repository root, with bash or zsh. The skills and agents cannot run them (the hook allows no shell functions or pipes). In an agent session use the Glob and Grep patterns in the table at the end.

## Setup (paste once per shell)

<!-- recipe:enum-setup -->
```bash
# src_files prints every JavaScript or TypeScript file under ROOT (default: the current folder) except dependency and cache folders
ROOT=.
src_files() { find "${ROOT:-.}" \( -name node_modules -o -name .git -o -name .next -o -name .turbo -o -name .vercel -o -name .expo \) -prune -o -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.mjs' -o -name '*.cjs' \) -print; }
# methods_in FILE prints the HTTP method names exported by a Next.js route file (declarations, re-exports, destructured handlers)
methods_in() {
  { grep -oE 'export +(async +)?(function +|const +)(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b' "$1"
    grep -oE 'export +(const +)?\{[^}]*\}' "$1"; } | grep -oE '\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b' | sort -u | tr '\n' ',' | sed 's/,$//'
}
```

## Next.js app router handlers

Lists every `route.*` file under an `app` folder, at any depth, with its exported methods. A handler file that exports no method name (`none`) needs reading: it may export a default function that a wrapper turns into a handler. The last lines list `middleware` and `proxy` files, because a check that lives only there is not an authorization check (SEC-API-027).

<!-- recipe:enum-app-router -->
```bash
src_files | grep -E '(^|/)app/(.*/)?route\.(ts|tsx|js|jsx|mjs)$' | sort | while read -r f; do
  m=$(methods_in "$f"); printf 'app-route\t%s\t%s\n' "$f" "${m:-none}"
done
src_files | grep -E '(^|/)(middleware|proxy)\.(ts|js|mjs)$' | sort | while read -r f; do printf 'edge-gate\t%s\n' "$f"; done
```

## Next.js pages router handlers

Lists every file under a `pages/api` folder, with the method names it mentions. `any` means the file never names a method, so every method reaches the handler.

<!-- recipe:enum-pages-router -->
```bash
src_files | grep -E '(^|/)pages/api/' | grep -vE '\.(test|spec)\.' | sort | while read -r f; do
  m=$(grep -oE "['\"](GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)['\"]" "$f" | tr -d "\"'" | sort -u | tr '\n' ',' | sed 's/,$//')
  printf 'pages-api\t%s\t%s\n' "$f" "${m:-any}"
done
```

## Server actions

A server action is an async function in a file that starts with the `'use server'` directive (file level: every export is a public endpoint) or a function with the directive inside its body (inline). Both are reachable by a direct POST. File level files print the number of exported async functions.

<!-- recipe:enum-server-actions -->
```bash
src_files | sort | while read -r f; do
  first=$(awk '/^[[:space:]]*$/ {next} /^[[:space:]]*(\/\/|\/\*|\*)/ {next} {print; exit}' "$f")
  if printf '%s' "$first" | grep -qE "^[[:space:]]*['\"]use server['\"]"; then
    n=$(grep -cE '^export +(async +function|const +[A-Za-z0-9_]+ *(:[^=]*)?= *async)' "$f")
    printf 'server-action\t%s\tfile-level\t%s\n' "$f" "$n"
  elif grep -qE "^[[:space:]]+['\"]use server['\"]" "$f"; then
    printf 'server-action\t%s\tinline\t%s\n' "$f" "$(grep -cE "^[[:space:]]+['\"]use server['\"]" "$f")"
  fi
done
```

## Express routers

Lists files that import `express` or build a `Router()`, with the count of route registrations per method and the number of mounts and chained `.route()` calls. A registration counts only when its first argument is a string that starts with `/`, so `cache.get('a')` and `headers.get('x')` are not counted. Other frameworks (Fastify, Koa, Hono, NestJS) use other verbs: copy the recipe and change the pattern.

<!-- recipe:enum-express -->
```bash
src_files | sort | while read -r f; do
  grep -qE "from +['\"]express['\"]|require\(['\"]express['\"]\)|\bRouter\(\)" "$f" || continue
  c=$(grep -oE "\.(get|post|put|patch|delete|head|options|all)\( *['\"\`]/" "$f" | sed -E 's/^\.([a-z]+).*/\1/' | sort | uniq -c | awk '{printf "%s%s:%s", s, toupper($2), $1; s=","}')
  mounts=$(grep -cE "\.use\( *['\"\`]/" "$f"); chains=$(grep -cE "\.route\( *['\"\`]/" "$f")
  printf 'express\t%s\t%s\tmounts=%s\tchains=%s\n' "$f" "${c:-none}" "$mounts" "$chains"
done
```

## One list, with totals

Run the setup block and the four recipes above, then count by kind. Compare the totals with the access matrix and with the log inventory. A handler in this list and not in the matrix is the finding for a Pro edition requirement and SEC-AUTHZ-002, and a handler with no denial record is the finding for SEC-LOG-003.

<!-- recipe:enum-totals -->
```bash
{ enum_all; } | cut -f1 | sort | uniq -c | awk '{printf "%s=%s\n", $2, $1}'
```

`enum_all` stands for the four recipes run one after the other, in the order above (the tests define it as exactly that).

## Structural gate queries

The gate questions in the standard are about the data model and the code paths. The word lists in the gate evidence text are hints. These queries give the structural answer first. Run the SQL on every environment's database (a read only role is enough: they read the catalog and no row), and the code searches on the whole repository. Record the commands, the number of files searched and the counts, as the gate asks.

### GATE-TENANTS: candidate sharing boundaries in the schema (Postgres, Supabase)

<!-- recipe:sql-tenants -->
```sql
-- 1. Candidates: every table that other tables reference with a foreign key, other than the users table (a helper, not the test)
select c.conrelid::regclass::text as child_table, c.confrelid::regclass::text as parent_table
from pg_constraint c
join pg_namespace n on n.oid = c.connamespace
where c.contype = 'f'
  and n.nspname not in ('pg_catalog', 'information_schema', 'auth', 'storage', 'realtime', 'vault', 'extensions', 'graphql', 'graphql_public', 'net', 'cron', 'supabase_functions', 'pgsodium')
  and c.confrelid::regclass::text not in ('auth.users', 'users', 'public.users')
order by 1, 2;
-- 2. Columns that look like a tenant key (a hint: the product may use its own word)
select table_schema, table_name, column_name
from information_schema.columns
where table_schema not in ('pg_catalog', 'information_schema', 'auth', 'storage', 'realtime', 'vault', 'extensions', 'graphql', 'graphql_public', 'net', 'cron', 'supabase_functions', 'pgsodium')
  and column_name ~* '(^|_)(tenant|org|organi[sz]ation|workspace|team|account|company|project|group)_?id$'
order by 1, 2, 3;
-- 3. Membership style tables
select table_schema, table_name
from information_schema.tables
where table_type = 'BASE TABLE'
  and table_schema not in ('pg_catalog', 'information_schema', 'auth', 'storage', 'realtime', 'vault', 'extensions', 'graphql', 'graphql_public', 'net', 'cron', 'supabase_functions', 'pgsodium')
  and table_name ~* '(member|membership|org_user|team_user|tenant_user|workspace_user|role_assign|collaborator)'
order by 1, 2;
```

Read the results as the gate defines a sharing boundary: a table that groups users or customers (an organisation, team, workspace or account) and that other tables reference to decide who may see their rows. Query 1 lists candidates only. A foreign key from one ordinary table to another (orders to products, comments to posts) is not a sharing boundary on its own, so look at the parent tables it returns and ask whether any of them groups customers. A hit in query 3 usually points to one. If a parent table from query 1 groups customers, or query 3 finds a membership style table, the answer is Yes, whatever the column names are. A schema with tables and no grouping table in any of the three queries is the evidence for No. Cross check it with the owner's statement that every customer has a separate deployment.

### GATE-PAYMENTS: payment tables and columns

<!-- recipe:sql-payments -->
```sql
select table_schema, table_name
from information_schema.tables
where table_type = 'BASE TABLE'
  and table_schema not in ('pg_catalog', 'information_schema', 'auth', 'storage', 'realtime', 'vault', 'extensions')
  and table_name ~* '(payment|subscription|invoice|entitlement|credit|plan|order|charge|transaction|billing|price|purchase|receipt|wallet)'
order by 1, 2;
select table_schema, table_name, column_name
from information_schema.columns
where table_schema not in ('pg_catalog', 'information_schema', 'auth', 'storage', 'realtime', 'vault', 'extensions')
  and column_name ~* '(stripe|paystack|paddle|flutterwave|revenuecat|apple|google).*(id|customer|token|receipt)|^(plan|tier|credits?|balance|entitlements?)$|price_?id|customer_?id'
order by 1, 2, 3;
```

### GATE-PAYMENTS, GATE-UPLOADS, GATE-TOOLS, GATE-URLFETCH, GATE-MCP: code searches

Each prints file names and counts only. Use the setup block first.

<!-- recipe:code-payments -->
```bash
src_files | xargs grep -lE "paystack|paddle|stripe|flutterwave|revenuecat|StoreKit|billing\.|checkout|entitlement" 2>/dev/null | sort
find "${ROOT:-.}" -name node_modules -prune -o -name package.json -print | xargs grep -lE '"(stripe|@stripe/[a-z-]+|paystack[a-z-]*|@paddle/[a-z-]+|flutterwave[a-z-]*|react-native-purchases)"' 2>/dev/null | sort
```

<!-- recipe:code-tools -->
```bash
# Tool registrations and model driven actions (SDK vocabularies differ, so the list is wide on purpose)
src_files | xargs grep -lE "\btools *[:=] *[\[{]|tool_choice|toolChoice|function_call|tool_use|bind_tools|registerTool|defineTool|server\.tool\(|\btool\(\{|generateText\(|streamText\(|messages\.create\(|responses\.create\(|agent\.run|computer_use" 2>/dev/null | sort
# Model output applied as an action: a field of a model result used in a write, a send or a call
src_files | xargs grep -lE "\.(tool_calls|toolCalls|function_call)\b" 2>/dev/null | sort
```

<!-- recipe:code-urlfetch -->
```bash
# Files with call sites of outbound HTTP libraries and renderers, with the number of matching lines
src_files | xargs grep -cE "\b(fetch|axios(\.[a-z]+)?|got|ky|undici\.[a-z]+|request|superagent|needle)\(|https?\.(get|request)\(|page\.goto\(|puppeteer|playwright|wkhtmltopdf|html-pdf|sharp\(" 2>/dev/null | grep -v ':0$' | sort
# Calls whose first argument is a variable, not a string literal (file:line only: read each one)
src_files | xargs grep -nE "\b(fetch|axios(\.[a-z]+)?|got|ky)\( *[A-Za-z_]" 2>/dev/null | cut -d: -f1,2 | sort
```

<!-- recipe:code-mcp -->
```bash
src_files | xargs grep -lE "@modelcontextprotocol/sdk|McpServer|mcp-handler|createMcpHandler|tools/list|tools/call|jsonrpc|['\"]/?mcp['\"]" 2>/dev/null | sort
```

<!-- recipe:code-uploads -->
```bash
src_files | xargs grep -lE "formData\(\)|multipart|multer|busboy|formidable|createSignedUploadUrl|getSignedUrl|presign|putObject|data:[a-z/]+;base64|FileReader|DocumentPicker|ImagePicker|launchImageLibrary" 2>/dev/null | sort
```

### What the answers decide

| Result | Meaning for the gate |
|--------|----------------------|
| SQL query 3 returns a membership style table, or a parent table from query 1 groups customers (an organisation, team, workspace or account) | GATE-TENANTS is Yes. A foreign key between ordinary tables is not enough on its own. |
| `code-tools` lists any file | Read each. A file that sends model output to a write, a message or a parameter makes GATE-TOOLS Yes, with or without a tool interface. |
| `code-urlfetch` lists a call whose first argument is a variable | Read it. If a user, a stored record, a file or a model chose the value, GATE-URLFETCH is Yes (SEC-API-035). |
| `code-mcp` lists any file | It is an MCP server until read (GATE-MCP). |
| A recipe prints nothing for a stack that clearly has the feature | The recipe does not know your layout. Widen it and record that you did. A No also needs the owner's statement. |

## Glob and Grep patterns for an agent session

The hook allows `grep`, `find` and `git ls-files` with plain arguments, and the Glob and Grep tools. Use these when the shell recipes above cannot run.

| List | Glob or Grep |
|------|--------------|
| App router handlers | Glob `**/app/**/route.{ts,tsx,js,jsx,mjs}`, then Grep with `-o` for `export (async )?(function\|const) (GET\|POST\|PUT\|PATCH\|DELETE)` in those files |
| Pages router handlers | Glob `**/pages/api/**/*.{ts,tsx,js,jsx,mjs}` |
| Server actions | Grep files_with_matches for `use server` over `**/*.{ts,tsx,js,jsx}`, then read the first statement of each file |
| Express routes | Grep files_with_matches for `from 'express'`, then Grep count mode for `\.(get\|post\|put\|patch\|delete)\( *['"]/` in those files |
| Edge gates | Glob `**/{middleware,proxy}.{ts,js,mjs}` |
