# Mirrors omacom/omarchy-pkgs pkgbuilds/omacut (0.4.0-1).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           omacut
Version:        0.4.0
Release:        1%{?dist}
Summary:        Simple Qt video trimmer using FFmpeg
License:        MIT
URL:            https://github.com/omacom-io/omacut
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtmultimedia-devel
Requires:       ffmpeg
Requires:       qt6-qtmultimedia
Requires:       xdg-desktop-portal
Requires:       hicolor-icon-theme

%description
Omacut trims video clips with a small Qt Quick interface and FFmpeg.

%prep
%autosetup

%build
./bin/build

%install
install -D -m 0755 build/omacut %{buildroot}%{_bindir}/omacut
install -D -m 0644 pkgbuild/omacut.desktop %{buildroot}%{_datadir}/applications/omacut.desktop
install -D -m 0644 pkgbuild/omacut.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/omacut.svg

%files
%license LICENSE
%{_bindir}/omacut
%{_datadir}/applications/omacut.desktop
%{_datadir}/icons/hicolor/scalable/apps/omacut.svg

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.4.0-1
- Package for Omadora, based on kamm3r/omadora-pkg.

* Mon Sep 28 2026 kamm3r - 0.4.0-1
- Port the upstream Omarchy video trimmer to Fedora.
