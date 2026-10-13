# Mirrors Arch's extra/umu-launcher (1.4.4-1). The build follows umu's own
# Fedora spec (packaging/rpm/umu-launcher.spec) with Arch's options: system
# pyzstd and urllib3, the Rust helper fetched by cargo during the build.

Name:           umu-launcher
Version:        1.4.4
Release:        1%{?dist}
Summary:        Launch non-Steam games with Proton
License:        GPL-3.0-only
URL:            https://github.com/Open-Wine-Components/umu-launcher
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  make
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  scdoc
BuildRequires:  git
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  libzstd-devel
BuildRequires:  python3-devel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  python3-hatchling
BuildRequires:  python3-hatch-vcs
BuildRequires:  python3-wheel
BuildRequires:  python3-pyzstd
BuildRequires:  python3-urllib3
BuildRequires:  python3-xlib

Requires:       python3
Requires:       python3-pyzstd
Requires:       python3-urllib3
Requires:       python3-xlib
# What Arch's package depends on for the Steam Runtime and Proton.
Requires:       bash
Requires:       curl
Requires:       dbus
Requires:       desktop-file-utils
Requires:       diffutils
Requires:       freetype
Requires:       gdk-pixbuf2
Requires:       hicolor-icon-theme
Requires:       lsof
Requires:       nss
Requires:       usbutils
Requires:       vulkan-loader
Requires:       xrandr
Requires:       zenity
Recommends:     python3-cbor2
Recommends:     python3-xxhash

%description
umu-launcher runs Windows games outside Steam with Proton inside the Steam
Runtime container, the way Steam itself does. Omarchy's Battle.net and Lutris
installers use it.

%prep
%autosetup -n %{name}-%{version}

%build
export CARGO_HOME="$PWD/.cargo"
./configure.sh --prefix=%{_prefix} --use-system-pyzstd --use-system-urllib
make

%install
export CARGO_HOME="$PWD/.cargo"
make DESTDIR=%{buildroot} PYTHONDIR=%{python3_sitelib} install
%py3_shebang_fix %{buildroot}%{_bindir}/umu-run

%files
%license LICENSE
%{_bindir}/umu-run
%{_mandir}/man*/umu*
%{python3_sitelib}/umu*

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 1.4.4-1
- Package for Omadora, mirroring Arch's umu-launcher with umu's own Fedora spec.
