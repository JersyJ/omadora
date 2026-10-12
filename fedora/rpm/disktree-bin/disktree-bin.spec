# Mirrors omacom/omarchy-pkgs pkgbuilds/disktree-bin (0.11.0-2).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           disktree-bin
Version:        0.11.0
Release:        2%{?dist}
Summary:        Treemap view of disk usage
License:        MIT
URL:            https://github.com/tobi/disktree
Source0:        %{url}/releases/download/v%{version}/disktree-%{version}-x86_64-linux.tar.gz#/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64
Provides:       disktree = %{version}-%{release}
Requires:       hicolor-icon-theme
Requires:       vulkan-loader

%description
Disktree visualizes disk usage as a treemap and helps identify files that take
up space.

%prep
%autosetup -n disktree-%{version}-x86_64-linux

%build
:

%install
install -D -m 0755 disktree %{buildroot}%{_bindir}/disktree
install -D -m 0644 disktree.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/disktree.svg
install -d %{buildroot}%{_datadir}/applications
sed -e 's|@BINDIR@/||' -e 's|@VERSION@|%{version}|' disktree.desktop.in >%{buildroot}%{_datadir}/applications/disktree.desktop
chmod 0644 %{buildroot}%{_datadir}/applications/disktree.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/disktree
%{_datadir}/applications/disktree.desktop
%{_datadir}/icons/hicolor/scalable/apps/disktree.svg

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.11.0-2
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 10 2026 kamm3r - 0.11.0-1
- Update to the release pinned in upstream 8787c23f.

* Mon Sep 28 2026 kamm3r - 0.10.1-1
- Repackage the upstream Omarchy Disktree release for Fedora.
