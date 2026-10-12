# Mirrors omacom/omarchy-pkgs pkgbuilds/hype (0.4.3-1).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           hype
Version:        0.4.3
Release:        1%{?dist}
Summary:        Markdown presentations with a visual slide editor
License:        MIT
URL:            https://github.com/omacom/hype
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  libwebp-devel
BuildRequires:  zlib-devel
Requires:       ffmpeg
Requires:       qt6-qtmultimedia
Requires:       qt6-qtimageformats
Requires:       qt6-qtsvg
Requires:       source-highlight
Requires:       xdg-desktop-portal
Requires:       hicolor-icon-theme

%description
Hype presents Markdown slides and provides a visual slide editor.

%prep
%autosetup

%build
./bin/build

%install
install -D -m 0755 build/hype %{buildroot}%{_bindir}/hype
install -D -m 0644 pkgbuild/hype.desktop %{buildroot}%{_datadir}/applications/hype.desktop
install -D -m 0644 pkgbuild/hype.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/hype.svg

%files
%license LICENSE
%doc README.md
%{_bindir}/hype
%{_datadir}/applications/hype.desktop
%{_datadir}/icons/hicolor/scalable/apps/hype.svg

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.4.3-1
- Package for Omadora, based on kamm3r/omadora-pkg.

* Mon Sep 28 2026 kamm3r - 0.4.3-1
- Port the upstream Omarchy presentation editor to Fedora.
