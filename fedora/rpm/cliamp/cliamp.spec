# Mirrors omacom/omarchy-pkgs pkgbuilds/cliamp (2.3.0-2).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           cliamp
Version:        2.3.0
Release:        2%{?dist}
Summary:        Retro terminal music player
License:        MIT
URL:            https://github.com/bjarneo/cliamp
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-vendor-%{version}.tar.gz
BuildRequires:  golang >= 1.26.6
BuildRequires:  pkgconfig(alsa)
BuildRequires:  libogg-devel
BuildRequires:  libvorbis-devel
BuildRequires:  flac-devel
BuildRequires:  mpg123-devel
BuildRequires:  gcc
Requires:       alsa-lib
Requires:       ffmpeg
Requires:       yt-dlp
Requires:       hicolor-icon-theme

%description
Cliamp is a terminal music player inspired by Winamp, with local files and
online audio support.

%prep
%autosetup -a 1

%build
export CGO_ENABLED=1 GOTOOLCHAIN=local GOFLAGS=-mod=vendor
go build -trimpath -buildmode=pie -ldflags='-s -w -X main.version=v%{version} -linkmode=external' -o cliamp .

%install
install -D -m 0755 cliamp %{buildroot}%{_bindir}/cliamp
install -D -m 0644 cliamp.desktop %{buildroot}%{_datadir}/applications/cliamp.desktop
install -D -m 0644 Cliamp.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/cliamp.png
install -D -m 0644 Cliamp.png %{buildroot}%{_datadir}/pixmaps/cliamp.png

%files
%license LICENSE
%doc README.md
%{_bindir}/cliamp
%{_datadir}/applications/cliamp.desktop
%{_datadir}/icons/hicolor/512x512/apps/cliamp.png
%{_datadir}/pixmaps/cliamp.png

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 2.3.0-2
- Package for Omadora, based on kamm3r/omadora-pkg.

* Tue Oct 06 2026 kamm3r - 2.3.0-1
- Update to the release pinned on upstream master.

* Tue Sep 29 2026 kamm3r - 2.2.0-2
- Install development headers for the native audio decoders.

* Mon Sep 28 2026 kamm3r - 2.2.0-1
- Port the upstream Omarchy music player to Fedora with vendored Go modules.
