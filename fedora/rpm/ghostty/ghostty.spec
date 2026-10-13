# Mirrors omacom/omarchy-pkgs pkgbuilds/ghostty (1.3.1-3): built from the
# release tarball with the exact Zig 0.15.2 toolchain Ghostty 1.3 requires,
# downloaded for the build only. Fetching Ghostty's Zig dependencies needs
# network access in the COPR build. Linked against Fedora's libraries.

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global zig_version 0.15.2
%global debug_package %{nil}

Name:           ghostty
Version:        1.3.1
Release:        3%{?dist}
Summary:        Fast, native, feature-rich terminal emulator
License:        MIT
URL:            https://github.com/ghostty-org/ghostty
Source0:        https://release.files.ghostty.org/%{version}/ghostty-%{version}.tar.gz
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/ghostty/build-data-llvm.patch
Source2:        https://ziglang.org/download/%{zig_version}/zig-x86_64-linux-%{zig_version}.tar.xz

ExclusiveArch:  x86_64

BuildRequires:  blueprint-compiler
BuildRequires:  curl
BuildRequires:  gettext
BuildRequires:  pkgconf-pkg-config
BuildRequires:  bzip2-devel
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  glib2-devel
BuildRequires:  gtk4-devel
BuildRequires:  gtk4-layer-shell-devel
BuildRequires:  harfbuzz-devel
BuildRequires:  libadwaita-devel
BuildRequires:  libpng-devel
BuildRequires:  oniguruma-devel
BuildRequires:  pixman-devel
BuildRequires:  wayland-devel
BuildRequires:  zlib-ng-compat-devel

Requires:       %{name}-shell-integration = %{version}-%{release}
Requires:       %{name}-terminfo = %{version}-%{release}
Suggests:       %{name}-nautilus

%description
Ghostty is a fast, native, feature-rich terminal emulator. Omarchy offers it
as an alternative default terminal.

%package shell-integration
Summary:        Shell integration scripts for Ghostty
BuildArch:      noarch

%description shell-integration
Shell integration scripts for Ghostty.

%package terminfo
Summary:        Terminfo for Ghostty
BuildArch:      noarch

%description terminfo
The xterm-ghostty terminfo entry. Fedora's ncurses-term already has the plain
"ghostty" entry, so only xterm-ghostty is shipped here.

%package nautilus
Summary:        Open in Ghostty for GNOME Files
License:        GPL-2.0-or-later
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Requires:       nautilus-python

%description nautilus
An "Open in Ghostty" context menu entry for GNOME Files.

%prep
%setup -q -n ghostty-%{version}
# Zig's native x86 linker cannot read .sframe relocations in crt1.o; use the
# bundled LLVM for the build-data helper, as the main executable does.
patch -Np1 -i "%{SOURCE1}"
mkdir -p ../zig
tar -xf "%{SOURCE2}" -C ../zig --strip-components=1
PATH="$PWD/../zig:$PATH" ZIG_GLOBAL_CACHE_DIR="$PWD/../zig-cache" ./nix/build-support/fetch-zig-cache.sh

%build
# A '-' suffix would select Ghostty's tip channel; the package revision goes
# into build metadata instead.
PATH="$PWD/../zig:$PATH" DESTDIR=build zig build \
  --prefix %{_prefix} \
  --system "$PWD/../zig-cache/p" \
  -Doptimize=ReleaseFast \
  -Dgtk-x11=true \
  -Dcpu=baseline \
  -Dpie=true \
  -Demit-docs=false \
  -Dversion-string="%{version}+omadora.%{release}" \
  --build-id=sha1

%install
cp -a build/. %{buildroot}/
install -D -m 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE
# Fedora's ncurses-term owns terminfo/g/ghostty.
rm -rf %{buildroot}%{_datadir}/terminfo/g
# Everything the build installed belongs to the main package, except what the
# subpackages take.
(cd %{buildroot} && find . \( -type f -o -type l \) -printf '/%%P\n' |
  grep -vE '^%{_datadir}/(ghostty/shell-integration|terminfo|nautilus-python)/' |
  grep -vxF '%{_licensedir}/%{name}/LICENSE' | sed 's/.*/"&"/') >ghostty.files

%files -f ghostty.files
%license %{_licensedir}/%{name}/LICENSE

%files shell-integration
%license %{_licensedir}/%{name}/LICENSE
%{_datadir}/ghostty/shell-integration

%files terminfo
%{_datadir}/terminfo/x/xterm-ghostty

%files nautilus
%{_datadir}/nautilus-python

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 1.3.1-3
- Package for Omadora, mirroring omarchy-pkgs.
