# Mirrors omacom/omarchy-pkgs pkgbuilds/omarchy-emacs (1.10.1-1).

Name:           omarchy-emacs
Version:        1.10.1
Release:        1%{?dist}
Summary:        Emacs integration for Omarchy with automatic theme and font syncing
License:        MIT
URL:            https://github.com/scottjones/omarchy-emacs
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

# Arch's emacs-wayland is the pure-GTK (Wayland) build; Fedora calls it emacs-pgtk.
Requires:       emacs-pgtk
Requires:       bash

%description
Emacs configuration that follows Omarchy's theme and font: a theme generated
from the current Omarchy colors, hooks that re-theme Emacs on theme and font
changes, and setup and restart commands.

%prep
%autosetup -n %{name}-%{version}

%build
# Nothing to build.

%install
share=%{buildroot}%{_datadir}/omarchy-emacs
install -d "$share/config/themes"
install -m 0644 config/init.el config/omarchy.el config/shell-bashrc "$share/config/"
install -m 0644 config/themes/omarchy-theme.el "$share/config/themes/"
install -m 0644 omarchy-colors.el.tpl "$share/"
install -D -m 0755 hooks/font-set "$share/hooks/font-set"
install -D -m 0755 hooks/theme-set "$share/hooks/theme-set"
install -d %{buildroot}%{_bindir}
install -m 0755 bin/omarchy-emacs-setup bin/omarchy-emacs-sync-hooks bin/omarchy-restart-emacs bin/omarchy-install-emacs %{buildroot}%{_bindir}/

%files
%license LICENSE
%{_datadir}/omarchy-emacs
%{_bindir}/omarchy-emacs-setup
%{_bindir}/omarchy-emacs-sync-hooks
%{_bindir}/omarchy-restart-emacs
%{_bindir}/omarchy-install-emacs

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 1.10.1-1
- Package for Omadora, mirroring omarchy-pkgs.
