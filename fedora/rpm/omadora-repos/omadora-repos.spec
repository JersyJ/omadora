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
install -d %{buildroot}%{_datadir}/omadora/repos/on-demand
install -m 0644 $repos/on-demand/*.repo %{buildroot}%{_datadir}/omadora/repos/on-demand/
install -m 0644 $repos/README.md %{buildroot}%{_datadir}/omadora/repos/README.md
install -m 0644 $repos/on-demand/README.md %{buildroot}%{_datadir}/omadora/repos/on-demand/README.md

%files
%license LICENSE
%config(noreplace) %{_sysconfdir}/yum.repos.d/*.repo
%config(noreplace) %{_sysconfdir}/dnf/repos.override.d/*.repo
%config(noreplace) %{_sysconfdir}/dnf/versionlock.toml
%{_datadir}/omadora

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - @VERSION@-@RELEASE@
- Package Omadora's repositories, limits and version locks.
