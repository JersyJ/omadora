# Mirrors omacom/omarchy-pkgs pkgbuilds/omarchy-hyprland-titlebars (0.2.1-1).
# Based on whelanh/omarchy-fedora (MIT).

%global debug_package %{nil}
# A Hyprland plugin only loads into the exact Hyprland build it was compiled
# against (upstream: hyprland=0.56.2, rebuild_on: hyprland). Pin the binary
# package to the hyprland-devel in the build root; empty while packing the SRPM.
%global hyprland_evr %(rpm -q --qf '%%{VERSION}-%%{RELEASE}' hyprland-devel 2>/dev/null | grep -v 'not installed' || :)
%global _lto_cflags %{nil}

Name:           omarchy-hyprland-titlebars
Version:        0.2.1
Release:        1%{?dist}
Summary:        Titlebars for Omarchy's floating workspace mode

License:        BSD-3-Clause AND MIT
URL:            https://github.com/omacom/omarchy-hyprland-titlebars
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprland)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(xkbcommon)

%if "%{hyprland_evr}" != ""
Requires:       hyprland%{?_isa} = %{hyprland_evr}
%endif
Requires:       hyprlang
Requires:       hyprutils

ExclusiveArch:  x86_64

%description
A native Hyprland plugin that gives Omarchy's floating workspace mode its window
titlebars. It is loaded from the fixed path
/usr/lib/omarchy-hyprland-titlebars/titlebars.so and registers with Hyprland as
`hyprbars`. It must match the running Hyprland version and is rebuilt when
Hyprland changes.

%prep
%autosetup

%build
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=%{_prefix}
cmake --build build --verbose

%install
DESTDIR=%{buildroot} cmake --install build
install -Dm644 LICENSE %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
install -Dm644 LICENSE.MIT %{buildroot}%{_datadir}/licenses/%{name}/LICENSE.MIT

%files
%license %{_datadir}/licenses/%{name}/LICENSE
%license %{_datadir}/licenses/%{name}/LICENSE.MIT
%{_prefix}/lib/omarchy-hyprland-titlebars/titlebars.so

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.2.1-1
- Package for Omadora, based on whelanh/omarchy-fedora.

* Sun Oct 11 2026 whelanh <brickhousedevelopers@gmail.com> - 0.2.0-1
- Initial Fedora package: Omarchy Hyprland titlebars plugin (v0.2.0)
