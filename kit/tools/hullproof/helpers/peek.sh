#!/bin/sh
# Print one line of a file with secret shaped values masked. Read only, POSIX sh, no dependencies beyond sed and awk.
#
# Usage: peek.sh FILE:LINE
#   Prints "FILE:LINE: <the line>" with these masked as [MASKED]: Stripe, GitHub, Slack and AWS key shapes, JWTs, private key headers,
#   passwords inside URLs, the value in an assignment to a name that contains secret, key, token, password or authorization,
#   and any run of 32 or more key characters. The line is cut at 300 characters. Nothing is written anywhere.
#   Use it instead of cat or sed when you need to see what is on a line of a file that may hold a secret. The owner runs it:
#   the audit hook gives agents no shell scripts.
# Exit: 0 printed, 1 the file has fewer lines, 2 usage error or unreadable file.
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: $0 FILE:LINE" >&2
  exit 2
fi
spec=$1
file=${spec%:*}
line=${spec##*:}
case "$line" in
  ''|*[!0-9]*) echo "error: LINE must be a number, give FILE:LINE" >&2; exit 2 ;;
esac
if [ "$file" = "$spec" ] || [ -z "$file" ] || [ "$line" -lt 1 ]; then
  echo "usage: $0 FILE:LINE (LINE starts at 1)" >&2
  exit 2
fi
[ -f "$file" ] && [ -r "$file" ] || { echo "error: $file is not a readable file" >&2; exit 2; }

total=$(awk 'END { print NR }' "$file")
if [ "$line" -gt "$total" ]; then
  echo "error: $file has $total lines" >&2
  exit 1
fi

# Case insensitive name words without GNU sed flags.
NAME='[A-Za-z0-9_.-]*([Ss][Ee][Cc][Rr][Ee][Tt]|[Kk][Ee][Yy]|[Tt][Oo][Kk][Ee][Nn]|[Pp][Aa][Ss][Ss]([Ww][Oo][Rr][Dd]|[Ww][Dd])?|[Aa][Uu][Tt][Hh][Oo][Rr][Ii][Zz][Aa][Tt][Ii][Oo][Nn]|[Bb][Ee][Aa][Rr][Ee][Rr])[A-Za-z0-9_.-]*'
awk -v n="$line" 'NR == n { print substr($0, 1, 300); exit }' "$file" | sed -E \
  -e 's/-----BEGIN [A-Z ]*PRIVATE KEY-----.*/-----BEGIN PRIVATE KEY-----[MASKED]/' \
  -e 's/(sk_(live|test)_)[A-Za-z0-9]+/\1[MASKED]/g' \
  -e 's/(gh[pousr]_)[A-Za-z0-9]+/\1[MASKED]/g' \
  -e 's/(xox[abprs]-)[A-Za-z0-9-]+/\1[MASKED]/g' \
  -e 's/AKIA[0-9A-Z]{12,}/AKIA[MASKED]/g' \
  -e 's/eyJ[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*/eyJ[MASKED]/g' \
  -e 's#(://[^:/@ ]+:)[^@ /]+@#\1[MASKED]@#g' \
  -e 's/([Bb]earer|[Bb]asic)[[:space:]]+[^[:space:]"'"'"']+/\1 [MASKED]/g' \
  -e "s/(${NAME}[\"']?[[:space:]]*[:=][[:space:]]*)\"[^\"]*\"/\\1\"[MASKED]\"/g" \
  -e "s/(${NAME}[\"']?[[:space:]]*[:=][[:space:]]*)'[^']*'/\\1'[MASKED]'/g" \
  -e "s/(${NAME}[\"']?[[:space:]]*[:=][[:space:]]*)[^\"'[:space:],;}]+/\\1[MASKED]/g" \
  -e 's/[A-Za-z0-9+\/=_-]{32,}/[MASKED]/g' \
  | sed -e "s|^|$file:$line: |"
