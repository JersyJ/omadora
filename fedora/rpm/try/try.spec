# Mirrors omacom/omarchy-pkgs pkgbuilds/tobi-try (1.10.1-2).
# Based on kamm3r/omadora-pkg (MIT).

Name:           try
Version:        1.10.1
Release:        2%{?dist}
Summary:        Fresh directories for every development experiment
License:        MIT
URL:            https://github.com/tobi/try
Source0:        https://github.com/tobi/try/archive/refs/tags/v%{version}.tar.gz#/try-%{version}.tar.gz
BuildArch:      noarch
Requires:       ruby
Provides:       tobi-try = %{version}-%{release}

%description
Try creates and manages fresh directories for short development experiments.

%prep
%autosetup -n try-%{version}

%build
sed -i '1c#!/usr/bin/ruby' try.rb

%install
install -D -m 0755 try.rb %{buildroot}%{_datadir}/%{name}/try.rb
install -D -m 0644 lib/tui.rb %{buildroot}%{_datadir}/%{name}/lib/tui.rb
install -D -m 0644 lib/fuzzy.rb %{buildroot}%{_datadir}/%{name}/lib/fuzzy.rb
install -d %{buildroot}%{_bindir}
ln -s ../share/%{name}/try.rb %{buildroot}%{_bindir}/try

%files
%license LICENSE
%doc README.md
%{_bindir}/try
%{_datadir}/%{name}

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 1.10.1-2
- Package for Omadora, based on kamm3r/omadora-pkg.

* Mon Sep 28 2026 kamm3r - 1.10.1-1
- Port the upstream Omarchy recipe to Fedora.
