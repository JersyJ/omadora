# Mirrors omacom/omarchy-pkgs pkgbuilds/tzupdate. Crates are vendored into the
# SRPM by fedora/rpm/build-srpm. Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           tzupdate
Version:        3.1.0
Release:        1%{?dist}
Summary:        Set the system timezone using IP geolocation
License:        MIT
URL:            https://github.com/cdown/tzupdate
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-vendor-%{version}.tar.gz
BuildRequires:  cargo
BuildRequires:  rust

%description
Tzupdate looks up the timezone for the machine's public IP address and sets
the system timezone to it.

%prep
%autosetup -a 1

%build
export CARGO_TARGET_DIR=target
cargo build --frozen --release

%install
install -D -m 0755 target/release/tzupdate %{buildroot}%{_bindir}/tzupdate

%files
%license LICENSE
%doc README.md
%{_bindir}/tzupdate

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 3.1.0-1
- Package for Omadora, based on kamm3r/omadora-pkg.
