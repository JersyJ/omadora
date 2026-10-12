#!/bin/bash

# Run upstream's own test suites (test/all: the CLI suite and every
# test/shell.d file) against the assembled Fedora tree, the code Omadora ships.
#
# Some tests need tools or a desktop the machine running them may not have, so
# the same suites also run on pristine upstream (the pinned commit) in the same
# environment; only failures pristine upstream does not have count. Each of
# those is a deliberate Fedora difference listed with its reason in
# fedora/tests/upstream-expected-failures.txt. Fails when an unlisted test
# fails only on the Fedora tree, and when a listed test passes again (so the
# list stays honest).
#
# Usage: fedora/tests/upstream-tests.sh
# Needs: bash, git, jq, node (Fedora: dnf install jq nodejs).

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

cd "$FEDORA_ROOT"
load_lock

# Some upstream tests talk to whatever Hyprland or Quickshell they can reach.
# Inside a desktop session that is the user's own desktop, so refuse: run this
# in CI's container or a VM.
if [[ -n ${WAYLAND_DISPLAY:-}${HYPRLAND_INSTANCE_SIGNATURE:-}${DISPLAY:-} ]]; then
  die "refusing to run inside a graphical session: upstream's tests can reach the live desktop. Run it in CI or a VM."
fi

# As root, many upstream tests skip rather than act on the machine, so a root
# run would hide failures the expected list accounts for.
if (( EUID == 0 )); then
  die "run as an unprivileged user: as root, upstream's tests skip much of what they check"
fi

build="$FEDORA_DIR/.build"
fedora_tree="$build/upstream-tests-fedora"
pristine_tree="$build/upstream-tests-pristine"

"$FEDORA_DIR/build/assemble" --out "$fedora_tree" >/dev/null
# The tests and the trees they read live in the repository only.
git archive HEAD test docs agents manual plans AGENTS.md 2>/dev/null | tar -x -C "$fedora_tree"
rm -rf "$pristine_tree"
mkdir -p "$pristine_tree"
git archive "$UPSTREAM_COMMIT" | tar -x -C "$pristine_tree"

# Failed test files of one tree, one per line; the full output stays in
# $build/upstream-tests-<name>.log for triage.
failures() {
  local tree=$1 log="$build/upstream-tests-$2.log"

  (cd "$tree" && ./test/shell) >"$log" 2>&1 || true
  # test/shell ends with "N of M test files failed:" and one line per file.
  sed -n '/test files failed:$/,$p' "$log" | grep -oE 'test/shell\.d/[^ ]+-test\.sh' || true
  if ! (cd "$tree" && ./test/cli) >>"$log" 2>&1; then
    echo "test/cli"
  fi
}

info "Running upstream's test suites on pristine upstream (the baseline)"
mapfile -t baseline < <(failures "$pristine_tree" pristine | sort -u)
info "Running upstream's test suites on the assembled Fedora tree"
mapfile -t fedora < <(failures "$fedora_tree" fedora | sort -u)

mapfile -t failed < <(comm -23 <(printf '%s\n' "${fedora[@]}" | sed '/^$/d') <(printf '%s\n' "${baseline[@]}" | sed '/^$/d'))

expected_file="$FEDORA_DIR/tests/upstream-expected-failures.txt"
mapfile -t expected < <(grep -vE '^\s*(#|$)' "$expected_file" 2>/dev/null | awk '{ print $1 }' | sort -u)

unexpected=$(comm -23 <(printf '%s\n' "${failed[@]}" | sed '/^$/d') <(printf '%s\n' "${expected[@]}" | sed '/^$/d'))
# Listed files that now pass on the Fedora tree (a file that also fails on
# pristine upstream here proves nothing either way).
fixed=$(comm -13 <(printf '%s\n' "${fedora[@]}" | sed '/^$/d') <(printf '%s\n' "${expected[@]}" | sed '/^$/d'))

echo "  pristine upstream: ${#baseline[@]} failing files; Fedora tree: ${#fedora[@]}; Fedora only: ${#failed[@]}; listed: ${#expected[@]}"
status=0
if [[ -n $unexpected ]]; then
  echo "Failing only on the Fedora tree, and not listed:"
  for file in $unexpected; do
    echo "  $file"
    awk -v f="$file" '$0 ~ "^==> " f { show = 1; next } /^==> / { show = 0 } show && /^not ok/' "$build/upstream-tests-fedora.log" | head -n 5 | sed 's/^/      /'
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
