#!/bin/bash

# Run upstream's own test suites (test/all: the CLI suite and every
# test/shell.d file) against the assembled Fedora tree, the code Omadora ships.
#
# Upstream's tests check upstream's files; on the assembled tree, the fork's
# overrides and patches are what they meet. A test that fails because of a
# deliberate Fedora difference is listed with its reason in
# fedora/tests/upstream-expected-failures.txt. Fails when a test outside that
# list fails, and when a listed test passes again (so the list stays honest).
#
# Usage: fedora/tests/upstream-tests.sh
# Needs: bash, git, jq, node (Fedora: dnf install jq nodejs).

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

cd "$FEDORA_ROOT"
load_lock

tree="$FEDORA_DIR/.build/upstream-tests"
"$FEDORA_DIR/build/assemble" --out "$tree" >/dev/null
# The tests live in the repository only; give them the assembled tree to test.
git archive HEAD test docs agents manual plans AGENTS.md 2>/dev/null | tar -x -C "$tree"

log="$FEDORA_DIR/.build/upstream-tests.log"
# The full output stays in $log for triage.
info "Running upstream's test suites on the assembled tree"
(cd "$tree" && ./test/shell) >"$log" 2>&1 || true
(cd "$tree" && ./test/cli) >>"$log" 2>&1 || echo "FAILED-SUITE test/cli" >>"$log"

# test/shell ends with "N of M test files failed:" and one "  test/shell.d/<file>" line each.
mapfile -t failed < <(sed -n '/test files failed:$/,$p' "$log" | grep -oE 'test/shell\.d/[^ ]+-test\.sh' | sort -u)
grep -q '^FAILED-SUITE test/cli' "$log" && failed+=("test/cli")

expected_file="$FEDORA_DIR/tests/upstream-expected-failures.txt"
mapfile -t expected < <(grep -vE '^\s*(#|$)' "$expected_file" 2>/dev/null | awk '{ print $1 }' | sort -u)

unexpected=$(comm -23 <(printf '%s\n' "${failed[@]}" | sort -u | sed '/^$/d') <(printf '%s\n' "${expected[@]}" | sed '/^$/d'))
fixed=$(comm -13 <(printf '%s\n' "${failed[@]}" | sort -u | sed '/^$/d') <(printf '%s\n' "${expected[@]}" | sed '/^$/d'))

echo "  failed: ${#failed[@]}, expected to fail: ${#expected[@]}"
status=0
if [[ -n $unexpected ]]; then
  echo "Unexpected failures:"
  for file in $unexpected; do
    echo "  $file"
    awk -v f="$file" '$0 ~ "^==> " f { show = 1; next } /^==> / { show = 0 } show && /^not ok/' "$log" | head -n 5 | sed 's/^/      /'
  done
  status=1
fi
if [[ -n $fixed ]]; then
  echo "Listed as expected failures but passing now (remove them from $expected_file):"
  printf '  %s\n' $fixed
  status=1
fi
(( status == 0 )) && info "Upstream tests: no unexpected results"
exit "$status"
