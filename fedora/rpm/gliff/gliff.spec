# Mirrors omacom/omarchy-pkgs pkgbuilds/gliff (0.3.1-1).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}
%global _lto_cflags %{nil}

Name:           gliff
Version:        0.3.1
Release:        1%{?dist}
Summary:        Hyprland remote desktop over SSH
License:        MIT AND BSD-2-Clause
URL:            https://github.com/omacom/gliff
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-vendor-%{version}.tar.gz
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  nasm
BuildRequires:  libva-devel >= 2.20
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libadwaita-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(vulkan)
Requires:       hicolor-icon-theme
Requires:       dbus
Requires:       openssh
Requires:       vulkan-loader
ExclusiveArch:  x86_64

%description
Gliff streams a Hyprland desktop over SSH using GPU H.264 encoding with
4:4:4 color.

%prep
%autosetup -a 1

%build
export CARGO_TARGET_DIR=target
cargo build --frozen --release

%check
cargo test --frozen --release --workspace

%install
install -D -m 0755 target/release/gliff %{buildroot}%{_bindir}/gliff
install -D -m 0755 target/release/gliff-server %{buildroot}%{_bindir}/gliff-server
install -D -m 0755 target/release/gliff-probe %{buildroot}%{_bindir}/gliff-probe

install -Dm644 pkgbuild/gliff.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/gliff.svg
install -Dm644 pkgbuild/gliff.desktop %{buildroot}%{_datadir}/applications/gliff.desktop

%files
%license LICENSE NOTICE
%doc README.md docs/hardware-quirks.md
%{_bindir}/gliff
%{_bindir}/gliff-server
%{_bindir}/gliff-probe
%{_datadir}/icons/hicolor/scalable/apps/gliff.svg
%{_datadir}/applications/gliff.desktop

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.3.1-1
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 10 2026 kamm3r - 0.3.0-1
- Update to the release pinned in upstream 8787c23f.

* Sat Oct 03 2026 kamm3r - 0.2.0-1
- Update to upstream master's tagged release with VA-API support and desktop files.
- Run the upstream workspace tests.

* Tue Sep 30 2026 kamm3r - 0.1.0-1
- Port the upstream Omarchy recipe to Fedora.
