# Mirrors omacom/omarchy-pkgs pkgbuilds/grok-bot (0.70.2-1): xAI's own Debian
# package (from Cursor's apt repository), repacked with Omarchy's launcher and
# desktop entry. Upstream's install hook only advises on kernels without
# unprivileged user namespaces; Fedora's kernel has them.

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_check_rpaths %{nil}
%global _build_id_links none

Name:           grok-bot
Version:        0.70.2
Release:        1%{?dist}
Summary:        Grok Bot desktop agent
License:        LicenseRef-proprietary
URL:            https://x.ai/bot
Source0:        https://downloads.cursor.com/aptrepo/pool/grok-bot/g/gr/grok-bot_%{version}_amd64.deb
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/grok-bot/grok-bot.sh
Source2:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/grok-bot/grok-bot.desktop

ExclusiveArch:  x86_64
AutoReqProv:    no
Provides:       sand = %{version}-%{release}
Conflicts:      sand

BuildRequires:  bsdtar

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       libnotify
Requires:       libsecret
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       nss
Requires:       libuuid
Requires:       xdg-utils
Recommends:     libappindicator-gtk3

%description
xAI's Grok Bot desktop agent, repacked with Omarchy's launcher, which starts it
on Wayland and reads extra flags from ~/.config/grok-bot-flags.conf.

%prep
%setup -q -c -T -n %{name}-%{version}
bsdtar -xOf "%{SOURCE0}" data.tar.xz | bsdtar -xf -

%build
# Nothing to build: the vendor's release.

%install
cp -a opt usr %{buildroot}/
rm -rf %{buildroot}%{_docdir} %{buildroot}%{_datadir}/applications/sand.desktop %{buildroot}%{_datadir}/applications/grok-bot.desktop
rm -f %{buildroot}%{_bindir}/grok-bot %{buildroot}%{_bindir}/sand
install -D -m 0755 "%{SOURCE1}" %{buildroot}%{_bindir}/grok-bot
ln -s grok-bot %{buildroot}%{_bindir}/sand
install -D -m 0644 "%{SOURCE2}" %{buildroot}%{_datadir}/applications/grok-bot.desktop
install -D -m 0644 "%{buildroot}/opt/Grok Bot/LICENSE.electron.txt" %{buildroot}%{_licensedir}/%{name}/LICENSE.electron.txt
install -D -m 0644 "%{buildroot}/opt/Grok Bot/LICENSES.chromium.html" %{buildroot}%{_licensedir}/%{name}/LICENSES.chromium.html
# Not setuid: Electron cannot run a setuid sandbox helper from a path with a
# space (electron#44414); it uses unprivileged user namespaces instead.
chmod 0755 "%{buildroot}/opt/Grok Bot/chrome-sandbox"

%files
%license %{_licensedir}/%{name}/LICENSE.electron.txt
%license %{_licensedir}/%{name}/LICENSES.chromium.html
%{_bindir}/grok-bot
%{_bindir}/sand
"/opt/Grok Bot"
%{_datadir}/applications/grok-bot.desktop
%{_datadir}/icons/hicolor/*/apps/*

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.70.2-1
- Package for Omadora, mirroring omarchy-pkgs.
