# Mirrors Arch's extra/lazydocker (0.25.2-1): upstream's release binary,
# repacked (Arch builds the same release from source). The COPRs that carry it
# lag upstream: atim/lazydocker stopped at 0.23.3, rivenirvana/lazydocker at 0.24.4.

%global debug_package %{nil}
%global __strip /bin/true

Name:           lazydocker
Version:        0.25.2
Release:        1%{?dist}
Summary:        Terminal UI for Docker and Docker Compose
License:        MIT
URL:            https://github.com/jesseduffield/lazydocker
Source0:        %{url}/releases/download/v%{version}/lazydocker_%{version}_Linux_x86_64.tar.gz

ExclusiveArch:  x86_64

%description
A simple terminal UI for both Docker and Docker Compose. Omarchy opens it from
its Docker menu entry (omarchy-launch-docker-tui).

%prep
%setup -q -c -n %{name}-%{version}

%build
# Nothing to build: upstream's release binary.

%install
install -D -m 0755 lazydocker %{buildroot}%{_bindir}/lazydocker

%files
%license LICENSE
%doc README.md
%{_bindir}/lazydocker

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.25.2-1
- Package for Omadora from upstream's release binary, mirroring Arch's version.
