# Mirrors omacom/omarchy-pkgs pkgbuilds/monologue (0.3.1-1).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           monologue
Version:        0.3.1
Release:        1%{?dist}
Summary:        Theme synced webcam recorder for Omarchy
License:        MIT
URL:            https://github.com/omacom/monologue
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtmultimedia-devel
Requires:       ffmpeg
Requires:       qt6-qtmultimedia
Requires:       xdg-desktop-portal
Requires:       hicolor-icon-theme

%description
Monologue records webcam video with Omarchy theme integration.

%prep
%autosetup

%build
./bin/build

%install
install -D -m 0755 build/monologue %{buildroot}%{_bindir}/monologue
install -D -m 0644 pkgbuild/monologue.desktop %{buildroot}%{_datadir}/applications/monologue.desktop
install -D -m 0644 pkgbuild/monologue.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/monologue.svg

%files
%license LICENSE
%{_bindir}/monologue
%{_datadir}/applications/monologue.desktop
%{_datadir}/icons/hicolor/scalable/apps/monologue.svg

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.3.1-1
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 10 2026 kamm3r - 0.3.1-1
- Update to the release pinned in upstream 8787c23f.

* Tue Oct 06 2026 kamm3r - 0.3.0-1
- Update to the release pinned on upstream master.

* Mon Sep 28 2026 kamm3r - 0.2.0-1
- Port the upstream Omarchy webcam recorder to Fedora.
