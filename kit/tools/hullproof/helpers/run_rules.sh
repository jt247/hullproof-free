#!/usr/bin/env bash
# Run the Hullproof Semgrep rule pack against a repository and print counts. Read only for the repository.
#
# Usage: run_rules.sh TARGET_REPO_PATH [LOCATIONS_JSON_PATH]
#   TARGET_REPO_PATH     repository to scan. Nothing is written inside it.
#   LOCATIONS_JSON_PATH  optional. Where to write the findings as rule, SEC IDs, severity hint,
#                        confidence, file and line. It holds no source text. Choose a path outside the repository.
#
# What it does, and why.
#   1. Works in a private temporary folder (mode 700) that is removed on exit. Nothing goes to a shared /tmp path.
#   2. Scans a clean copy of the repository's tracked and not ignored files, with an ignore file that names only
#      node_modules. The repository's own .semgrepignore, and Semgrep's default skipping of folders named test
#      or tests, cannot hide code from the scan. The kit's own tools/hullproof folder is left out. Inline nosemgrep comments are not honored, and their number is printed.
#   3. Writes Semgrep's JSON to the private folder and prints counts only. Matched code is never printed.
#      Semgrep's raw JSON can carry source lines for a logged in user, so it never leaves the private folder.
# Output: files scanned, rule count, findings per SEC ID, rule hits per rule, scan errors, nosemgrep comments.
# Counts are unique per file, line and SEC ID.
set -euo pipefail
umask 077

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: $0 TARGET_REPO_PATH [LOCATIONS_JSON_PATH]" >&2
  exit 2
fi
TARGET=$(cd "$1" 2>/dev/null && pwd) || { echo "error: $1 is not a directory" >&2; exit 2; }
LOCS=${2:-}
HERE=$(cd "$(dirname "$0")" && pwd)
RULES="$HERE/../rules"
# Folder of the kit's own rules and test fixtures, relative to the target, when the kit sits inside it. It holds
# intentionally bad code, so it is left out of the scan and a clean project shows zero. Check the kit itself with:
# shasum -a 256 -c docs/hullproof/.kit-manifest
KIT_DIR=""
case "$HERE" in "$TARGET"/*) KIT_DIR="${HERE#"$TARGET"/}"; KIT_DIR="${KIT_DIR%/helpers}" ;; esac
command -v semgrep >/dev/null || { echo "error: semgrep not installed" >&2; exit 2; }
command -v jq >/dev/null || { echo "error: jq not installed" >&2; exit 2; }

if [ -n "$LOCS" ]; then
  LOCS_DIR=$(cd "$(dirname "$LOCS")" 2>/dev/null && pwd) || { echo "error: folder of $LOCS does not exist" >&2; exit 2; }
  LOCS="$LOCS_DIR/$(basename "$LOCS")"
  case "$LOCS" in "$TARGET"/*) echo "warning: locations path is inside the target repo, choose a path outside it" >&2 ;; esac
fi

WORK=$(mktemp -d)
chmod 700 "$WORK"
trap 'rm -rf "$WORK"' EXIT
SRC="$WORK/src"
mkdir -p "$SRC"

# Copy tracked and not ignored files. Outside a git repository, copy everything except node_modules.
if git -C "$TARGET" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$TARGET" ls-files -z --cached --others --exclude-standard \
    | tar -C "$TARGET" --null -T - -cf - 2>/dev/null | tar -C "$SRC" -xf - 2>/dev/null || true
else
  echo "note: not a git repository, copying everything except node_modules" >&2
  tar -C "$TARGET" --exclude=node_modules -cf - . | tar -C "$SRC" -xf -
fi
[ -z "$KIT_DIR" ] || rm -rf "${SRC:?}/$KIT_DIR"
printf 'node_modules/\n' > "$SRC/.semgrepignore"

NOSEM=$( (grep -rIl --exclude-dir=node_modules -e 'nosem' "$SRC" 2>/dev/null || true) | wc -l | tr -d ' ')

(
  cd "$SRC"
  semgrep scan --config "$RULES" --metrics=off --disable-version-check --quiet --json \
    --disable-nosem --no-git-ignore --output "$WORK/semgrep.json" . >/dev/null 2>"$WORK/semgrep.err" || true
)
[ -s "$WORK/semgrep.json" ] || { echo "error: semgrep produced no output" >&2; exit 2; }

jq '[ .results[] | {rule: (.check_id | split(".") | last), sec_ids: .extra.metadata.sec_ids,
      severity_hint: .extra.metadata.severity_hint, confidence: .extra.metadata.confidence,
      file: (.path | sub("^\\./"; "")), line: .start.line} ]' "$WORK/semgrep.json" > "$WORK/locations.json"

[ -z "$LOCS" ] || cp "$WORK/locations.json" "$LOCS"

echo "FILES SCANNED $(jq '.paths.scanned | length' "$WORK/semgrep.json")"
echo "RULES $(cat "$RULES"/*.yaml | grep -c '^  - id:')"
echo "FINDINGS BY SEC ID"
jq -r '[ .[] | . as $r | $r.sec_ids[] | {sec: ., file: $r.file, line: $r.line} ] | unique
       | group_by(.sec) | map("  \(.[0].sec) \(length)") | if length == 0 then ["  none"] else . end | .[]' "$WORK/locations.json"
echo "RULE HITS"
jq -r 'group_by(.rule) | map("  \(.[0].rule) \(length)") | if length == 0 then ["  none"] else . end | .[]' "$WORK/locations.json"
echo "SCAN ERRORS $(jq '.errors | length' "$WORK/semgrep.json") (a partial parse means part of one file was skipped)"
jq -r '.errors | map(if type == "array" then .[0] else (.type | tostring) end) | group_by(.) | map("  \(.[0]) \(length)") | .[]' "$WORK/semgrep.json"
echo "FILES WITH NOSEM COMMENTS (not honored) $NOSEM (files in your project that contain a nosemgrep comment; the scan ignores the comment, so review those lines)"
