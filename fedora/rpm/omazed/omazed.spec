# Mirrors omacom/omarchy-pkgs pkgbuilds/omazed (2.2.0-3).

Name:           omazed
Version:        2.2.0
Release:        3%{?dist}
Summary:        Live theme switching for Zed in Omarchy
License:        MIT
URL:            https://github.com/aps6/omazed
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       bash
Requires:       jq
Requires:       perl-interpreter

%description
Keeps the Zed editor's theme in step with Omarchy's system theme. Run
"omazed setup" once (Omarchy's Zed installer does) to install the theme hook.

%prep
%autosetup -n %{name}-%{version}

%build
# Nothing to build.

%install
# The scripts find their template next to themselves, so it goes into
# /usr/bin as upstream's package puts it.
install -D -m 0755 omazed %{buildroot}%{_bindir}/omazed
install -D -m 0755 omazed-generator.sh %{buildroot}%{_bindir}/omazed-generator.sh
install -D -m 0644 omazed-theme.tpl %{buildroot}%{_bindir}/omazed-theme.tpl
install -D -m 0755 omazed-font.sh %{buildroot}%{_bindir}/omazed-font.sh

%files
%license LICENSE
%doc README.md
%{_bindir}/omazed
%{_bindir}/omazed-generator.sh
%{_bindir}/omazed-theme.tpl
%{_bindir}/omazed-font.sh

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 2.2.0-3
- Package for Omadora, mirroring omarchy-pkgs.
