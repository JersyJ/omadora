# Mirrors omacom/omarchy-pkgs pkgbuilds/herdr (0.9.1-1).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}
%global zigver 0.16.0

Name:           herdr
Version:        0.9.1
Release:        1%{?dist}
Summary:        Herdr terminal workspace manager for AI coding agents
License:        Apache-2.0
URL:            https://github.com/herdrdev/herdr
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        https://ziglang.org/download/%{zigver}/zig-x86_64-linux-%{zigver}.tar.xz
Source2:        https://ziglang.org/download/%{zigver}/zig-aarch64-linux-%{zigver}.tar.xz
Source3:        %{name}-vendor-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc

%description
Herdr terminal workspace manager for AI coding agents.

%prep
%autosetup -a 3

%build
case "%{_arch}" in
  x86_64) ZIG_TARBALL="%{SOURCE1}"; ZIG_DIR="zig-x86_64-linux-%{zigver}" ;;
  aarch64) ZIG_TARBALL="%{SOURCE2}"; ZIG_DIR="zig-aarch64-linux-%{zigver}" ;;
  *) echo "Unsupported arch %{_arch} for vendored Zig" >&2; exit 1 ;;
esac
tar -xf "$ZIG_TARBALL" -C .
export ZIG="$PWD/$ZIG_DIR/zig"
export ZIG_GLOBAL_CACHE_DIR="$PWD/zig-cache"
export CARGO_TARGET_DIR=target
cargo build --frozen --release

%install
install -D -m 0755 target/release/herdr %{buildroot}%{_bindir}/herdr

%files
%license LICENSE
%doc README.md
%{_bindir}/herdr

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.9.1-1
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 03 2026 kamm3r - 0.9.1-2
- Keep Cargo registry sources separate from upstream path dependencies.

* Wed Sep 30 2026 kamm3r - 0.9.1-1
- Port the upstream Omarchy Herdr recipe to Fedora.
