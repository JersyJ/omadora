#!/bin/bash

# Resolve Omarchy's package set on Fedora with only the allowed repositories.
#
# Run as root in a disposable Fedora container (CI uses fedora:45). Installs
# the repo files and version locks from fedora/repos, adds RPM Fusion, then asks
# dnf to install every package upstream's x86_64 lists map to, without
# installing anything. Fails when a package is missing or dependencies don't
# resolve, which also catches an includepkgs list that is too narrow.
#
# Packages for our COPR that have no recipe in fedora/rpm yet are skipped and
# listed; they can't resolve before they are built.

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

cd "$FEDORA_ROOT"
load_lock

(( EUID == 0 )) || die "run as root in a disposable Fedora container"
[[ $(rpm -E %fedora) == "$FEDORA_RELEASE" ]] || die "this is Fedora $(rpm -E %fedora); upstream.lock targets $FEDORA_RELEASE"

info "Installing repositories and version locks"
install -m 0644 fedora/repos/*.repo /etc/yum.repos.d/
install -m 0644 fedora/repos/versionlock.toml /etc/dnf/versionlock.toml
dnf -y -q install \
  "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$FEDORA_RELEASE.noarch.rpm" \
  "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$FEDORA_RELEASE.noarch.rpm"
install -m 0644 -D -t /etc/dnf/repos.override.d fedora/repos/repos.override.d/*.repo
dnf versionlock list

# includepkgs must actually take effect: every package a limited repository
# offers has to match one of its patterns. A typo in a section name would
# otherwise leave a repository unrestricted without any error.
info "Checking repository limits"
mapfile -t limited < <(awk -F= '/^\[/ { section = substr($0, 2, length($0) - 2) } /^includepkgs=/ { print section "=" $2 }' \
  fedora/repos/*.repo fedora/repos/repos.override.d/*.repo)
for entry in "${limited[@]}"; do
  repo=${entry%%=*}
  read -ra patterns <<<"${entry#*=}"
  dnf repo list --enabled --quiet "$repo" 2>/dev/null | grep -q . || continue
  offered=0
  while read -r name; do
    offered=$((offered + 1))
    matched=0
    for pattern in "${patterns[@]}"; do
      # shellcheck disable=SC2053 # the pattern is a glob on purpose
      if [[ $name == $pattern ]]; then
        matched=1
        break
      fi
    done
    (( matched )) || die "$repo offers $name, which its includepkgs does not allow; the limit is not applied"
  done < <(dnf repoquery --quiet --repo "$repo" --queryformat '%{name}\n' | sort -u)
  printf '  %-60s %d packages offered\n' "$repo" "$offered"
done

# Fedora package names for everything in upstream's lists, by source.
packages=()
skipped=()
# awk does the selection: bash's read would merge the empty columns of
# dropped packages, because tab counts as whitespace.
while read -r source name; do
  if [[ $source == "ours" && ! -d fedora/rpm/$name ]]; then
    skipped+=("$name")
  else
    packages+=("$name")
  fi
done < <(awk -F'\t' '
  NR == FNR { listed[$1] = 1; next }
  /^#/ || !($1 in listed) || $3 ~ /^(drop|todo|flatpak|mise:)/ { next }
  { n = split($2, names, " "); for (i = 1; i <= n; i++) print $3, names[i] }' <(upstream_package_names) fedora/packages/map.tsv)

(( ${#packages[@]} > 0 )) || die "no packages selected"
mapfile -t packages < <(printf '%s\n' "${packages[@]}" | sort -u)

info "Resolving ${#packages[@]} packages (${#skipped[@]} skipped: not built in our COPR yet)"
(( ${#skipped[@]} == 0 )) || printf '  skipped: %s\n' "${skipped[*]}"

log=$(mktemp)
dnf install --assumeno --allowerasing "${packages[@]}" >"$log" 2>&1 || true
if grep -qE '^(Problem|No match for argument|Failed to resolve)' "$log" || ! grep -q '^Transaction Summary' "$log"; then
  cat "$log"
  die "the package set does not resolve"
fi
sed -n '/^Transaction Summary/,/^$/p' "$log"

# Where packages come from, and anything that would touch what is installed:
# a third-party repository showing up here unexpectedly is worth a look.
info "Packages by repository"
awk '
  /^Package +Arch +Version +Repository/ { table = 1; next }
  /^Transaction Summary/ { table = 0 }
  !table { next }
  /^[A-Z][A-Za-z ]*:$/ { section = $0; next }
  /^ / && NF >= 5 && $1 != "replacing" && section != "" {
    repo = $4
    count[repo]++
    if (repo !~ /^(fedora|updates|updates-testing)$/) third[repo] = third[repo] " " $1
    if (section ~ /^(Upgrading|Replacing|Removing|Downgrading)/) touched = touched "\n  " section " " $1 " (" repo ")"
  }
  END {
    for (repo in count) printf "  %-60s %d\n", repo, count[repo]
    for (repo in third) printf "\n  %s:%s\n", repo, third[repo]
    if (touched != "") printf "\nChanges to installed packages:%s\n", touched
  }' "$log"

info "Package set resolves"
