# Mirrors omacom/omarchy-pkgs pkgbuilds/perplexity (26.10.1+build108257-1):
# Perplexity's own Debian package, repacked with Omarchy's launcher.

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_check_rpaths %{nil}
%global _build_id_links none

Name:           perplexity
Version:        26.10.1+build108257
Release:        1%{?dist}
Summary:        Official Perplexity desktop app
License:        LicenseRef-proprietary
URL:            https://www.perplexity.ai
# The download path spells the version's "+" as %%2B: bump it with Version (a
# stale one fails the checksum in sources.sha256).
Source0:        https://packages.perplexity.ai/deb/pool/main/p/perplexity/perplexity_26.10.1%%2Bbuild108257_amd64.deb#/perplexity_%{version}_amd64.deb
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/perplexity/perplexity-launcher.sh

ExclusiveArch:  x86_64
AutoReqProv:    no

BuildRequires:  bsdtar

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       bash
Requires:       bubblewrap
Requires:       cairo
Requires:       dbus-libs
Requires:       expat
Requires:       libgcc
Requires:       gdk-pixbuf2
Requires:       glib2
Requires:       glibc
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       cups-libs
Requires:       libdrm
Requires:       libglvnd
Requires:       libnotify
Requires:       libsecret
Requires:       libX11
Requires:       libxcb
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXext
Requires:       libXfixes
Requires:       libxkbcommon
Requires:       libXrandr
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       nspr
Requires:       nss
Requires:       pango
Requires:       systemd-libs
Requires:       libuuid
Requires:       vulkan-loader
Requires:       xdg-utils
Recommends:     libappindicator-gtk3

%description
The official Perplexity desktop app. Perplexity's Debian package, repacked with
Omarchy's launcher, which starts it on Wayland and reads extra flags from
~/.config/perplexity-flags.conf.

%prep
%setup -q -c -T -n %{name}-%{version}
bsdtar -xOf "%{SOURCE0}" data.tar.xz | bsdtar --no-same-owner -xf -
# The on-device model runtime's setup service, which upstream's package drops.
rm -rf lib
unexpected=$(find . -mindepth 1 -path ./opt -prune -o -path ./usr -prune -o -print)
[ -z "$unexpected" ] || { echo "Unexpected entries outside opt/ and usr/: $unexpected" >&2; exit 1; }

%build
# Nothing to build: Perplexity's release.

%install
cp -a opt usr %{buildroot}/
install -D -m 0755 "%{SOURCE1}" %{buildroot}%{_bindir}/perplexity
sed -i 's|^Exec=.*|Exec=perplexity %%U|' %{buildroot}%{_datadir}/applications/perplexity.desktop
chmod 4755 %{buildroot}/opt/Perplexity/chrome-sandbox
install -D -m 0644 %{buildroot}/opt/Perplexity/LICENSE.electron.txt %{buildroot}%{_licensedir}/%{name}/LICENSE.electron.txt
# Fedora confines with SELinux, not AppArmor; the profile stays in resources/.
rm -rf %{buildroot}%{_docdir}

%files
%license %{_licensedir}/%{name}/LICENSE.electron.txt
%{_bindir}/perplexity
/opt/Perplexity
%{_datadir}/applications/perplexity.desktop
%{_datadir}/icons/hicolor/*/apps/*

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 26.10.1+build108257-1
- Package for Omadora, mirroring omarchy-pkgs.
