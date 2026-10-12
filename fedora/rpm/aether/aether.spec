# Mirrors omacom/omarchy-pkgs pkgbuilds/aether (4.32.0-2).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           aether
Version:        4.32.0
Release:        2%{?dist}
Summary:        Desktop theming application for Omarchy
License:        MIT
URL:            https://github.com/omacom/aether
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{url}/releases/download/v%{version}/aether-linux-amd64#/aether-linux-amd64-%{version}
ExclusiveArch:  x86_64
Requires:       gtk3
Requires:       webkit2gtk4.1

%description
Aether extracts colors from wallpapers and applies cohesive desktop themes.
This package uses the upstream Linux release binary and desktop resources.

%prep
%autosetup

%build

%install
install -D -m 0755 %{SOURCE1} %{buildroot}%{_bindir}/aether
install -D -m 0644 build/linux/aether.desktop %{buildroot}%{_datadir}/applications/aether.desktop
install -D -m 0644 li.oever.aether.url-handler.desktop %{buildroot}%{_datadir}/applications/li.oever.aether.url-handler.desktop
install -D -m 0644 icon.png %{buildroot}%{_datadir}/pixmaps/aether.png
install -D -m 0644 assets/aether-icon-512.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/aether.png

%files
%doc README.md
%{_bindir}/aether
%{_datadir}/applications/aether.desktop
%{_datadir}/applications/li.oever.aether.url-handler.desktop
%{_datadir}/pixmaps/aether.png
%{_datadir}/icons/hicolor/512x512/apps/aether.png

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 4.32.0-2
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 10 2026 kamm3r - 4.32.0-1
- Update to the release pinned in upstream 8787c23f.

* Tue Oct 06 2026 kamm3r - 4.31.1-1
- Update to the release pinned on upstream master.

* Mon Sep 28 2026 kamm3r - 4.30.0-1
- Port the upstream Omarchy release package to Fedora.
