# Mirrors omacom/omarchy-pkgs pkgbuilds/ttfx (0.5.0-2).
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}

Name:           ttfx
Version:        0.5.0
Release:        2%{?dist}
Summary:        Terminal text effects as a Rust binary
License:        MIT
URL:            https://github.com/omacom/ttfx
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-vendor-%{version}.tar.gz
BuildRequires:  cargo
BuildRequires:  rust

%description
Terminal text effects for animations and screensavers.

%prep
%autosetup -a 1

%build
export CARGO_TARGET_DIR=target
cargo build --frozen --release

%install
install -D -m 0755 target/release/ttfx %{buildroot}%{_bindir}/ttfx
install -d %{buildroot}%{_datadir}/bash-completion/completions
target/release/ttfx --print-completion bash >%{buildroot}%{_datadir}/bash-completion/completions/ttfx
install -d %{buildroot}%{_datadir}/zsh/site-functions
target/release/ttfx --print-completion zsh >%{buildroot}%{_datadir}/zsh/site-functions/_ttfx

%files
%license LICENSE
%doc NOTICE README.md
%{_bindir}/ttfx
%{_datadir}/bash-completion/completions/ttfx
%{_datadir}/zsh/site-functions/_ttfx

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.5.0-2
- Package for Omadora, based on kamm3r/omadora-pkg.

* Mon Sep 28 2026 kamm3r - 0.5.0-1
- Port the upstream Omarchy recipe to Fedora with vendored Cargo dependencies.
