# Mirrors omacom/omarchy-pkgs pkgbuilds/omarchy-dev (the quattro package) over
# the assembled Fedora tree (fedora/build/assemble: overrides, patches and
# exclusions applied). build-srpm fills @VERSION@ and @RELEASE@.
#
# Hard dependencies follow the PKGBUILD's: only packages whose removal would
# brick the desktop. The kickstart installs the full default package set from
# install/omarchy-base.packages through fedora/packages/map.tsv.

%global omarchy_version @VERSION@
%global omarchy_release @RELEASE@

%global debug_package %{nil}
%global __brp_python_bytecompile %{nil}
%global __brp_mangle_shebangs %{nil}

# Commands omarchy-settings ships, because they are needed before this package
# or must outlive it.
%global settings_commands omarchy-debug omarchy-debug-idle omarchy-upload-log omarchy-sudo-passwordless omarchy-security-functions

Name:           omarchy
Version:        %{omarchy_version}
Release:        %{omarchy_release}%{?dist}
Summary:        Beautiful, modern and opinionated Hyprland desktop by DHH, on Fedora
License:        MIT
URL:            https://github.com/JersyJ/omadora
Source0:        omarchy-%{omarchy_version}.tar.gz
BuildArch:      noarch

Requires:       omarchy-settings = %{version}-%{release}
Requires:       omarchy-security-functions
Requires:       omadora-repos
# Wayland / Hyprland core
Requires:       hyprland
Requires:       quickshell
# Our own uwsm build (fedora/rpm/uwsm): it ships uwsm-app, which Omarchy
# launches every app through.
Requires:       uwsm >= 0.27.0
Requires:       /usr/bin/uwsm-app
# omarchy-shell lists keyboard layouts with xkbcli (in Arch's libxkbcommon)
Requires:       libxkbcommon-utils
# Arch's Hyprland requires Xwayland; nett00n's does not, and X11 apps need it
Requires:       xorg-x11-server-Xwayland
# omarchy-update records the update with script(1), which Arch ships in
# util-linux and Fedora in a subpackage
Requires:       util-linux-script
Requires:       sddm
Requires:       xdg-desktop-portal-hyprland
# Audio / auth / portal essentials
Requires:       wireplumber
Requires:       pipewire
Requires:       gnome-keyring
# Required by omarchy-* scripts and omarchy-shell
Requires:       gum
Requires:       jq
Requires:       git
Requires:       perl-interpreter
# Fedora splits Perl's core modules out of perl-interpreter; Arch's perl has
# them all. Clipboard history, omarchy-menu-select and omarchy-menu-input build
# JSON with these, and omarchy-games-retro-install uses the open pragma.
Requires:       perl(Encode)
Requires:       perl(JSON::PP)
Requires:       perl(open)
# Arch's tesseract depends on its orientation and script detection data
# (tesseract-data-osd); Fedora's does not, so tesseract --psm 0/1 would fail.
Requires:       (tesseract-osd if tesseract)
# Package management (pacman and pacman-contrib on Arch)
Requires:       dnf5
# omarchy-provision-user sets up the user directories with it
Requires:       xdg-user-dirs
# System font the UI assumes
Requires:       ttf-jetbrains-mono-nerd-basic
# Snapshots (Limine and its hooks on Arch; Fedora boots with GRUB)
Requires:       snapper

%description
The Omarchy runtime: every omarchy command, the install, hardware and
migration scripts, the themes, the Quickshell desktop shell, and Omadora's
Fedora package map, installed under /usr/share/omarchy with the commands in
/usr/bin.

%prep
%setup -q -n omarchy-%{omarchy_version}

%build
# Nothing to build.

%install
share=%{buildroot}%{_datadir}/omarchy
install -d %{buildroot}%{_bindir} "$share/bin"

: >%{_builddir}/omarchy.files
for command in bin/*; do
  [[ -f $command ]] || continue
  name=$(basename "$command")
  case " %{settings_commands} " in
    *" $name "*) continue ;;
  esac
  install -m 0755 "$command" %{buildroot}%{_bindir}/"$name"
  ln -s %{_bindir}/"$name" "$share/bin/$name"
  printf '%%s\n' %{_bindir}/"$name" %{_datadir}/omarchy/bin/"$name" >>%{_builddir}/omarchy.files
done

cp -a install themes migrations shell "$share/"
install -m 0644 version "$share/version"

# Omadora's runtime data: the Arch-to-Fedora package map the omarchy-pkg-*
# helpers read, and which commits this build came from.
install -d "$share/fedora/packages"
install -m 0644 fedora/packages/map.tsv "$share/fedora/packages/map.tsv"
install -m 0644 fedora/build-info "$share/fedora/build-info"
install -m 0644 fedora/pkg.sh "$share/fedora/pkg.sh"


# New users are already on this layout, so their migration markers are seeded.
install -d %{buildroot}%{_sysconfdir}/skel/.local/state/omarchy/migrations
for migration in migrations/*.sh; do
  : >%{buildroot}%{_sysconfdir}/skel/.local/state/omarchy/migrations/"$(basename "$migration")"
done

%files -f %{_builddir}/omarchy.files
%license LICENSE
%dir %{_datadir}/omarchy
%dir %{_datadir}/omarchy/bin
%{_datadir}/omarchy/install
%{_datadir}/omarchy/themes
%{_datadir}/omarchy/migrations
%{_datadir}/omarchy/shell
%{_datadir}/omarchy/version
%{_datadir}/omarchy/fedora
%dir %{_sysconfdir}/skel/.local/state/omarchy/migrations
%{_sysconfdir}/skel/.local/state/omarchy/migrations/*

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - @VERSION@-@RELEASE@
- Package omarchy for Omadora from the assembled Fedora tree.
