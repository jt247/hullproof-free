#!/bin/sh
# Run the Hullproof scanners that are installed, with the kit's own configuration, and save each output with a small JSON beside it.
# POSIX sh. Installs nothing. Read only for the repository: every file is written to the output folder you name.
#
# Usage: scan.sh --out OUT_DIR [--allow-network] [REPO_PATH]
#   REPO_PATH        the repository to scan, default the current folder. It must be a git repository.
#   --out OUT_DIR    where the outputs go. Choose a folder outside the repository, so the working tree stays clean.
#   --allow-network  also run OSV Scanner, which sends package names to osv.dev. Without it OSV is skipped and said so.
#
# What runs (exactly the forms of the Tool chain table in tools/hullproof/helpers/agent-rules.md and the audit skill), each only when installed:
#   gitleaks git . --redact --no-banner --config <kit>/gitleaks.toml --ignore-gitleaks-allow      -> gitleaks-git.txt
#   gitleaks dir . --redact --no-banner --config <kit>/gitleaks.toml --ignore-gitleaks-allow      -> gitleaks-dir.txt
#   semgrep scan --config <kit>/rules --metrics=off                                              -> semgrep.txt
#   osv-scanner scan source -r .                                                                 -> osv-scanner.txt
# Beside each output NAME.txt goes NAME.meta.json with: commit, tree, tool, version, config_sha, files_scanned, files_tracked
# (plus output and exit_code). files_scanned is read from the scanner's own summary and is null when the tool does not print a file count.
# config_sha is the sha256 of the config file, or of the sorted per file sha256 list for the rules folder, or null when the tool has no kit config.
# files_tracked is the number of files git tracks at that commit. A scan that covered fewer files than that did not see everything.
#
# Safety. Before any git command it runs the same three counts as the audit skill on .git/config, and refuses to go on (exit 2)
# when a git command could run code from the folder: a key like fsmonitor, sshCommand, hooksPath, textconv, pager or editor,
# or a diff, filter or credential section. A remote URL with credentials is reported by count and the line is never printed.
# Semgrep text output contains matched source lines. The files are written with mode 600 in a folder with mode 700, and this script prints counts only.
# Exit: 0 finished (scanner findings do not change it, read exit_code in each JSON), 2 usage error or refused.
set -eu
umask 077

HERE=$(cd "$(dirname "$0")" && pwd)
OUT=""
NET=0
REPO=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --out) [ "$#" -ge 2 ] || { echo "usage: $0 --out OUT_DIR [--allow-network] [REPO_PATH]" >&2; exit 2; }; OUT=$2; shift 2 ;;
    --allow-network) NET=1; shift ;;
    -h|--help) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "error: unknown option $1" >&2; exit 2 ;;
    *) [ -z "$REPO" ] || { echo "error: one repository path only" >&2; exit 2; }; REPO=$1; shift ;;
  esac
done
[ -n "$OUT" ] || { echo "usage: $0 --out OUT_DIR [--allow-network] [REPO_PATH]" >&2; exit 2; }
REPO=$(cd "${REPO:-.}" 2>/dev/null && pwd) || { echo "error: repository path is not a folder" >&2; exit 2; }

# ---- refuse when the git configuration could run code (the three counts of the audit skill) ----
[ -e "$REPO/.git" ] || { echo "error: $REPO is not a git repository" >&2; exit 2; }
if [ -d "$REPO/.git" ]; then
  CONF="$REPO/.git/config"
  [ ! -e "$REPO/.git/config.worktree" ] || { echo "refused: .git/config.worktree exists, its content cannot be checked here" >&2; exit 2; }
