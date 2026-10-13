# Mirrors Arch's extra/uwsm (the uwsm Omarchy runs on Arch): the same release
# and the same optional scripts, uwsm-app among them. Omarchy launches every
# app through uwsm-app, which nett00n's Fedora build leaves out, and that build
# also misses the Python modules uwsm imports. Built here instead (DECISIONS.md,
# "uwsm").

Name:           uwsm
Version:        0.27.0
Release:        1%{?dist}
Summary:        Standalone Wayland session manager built on systemd
License:        MIT
URL:            https://github.com/Vladimir-csp/uwsm
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  meson
BuildRequires:  scdoc
BuildRequires:  python3-devel
BuildRequires:  systemd-rpm-macros
# meson checks that uwsm's Python modules import.
BuildRequires:  python3-dbus
BuildRequires:  python3-pyxdg

Requires:       bash
Requires:       python3
Requires:       python3-pyxdg
Requires:       python3-dbus
# uwsm runs waitpid (util-linux) to follow the compositor.
Requires:       /usr/bin/waitpid
# uwsm app reports launch failures through notify-send; "uwsm start select"
# uses whiptail.
Recommends:     libnotify
Recommends:     newt

%description
Universal Wayland Session Manager wraps a standalone Wayland compositor into a
set of systemd units, provides the session's environment to them and launches
applications as systemd units. Includes the uwsm-app, uuctl, fumon and
wait-tray helper scripts.

%prep
%autosetup -n %{name}-%{version}

%build
%meson -Duuctl=enabled -Dfumon=enabled -Duwsm-app=enabled -Dwait-tray=enabled
%meson_build

%install
%meson_install

%files
# meson installs the license, README and example units itself.
%license %{_datadir}/licenses/%{name}/LICENSE
%{_docdir}/%{name}/
%{_bindir}/uwsm
%{_bindir}/uwsm-app
%{_bindir}/uwsm-terminal
%{_bindir}/uwsm-terminal-service
%{_bindir}/uwsm-terminal-scope
%{_bindir}/uuctl
%{_bindir}/fumon
%{_bindir}/wait-tray
%{_userunitdir}/*
%{_userpresetdir}/80-fumon.preset
%{_libexecdir}/%{name}/
%{_datadir}/%{name}/
%{_datadir}/applications/uuctl.desktop
%{_mandir}/man1/*
%{_mandir}/man3/*

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.27.0-1
- Package for Omadora, mirroring Arch's build options (uwsm-app, uuctl, fumon,
  wait-tray).
