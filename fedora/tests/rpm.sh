#!/bin/bash

# Build the packages Omadora makes from this repository (omarchy,
# omarchy-settings, omadora-repos) and install them into this machine.
#
# Run as root in a disposable Fedora container (CI uses fedora:45). It packs
# each SRPM with fedora/rpm/build-srpm exactly as COPR does, rebuilds it, then
# installs the three RPMs with the repositories from fedora/repos, which
# exercises their dependencies, file conflicts and scriptlets.
#
# Usage: fedora/tests/rpm.sh [outdir]

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

cd "$FEDORA_ROOT"
load_lock

(( EUID == 0 )) || die "run as root in a disposable Fedora container"

out=$(realpath -m "${1:-$FEDORA_DIR/.build/rpm}")
rm -rf "$out"
mkdir -p "$out"

dnf -y -q install rpm-build rpmdevtools dnf5-plugins git-core patch rpmlint

for name in omadora-repos omarchy-settings omarchy; do
  info "Building $name"
  fedora/rpm/build-srpm "fedora/rpm/$name/$name.spec" "$out/srpm-$name"
  dnf -y -q builddep "$out/srpm-$name"/*.src.rpm
  rpmbuild --rebuild --define "_rpmdir $out" "$out/srpm-$name"/*.src.rpm
done

mapfile -t rpms < <(find "$out" -name '*.noarch.rpm' | sort)
printf '  %s\n' "${rpms[@]##*/}"

info "rpmlint (informational)"
rpmlint "${rpms[@]}" | tail -n 25 || :

info "Installing with Omadora's repositories"
install -m 0644 fedora/repos/*.repo /etc/yum.repos.d/
install -m 0644 -D -t /etc/dnf/repos.override.d fedora/repos/repos.override.d/*.repo
dnf -y -q install \
  "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$FEDORA_RELEASE.noarch.rpm" \
  "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$FEDORA_RELEASE.noarch.rpm"
dnf -y install --setopt=install_weak_deps=False "${rpms[@]}"

info "Checking the installed packages"
rpm -V omadora-repos omarchy-settings omarchy || die "rpm -V reports changed files"
for path in /usr/bin/omarchy /usr/share/omarchy/fedora/packages/map.tsv /etc/skel/.config/hypr \
            /usr/share/plymouth/themes/omarchy/omarchy.plymouth /etc/sudoers.d/omarchy-tzupdate \
            /etc/yum.repos.d/omadora.repo /etc/dnf/versionlock.toml; do
  [[ -e $path ]] || die "missing after install: $path"
done
[[ $(stat -c %a /etc/sudoers.d/omarchy-tzupdate) == "440" ]] || die "sudoers.d file is not 0440"
visudo -c >/dev/null || die "sudoers no longer parses"
grep -q '^deny = 10' /etc/security/faillock.conf || die "faillock override not applied"
grep -q 'Theme=omarchy' /etc/plymouth/plymouthd.conf || die "plymouth override not applied"
info "Packages build and install"
