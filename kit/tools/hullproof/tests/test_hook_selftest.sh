#!/bin/sh
# Runs the read only hook self test (known bypass cases plus extra cases, both profiles). Exits nonzero on any failure.
# Usage: sh tools/hullproof/tests/test_hook_selftest.sh   (from the kit root, where .claude/hooks lives)
set -e
HOOK="${1:-.claude/hooks/hullproof-readonly-bash.mjs}"
node "$HOOK" --selftest
