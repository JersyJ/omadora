# Mirrors omacom/omarchy-pkgs pkgbuilds/owe-lockfeed (0.2.10-2).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           owe-lockfeed
Version:        0.2.10
Release:        2%{?dist}
Summary:        QML lock screen video feed for OWE
License:        MIT
URL:            https://github.com/omacom/owe
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/owe-%{version}.tar.gz
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
Requires:       qt6-qtdeclarative

%description
A QML module that displays OWE wallpaper video on the lock screen.

%prep
%autosetup -n owe-%{version}

%build
cmake -S qml-plugin -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=%{_prefix} -DCMAKE_INSTALL_LIBDIR=%{_lib}
cmake --build build

%install
DESTDIR=%{buildroot} cmake --install build

%check
ctest --test-dir build --output-on-failure

%files
%{_libdir}/qt6/qml/Owe/LockFeed

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.2.10-2
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 10 2026 kamm3r - 0.2.10-1
- Update to the release pinned in upstream 8787c23f.

* Tue Oct 06 2026 kamm3r - 0.2.9-1
- Update to the release pinned on upstream master.

* Mon Sep 28 2026 kamm3r - 0.2.7-1
- Port the upstream Omarchy lock screen feed to Fedora.
