# Omadora's package repositories, limits and version locks, so installed
# machines keep exactly the sources the kickstart used. Built from
# fedora/repos in the assembled tree; build-srpm fills @VERSION@ and @RELEASE@.
# fedora/repos/README.md describes each file.

%global omarchy_version @VERSION@
%global omarchy_release @RELEASE@

Name:           omadora-repos
Version:        %{omarchy_version}
Release:        %{omarchy_release}%{?dist}
Summary:        Package repositories, limits and version locks for Omadora
License:        MIT
URL:            https://github.com/JersyJ/omadora
Source0:        omarchy-%{omarchy_version}.tar.gz
BuildArch:      noarch

Requires:       dnf5
Requires:       rpmfusion-free-release
Requires:       rpmfusion-nonfree-release

%description
The repository files Omadora installs from: its own COPR, the Hyprland COPR,
single-app COPRs and mise, each limited with includepkgs to the packages
Omadora takes from it; the same limits for RPM Fusion; the dnf version locks
for Hyprland and Quickshell; and the on-demand repositories Omarchy's optional
installers add when needed.

%prep
%setup -q -n omarchy-%{omarchy_version}

%build
# Nothing to build.

%install
repos=fedora/repos
install -d %{buildroot}%{_sysconfdir}/yum.repos.d %{buildroot}%{_sysconfdir}/dnf/repos.override.d
install -m 0644 $repos/*.repo %{buildroot}%{_sysconfdir}/yum.repos.d/
install -m 0644 $repos/repos.override.d/*.repo %{buildroot}%{_sysconfdir}/dnf/repos.override.d/
install -m 0644 $repos/versionlock.toml %{buildroot}%{_sysconfdir}/dnf/versionlock.toml
install -d %{buildroot}%{_sysconfdir}/pki/rpm-gpg/omadora
install -m 0644 $repos/keys/*.asc %{buildroot}%{_sysconfdir}/pki/rpm-gpg/omadora/
install -d %{buildroot}%{_datadir}/omadora/repos/on-demand
install -m 0644 $repos/on-demand/*.repo %{buildroot}%{_datadir}/omadora/repos/on-demand/
install -m 0644 $repos/README.md %{buildroot}%{_datadir}/omadora/repos/README.md
install -m 0644 $repos/on-demand/README.md %{buildroot}%{_datadir}/omadora/repos/on-demand/README.md

%posttrans
# dnf asks before it trusts a repository's key, and dnf5-automatic (the daily
# security updates) cannot answer, so it would cancel every run on a fresh
# install. Import the local key files the enabled repositories name: ours,
# Fedora's and RPM Fusion's.
releasever=$(rpm -E %%fedora)
basearch=$(uname -m)
for key in $(sed -n 's/^gpgkey[[:space:]]*=[[:space:]]*//p' /etc/yum.repos.d/*.repo | tr ' ,' '\n\n' |
             sed -n 's|^file://||p' | sed "s/\$releasever/$releasever/g; s/\$basearch/$basearch/g" | sort -u); do
  if [ -f "$key" ]; then
    rpm --import "$key" || :
  fi
done

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/yum.repos.d/*.repo
%config(noreplace) %{_sysconfdir}/dnf/repos.override.d/*.repo
%config(noreplace) %{_sysconfdir}/dnf/versionlock.toml
%{_sysconfdir}/pki/rpm-gpg/omadora
%{_datadir}/omadora

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - @VERSION@-@RELEASE@
- Package Omadora's repositories, limits and version locks.