else
  # .git is a file (worktree or submodule): follow its gitdir line to the main git folder
  GD=$(sed -n 's/^gitdir: //p' "$REPO/.git" | head -n 1)
  case "$GD" in /*) ;; *) GD="$REPO/$GD" ;; esac
  MAIN=$(cd "$GD/../.." 2>/dev/null && pwd) || { echo "refused: GIT CONFIG: NOT CHECKED (cannot reach the main git folder)" >&2; exit 2; }
  CONF="$MAIN/config"
fi
[ -f "$CONF" ] || { echo "refused: GIT CONFIG: NOT CHECKED (no config file at the expected place)" >&2; exit 2; }
C1=$(grep -c -i -E '^[ 	]*(fsmonitor|sshCommand|hooksPath|textconv|pager|editor)[ 	]*=' "$CONF" || true)
C2=$(grep -c -i -E '^\[(diff|filter|credential)[ "]|^\[(diff|filter|credential)\]' "$CONF" || true)
C3=$(grep -c -E '://[^/ ]*@' "$CONF" || true)
echo "git config counts: code running keys $C1, driver and credential sections $C2, remote URLs with credentials $C3"
if [ "$C1" -gt 0 ] || [ "$C2" -gt 0 ]; then
  echo "refused: a git command could run code from this folder (the first two counts must be 0). Check the folder, remove the entries, or scan a fresh clone." >&2
  exit 2
fi
[ "$C3" -eq 0 ] || echo "note: a remote URL holds embedded credentials. Treat that credential as exposed (ROTATION REQUIRED, a Pro edition requirement). The line is not printed."

# git runs with the user and system configuration switched off as well
GIT="git -C $REPO"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_OPTIONAL_LOCKS=0
COMMIT=$($GIT rev-parse HEAD 2>/dev/null) || { echo "error: no commit in $REPO" >&2; exit 2; }
TREE=$($GIT rev-parse 'HEAD^{tree}')
TRACKED=$($GIT ls-files -z | tr -cd '\000' | wc -c | tr -d ' ')

mkdir -p "$OUT"
chmod 700 "$OUT"
OUT=$(cd "$OUT" && pwd)
case "$OUT" in "$REPO"|"$REPO"/*) echo "warning: the output folder is inside the repository, which makes the working tree dirty" >&2 ;; esac

# kit paths as the scanner sees them: relative to the repository when the kit sits inside it, absolute otherwise
case "$HERE" in "$REPO"/*) KIT=${HERE#"$REPO"/} ;; *) KIT=$HERE ;; esac

sha256() { if command -v shasum >/dev/null 2>&1; then shasum -a 256; else sha256sum; fi | awk '{print $1}'; }
dir_sha() { (cd "$1" && find . -type f | LC_ALL=C sort | while read -r f; do sha256 < "$f"; done | sha256); }
json_str() { printf '%s' "$1" | tr -d '\000-\037' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }
json_or_null() { if [ -z "$1" ]; then printf 'null'; else printf '"%s"' "$(json_str "$1")"; fi; }
num_or_null() { case "$1" in ''|*[!0-9]*) printf 'null' ;; *) printf '%s' "$1" ;; esac; }

# run NAME TOOL VERSION_CMD CONFIG_SHA SCANNED_FROM_OUTPUT_CMD -- command words
run() {
  name=$1 tool=$2 vcmd=$3 csha=$4 counter=$5
  shift 5
  version=$($vcmd 2>&1 | tr -d '\033' | sed 's/\[[0-9;]*m//g' | grep -E -m 1 '[0-9]+\.[0-9]+' || true)
  : > "$OUT/$name.txt"
  chmod 600 "$OUT/$name.txt"
  set +e
  (cd "$REPO" && "$@") > "$OUT/$name.txt" 2>&1
  rc=$?
  set -e
  scanned=$(eval "$counter" < "$OUT/$name.txt" 2>/dev/null || true)
  {
    printf '{\n  "commit": "%s",\n  "tree": "%s",\n  "tool": "%s",\n  "version": %s,\n' "$COMMIT" "$TREE" "$tool" "$(json_or_null "$version")"
    printf '  "config_sha": %s,\n  "files_scanned": %s,\n  "files_tracked": %s,\n' "$(json_or_null "$csha")" "$(num_or_null "$scanned")" "$TRACKED"
    printf '  "output": "%s.txt",\n  "exit_code": %s\n}\n' "$name" "$rc"
  } > "$OUT/$name.meta.json"
  chmod 600 "$OUT/$name.meta.json"
  echo "ran $tool: exit $rc, output $name.txt, files_scanned ${scanned:-null} of $TRACKED tracked"
}

cfg_gl="$HERE/gitleaks.toml"
[ -f "$cfg_gl" ] && [ -d "$HERE/rules" ] || { echo "error: the kit configuration is missing next to this script" >&2; exit 2; }
SHA_GL=$(sha256 < "$cfg_gl")
SHA_RULES=$(dir_sha "$HERE/rules")

if command -v gitleaks >/dev/null 2>&1; then
  run gitleaks-git gitleaks "gitleaks version" "$SHA_GL" "echo" gitleaks git . --redact --no-banner --config "$KIT/gitleaks.toml" --ignore-gitleaks-allow
  run gitleaks-dir gitleaks "gitleaks version" "$SHA_GL" "echo" gitleaks dir . --redact --no-banner --config "$KIT/gitleaks.toml" --ignore-gitleaks-allow
else
  echo "skipped gitleaks: not installed (SEC-SECRETS-004 and a Pro edition requirement stay NOT ASSESSED)"
fi
if command -v semgrep >/dev/null 2>&1; then
  run semgrep semgrep "semgrep --version" "$SHA_RULES" "sed -n 's/.*Ran [0-9]* rules on \([0-9]*\) files\{0,1\}.*/\1/p' | head -n 1" semgrep scan --config "$KIT/rules" --metrics=off
else
  echo "skipped semgrep: not installed"
fi
if command -v osv-scanner >/dev/null 2>&1; then
  if [ "$NET" -eq 1 ]; then
    run osv-scanner osv-scanner "osv-scanner --version" "" "grep -c '^Scanned '" osv-scanner scan source -r .
  else
    echo "skipped osv-scanner: it sends package names to osv.dev, give --allow-network to run it"
  fi
else
  echo "skipped osv-scanner: not installed"
fi
echo "done. Outputs are in $OUT. Read the JSON files for exit codes and counts, and keep the .txt files out of chat and reports."
