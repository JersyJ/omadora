# Starship comes from Arch's own repositories, not omarchy-pkgs, and Fedora 45
# has no maintained build (atim/starship stopped at Fedora 43). Built from the
# release tag with crates vendored into the SRPM by fedora/rpm/build-srpm.

%global debug_package %{nil}

Name:           starship
Version:        1.26.0
Release:        1%{?dist}
Summary:        Minimal, fast and customizable prompt for any shell
License:        ISC
URL:            https://github.com/starship/starship
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-vendor-%{version}.tar.gz
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  make

%description
Starship is a cross-shell prompt that shows the information you need while
you work: git status, language versions, command duration and more.

%prep
%autosetup -a 1

%build
export CARGO_TARGET_DIR=target
cargo build --frozen --release

%install
install -D -m 0755 target/release/starship %{buildroot}%{_bindir}/starship

%files
%license LICENSE
%doc README.md
%{_bindir}/starship

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 1.26.0-1
- Package for Omadora.
