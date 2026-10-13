# Mirrors omacom/omarchy-pkgs pkgbuilds/once-bin (0.3.4-1).

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global debug_package %{nil}
%global __strip /bin/true

Name:           once-bin
Version:        0.3.4
Release:        1%{?dist}
Summary:        CLI/TUI for installing and managing self-hosted web applications
License:        MIT
URL:            https://github.com/basecamp/once
Source0:        %{url}/releases/download/v%{version}/once-linux-amd64#/once-%{version}-x86_64
Source1:        https://raw.githubusercontent.com/basecamp/once/v%{version}/MIT-LICENSE#/MIT-LICENSE-%{version}
Source2:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/once-bin/once-background.service

ExclusiveArch:  x86_64
Provides:       once = %{version}-%{release}
Conflicts:      once

BuildRequires:  systemd-rpm-macros
# Docker as Omadora installs it (moby-engine) or Docker's own docker-ce.
Requires:       /usr/bin/docker

%description
ONCE installs and manages self-hosted web applications from 37signals. The
once-background service runs its background tasks; Omarchy's ONCE installer
enables it.

%prep
%setup -q -c -T -n %{name}-%{version}

%build
# Nothing to build: the release binary.

%install
install -D -m 0755 "%{SOURCE0}" %{buildroot}%{_bindir}/once
install -D -m 0644 "%{SOURCE1}" %{buildroot}%{_licensedir}/%{name}/LICENSE
install -D -m 0644 "%{SOURCE2}" %{buildroot}%{_unitdir}/once-background.service

# Upstream's install hooks: restart the service on upgrade, stop and disable it
# on removal.
%post
%systemd_post once-background.service

%preun
%systemd_preun once-background.service

%postun
%systemd_postun_with_restart once-background.service

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/once
%{_unitdir}/once-background.service

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.3.4-1
- Package for Omadora, mirroring omarchy-pkgs.
