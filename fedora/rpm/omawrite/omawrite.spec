# Mirrors omacom/omarchy-pkgs pkgbuilds/omawrite (0.6.0-2).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           omawrite
Version:        0.6.0
Release:        2%{?dist}
Summary:        Simple Markdown writing app built with Qt Quick
License:        MIT AND OFL-1.1
URL:            https://github.com/omacom-io/omawrite
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
Requires:       qt6-qtdeclarative
Requires:       xdg-desktop-portal
Requires:       hicolor-icon-theme

%description
Omawrite is a focused Markdown editor with Omarchy theme integration.

%prep
%autosetup

%build
./bin/build

%install
install -D -m 0755 build/omawrite %{buildroot}%{_bindir}/omawrite
install -D -m 0644 pkgbuild/omawrite.desktop %{buildroot}%{_datadir}/applications/omawrite.desktop
install -D -m 0644 pkgbuild/omawrite.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/omawrite.svg

%files
%license LICENSE
%license fonts/OFL.txt
%{_bindir}/omawrite
%{_datadir}/applications/omawrite.desktop
%{_datadir}/icons/hicolor/scalable/apps/omawrite.svg

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.6.0-2
- Package for Omadora, based on kamm3r/omadora-pkg.

* Tue Oct 06 2026 kamm3r - 0.6.0-1
- Update to the release pinned on upstream master.

* Mon Sep 28 2026 kamm3r - 0.5.0-1
- Port the upstream Omarchy Markdown editor to Fedora.
