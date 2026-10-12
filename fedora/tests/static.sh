#!/bin/bash

# Static checks for the Fedora fork. CI runs this on every push and PR.
#
# Fails on: upstream drift, unmapped or malformed package entries, migrations
# missing a review row or changed since review, a failing assemble (unknown
# top-level path, drifted override, rejected patch) and shellcheck errors.
# Reports, without failing: unreviewed migrations, optional package names
# used in scripts but not mapped yet, and the remaining porting backlog.

set -uo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

cd "$FEDORA_ROOT" || exit 1
failures=0

check() {
  local name=$1
  shift

  echo
  info "$name"
  if "$@"; then
    echo "  ok"
  else
    echo -e "  \033[31mFAILED\033[0m"
    failures=$((failures + 1))
  fi
}

package_map_is_valid() {
  local bad

  bad=$(grep -v '^#' fedora/packages/map.tsv | tail -n +2 | awk -F'\t' '
    NF != 4 { print "line " NR ": expected 4 tab-separated columns, got " NF; next }
    $3 !~ /^(fedora|copr:[^\/]+\/[^\/]+|rpmfusion-free|rpmfusion-nonfree|repo:[a-z0-9-]+|ours|flatpak|mise:[a-z0-9-]+|drop|todo)$/ { print $1 ": unknown source " $3 }
    $3 != "drop" && $3 != "todo" && $2 == "" { print $1 ": source " $3 " needs a Fedora name" }
    seen[$1]++ { print $1 ": mapped twice" }')
  if [[ -n $bad ]]; then
    sed 's/^/  /' <<<"$bad"
    return 1
  fi
}

listed_packages_are_mapped() {
  local missing todo

  missing=$(comm -23 <(upstream_package_names) <(mapped_package_names))
  todo=$(grep -v '^#' fedora/packages/map.tsv | awk -F'\t' '$3 == "todo" { print $1 }' | tr '\n' ' ')
  [[ -z $todo ]] || echo "  still todo: $todo"
  if [[ -n $missing ]]; then
    echo "  unmapped packages from install/*.packages:"
    sed 's/^/    /' <<<"$missing"
    return 1
  fi
}

report_optional_packages() {
  local unmapped

  unmapped=$(git grep -hoE 'omarchy-pkg-(add|aur-add|drop|present|missing)( +[a-z0-9][A-Za-z0-9@._+-]*)+' -- bin install migrations default shell |
    sed -E 's/^omarchy-pkg-[a-z-]+ +//' | tr ' ' '\n' | grep -E '^[a-z0-9][a-z0-9@._+-]*$' | sort -u |
    comm -23 - <(mapped_package_names))
  echo "  $(grep -c . <<<"$unmapped") package names used by optional installers are not mapped yet (Phase 1 backlog)"
}

shellcheck_fedora_scripts() {
  if ! command -v shellcheck >/dev/null 2>&1; then
    echo "  shellcheck not installed; skipped"
    return 0
  fi
  shellcheck -x -S warning fedora/lib/common.sh fedora/bin/* fedora/build/assemble fedora/tests/*.sh &&
    find fedora/overrides -type f -exec shellcheck -s bash -S warning {} +
}

check "Upstream-owned paths match the pinned upstream commit" fedora/bin/check-invariant
check "Package map is well-formed" package_map_is_valid
check "Every package in upstream's package lists is mapped" listed_packages_are_mapped
check "Every upstream migration has an up-to-date review row" fedora/bin/migrations-status --check
check "Fedora tree assembles (layout, exclusions, overrides, patches)" fedora/build/assemble --out "$FEDORA_DIR/.build/static-check"
check "Shellcheck" shellcheck_fedora_scripts

echo
info "Backlog (informational)"
report_optional_packages
fedora/bin/port-status

echo
if (( failures > 0 )); then
  die "$failures check(s) failed"
fi
info "All checks passed"
