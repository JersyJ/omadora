#!/bin/bash

# Static checks for the Fedora fork. CI runs this on every push and PR.
#
# Fails on: upstream drift, unmapped or malformed package entries, migrations
# missing a review row or changed since review, a failing assemble (unknown
# top-level path, drifted override, rejected patch), RPM recipes with unpinned
# sources or a stale omarchy-pkgs commit, and shellcheck errors.
# Reports, without failing: unreviewed migrations, optional package names
# used in scripts but not mapped yet, packages for our COPR without a recipe,
# and the remaining porting backlog.

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

# Every recipe pins its remote sources, and recipes built from omarchy-pkgs use
# the commit pinned in fedora/upstream.lock.
rpm_recipes_are_pinned() {
  local dir name commit status=0

  load_lock
  for dir in fedora/rpm/*/; do
    name=$(basename "$dir")
    if [[ ! -f $dir/$name.spec ]]; then
      echo "  $dir: missing $name.spec"
      status=1
    fi
    if [[ ! -f $dir/sources.sha256 ]]; then
      echo "  $dir: missing sources.sha256"
      status=1
    fi
    commit=$(sed -n 's/^%global pkgs_commit[[:space:]]\+//p' "$dir/$name.spec" 2>/dev/null)
    if [[ -n $commit && $commit != "$PKGS_COMMIT" ]]; then
      echo "  $name: pkgs_commit ${commit:0:10} differs from PKGS_COMMIT ${PKGS_COMMIT:0:10} in upstream.lock"
      status=1
    fi
  done
  return $status
}

# Every package mapped to a COPR, to our COPR ("ours") or to a vendor repository
# is allowed by that repository's includepkgs in fedora/repos.
repos_cover_map() {
  local bad

  bad=$(awk -F'\t' '
    FNR == 1 { file++ }
    file == 1 && /^\[/ { section = substr($0, 2, length($0) - 2) }
    file == 1 && /^includepkgs=/ {
      sub(/^includepkgs=/, "")
      n = split($0, names, " ")
      for (i = 1; i <= n; i++) allowed[section, names[i]] = 1
    }
    file == 2 && !/^#/ && $3 ~ /^(copr:|ours$|repo:)/ {
      section = $3
      if (section == "ours") section = "copr:jersyj/omadora"
      if (section ~ /^copr:/) { split(substr(section, 6), op, "/"); section = "copr:copr.fedorainfracloud.org:" op[1] ":" op[2] }
      if (section ~ /^repo:/) section = substr(section, 6) "-repo"
      n = split($2, names, " ")
      for (i = 1; i <= n; i++) if (!((section, names[i]) in allowed)) print $1 ": " names[i] " is not in includepkgs of [" section "]"
    }' <(cat fedora/repos/*.repo) fedora/packages/map.tsv)
  if [[ -n $bad ]]; then
    sed 's/^/  /' <<<"$bad"
    return 1
  fi
}

report_missing_recipes() {
  local missing

  missing=$(grep -v '^#' fedora/packages/map.tsv | awk -F'\t' '$3 == "ours" { print $2 }' | tr ' ' '\n' | sort -u |
    while read -r name; do [[ -d fedora/rpm/$name ]] || echo "$name"; done)
  echo "  $(grep -c . <<<"$missing") packages for our COPR have no recipe in fedora/rpm yet"
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
  shellcheck -x -S warning fedora/lib/common.sh fedora/bin/* fedora/build/assemble fedora/rpm/build-srpm fedora/tests/*.sh &&
    find fedora/overrides -type f -exec shellcheck -s bash -S warning {} +
}

check "Upstream-owned paths match the pinned upstream commit" fedora/bin/check-invariant
check "Package map is well-formed" package_map_is_valid
check "Every package in upstream's package lists is mapped" listed_packages_are_mapped
check "Every upstream migration has an up-to-date review row" fedora/bin/migrations-status --check
check "Fedora tree assembles (layout, exclusions, overrides, patches)" fedora/build/assemble --out "$FEDORA_DIR/.build/static-check"
check "Repository files allow every mapped package" repos_cover_map
check "RPM recipes pin their sources" rpm_recipes_are_pinned
check "Shellcheck" shellcheck_fedora_scripts

echo
info "Backlog (informational)"
report_optional_packages
report_missing_recipes
fedora/bin/port-status

echo
if (( failures > 0 )); then
  die "$failures check(s) failed"
fi
info "All checks passed"
