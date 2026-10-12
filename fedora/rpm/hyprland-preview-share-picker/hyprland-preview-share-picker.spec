# Mirrors omacom/omarchy-pkgs pkgbuilds/hyprland-preview-share-picker (0.2.1-3).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}
%global _protocols_commit 3a5c2bda1c1a4e55cc1330c782547695a93f05b2

Name:           hyprland-preview-share-picker
Version:        0.2.1
Release:        3%{?dist}
Summary:        Hyprland share picker with window and monitor previews
License:        MIT
URL:            https://github.com/WhySoBad/hyprland-preview-share-picker
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-vendor-%{version}.tar.gz
Source2:        https://github.com/hyprwm/hyprland-protocols/archive/%{_protocols_commit}.tar.gz#/hyprland-protocols-%{_protocols_commit}.tar.gz
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)
Requires:       hyprland
Requires:       xdg-desktop-portal-hyprland

%description
An alternative share picker for Hyprland with window and monitor previews.

%prep
%autosetup -a 1
tar -xzf %{SOURCE2}
rmdir lib/hyprland-protocols 2>/dev/null || true
ln -s ../hyprland-protocols-%{_protocols_commit} lib/hyprland-protocols
cat > build.rs <<'EOF'
fn main() {
    println!("cargo::rustc-env=GIT_VERSION=v%{version}-r0-release");
}
EOF

%build
export CARGO_TARGET_DIR=target
cargo build --frozen --release
./target/release/hyprland-preview-share-picker schema > schema.json

%install
install -D -m 0755 target/release/hyprland-preview-share-picker %{buildroot}%{_bindir}/hyprland-preview-share-picker
install -D -m 0644 schema.json %{buildroot}%{_datadir}/hyprland-preview-share-picker/schema.json

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprland-preview-share-picker
%{_datadir}/hyprland-preview-share-picker/schema.json

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.2.1-3
- Package for Omadora, based on kamm3r/omadora-pkg.

* Sat Oct 03 2026 kamm3r - 0.2.1-2
- Extract both dependency archives; repeated autosetup -a options only use the last.

* Tue Sep 30 2026 kamm3r - 0.2.1-1
- Port the upstream Omarchy recipe to Fedora.
