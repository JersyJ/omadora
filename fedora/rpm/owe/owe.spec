# Mirrors omacom/omarchy-pkgs pkgbuilds/owe (0.2.10-4).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           owe
Version:        0.2.10
Release:        4%{?dist}
Summary:        Wallpaper engine for Omarchy
License:        MIT
URL:            https://github.com/omacom/owe
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
%global pkgs_commit 87ed2a7e23db51c53bf6f45942e63f21b9b43920
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/owe/lock-policy-timestamp.patch
Source2:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/owe/package-restart
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(epoxy)
BuildRequires:  pkgconfig(mpv)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libswscale)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  systemd-rpm-macros
BuildRequires:  python3
BuildRequires:  mesa-dri-drivers
BuildRequires:  ffmpeg
Requires:       mpv
Requires:       ffmpeg
Requires:       socat
Requires(posttrans): systemd

%description
OWE renders still and video wallpapers and provides a user session daemon.

%prep
%autosetup
patch -Np1 -i "%{SOURCE1}"

%build
%meson
%meson_build

%install
%meson_install
install -D -m 0644 systemd/owed.service %{buildroot}%{_userunitdir}/owed.service
sed -i 's|%h/.local/bin/owed|%{_bindir}/owed|' %{buildroot}%{_userunitdir}/owed.service
install -D -m 0755 hooks/owe-idle %{buildroot}%{_bindir}/owe-idle
install -D -m 0644 hooks/theme-set.d/10-owe-sync %{buildroot}%{_datadir}/owe/10-owe-sync
install -D -m 0755 "%{SOURCE2}" %{buildroot}%{_libexecdir}/owe/package-restart

%check
%meson_test

%posttrans
# Restart only active sessions on upgrade, after systemd reloads user units.
if [ "$1" -gt 1 ]; then
  systemctl list-units 'user@*.service' --state=running --no-legend --plain | while read -r unit _; do
    user_id=${unit#user@}
    user_id=${user_id%.service}
    systemctl --user --machine="$user_id@.host" daemon-reload || :
  done
  %{_libexecdir}/owe/package-restart || :
fi

%files
%doc README.md
%doc config/config.toml
%{_bindir}/owe
%{_bindir}/owed
%{_bindir}/owe-render
%{_bindir}/owe-idle
%{_userunitdir}/owed.service
%{_datadir}/owe/10-owe-sync
%{_libexecdir}/owe/package-restart

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.2.10-4
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 10 2026 kamm3r - 0.2.10-1
- Update to the release pinned in upstream 8787c23f.

* Tue Oct 06 2026 kamm3r - 0.2.9-1
- Update to the release pinned on upstream master.

* Mon Sep 28 2026 kamm3r - 0.2.7-1
- Port the upstream Omarchy wallpaper engine to Fedora.
