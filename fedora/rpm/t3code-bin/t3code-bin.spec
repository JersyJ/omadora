# Mirrors omacom/omarchy-pkgs pkgbuilds/t3code-bin (0.0.45-2): the release
# AppImage, unpacked under /usr/lib/t3code with Omarchy's launchers.
# Not registered in COPR and "todo" in the package map: dropped from the extras for now (decided 2026-10-13).

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_check_rpaths %{nil}
%global _build_id_links none

Name:           t3code-bin
Version:        0.0.45
Release:        2%{?dist}
Summary:        Open-source control plane for coding agents
License:        MIT
URL:            https://t3.codes
Source0:        https://github.com/pingdotgg/t3code/releases/download/v%{version}/T3-Code-%{version}-x86_64.AppImage
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/t3code-bin/t3code-launcher.sh
Source2:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/t3code-bin/t3-launcher.sh
Source3:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/t3code-bin/LICENSE

ExclusiveArch:  x86_64
AutoReqProv:    no
Provides:       t3code = %{version}-%{release}
Conflicts:      t3code

BuildRequires:  7zip

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       cairo
Requires:       dbus-libs
Requires:       expat
Requires:       libgcc
Requires:       glib2
Requires:       glibc
Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       cups-libs
Requires:       libnotify
Requires:       libX11
Requires:       libxcb
Requires:       libXcomposite
Requires:       libXdamage
Requires:       libXext
Requires:       libXfixes
Requires:       libxkbcommon
Requires:       libXrandr
Requires:       mesa-libgbm
Requires:       nspr
Requires:       nss
Requires:       pango
Requires:       systemd-libs
Requires:       xdg-utils

%description
T3 Code is an open-source control plane for coding agents such as Claude Code
and Codex. The release AppImage, unpacked, with Omarchy's t3code and t3
launchers.

%prep
%setup -q -c -T -n %{name}-%{version}
7z x "%{SOURCE0}" -osquashfs-root >/dev/null
cd squashfs-root
# The AppImage's usr/ holds only icons and libraries Fedora provides.
unexpected=$(find usr \( -type f -o -type l \) | grep -vE \
  '^usr/share/icons/hicolor/[0-9]+x[0-9]+/apps/t3code\.png$|^usr/lib/lib(Xss\.so\.1|Xtst\.so\.6|appindicator3?\.so\.1|gconf-2\.so\.4|indicator3?\.so\.7|notify\.so\.4)(\.[0-9]+)*$' || true)
[ -z "$unexpected" ] || { echo "Unexpected files in the AppImage's usr/ tree: $unexpected" >&2; exit 1; }

%build
# Nothing to build: the release AppImage.

%install
cd squashfs-root
for icon in usr/share/icons/hicolor/*/apps/t3code.png; do
  size=${icon#usr/share/icons/hicolor/}
  install -D -m 0644 "$icon" %{buildroot}%{_datadir}/icons/hicolor/${size%%%%/*}/apps/t3code.png
done
sed -e 's|^Exec=.*|Exec=t3code %%U|' -e 's|^Name=.*|Name=T3 Code|' -e '/^X-AppImage-Version=/d' \
  t3code.desktop >t3code.desktop.fedora
install -D -m 0644 t3code.desktop.fedora %{buildroot}%{_datadir}/applications/t3code.desktop
rm -rf AppRun .DirIcon usr t3code.desktop t3code.desktop.fedora t3code.png
install -d %{buildroot}%{_prefix}/lib/t3code
cp -a . %{buildroot}%{_prefix}/lib/t3code/
chmod -R a+rX %{buildroot}%{_prefix}/lib/t3code
chmod 4755 %{buildroot}%{_prefix}/lib/t3code/chrome-sandbox
install -D -m 0755 "%{SOURCE1}" %{buildroot}%{_bindir}/t3code
install -D -m 0755 "%{SOURCE2}" %{buildroot}%{_bindir}/t3
install -D -m 0644 "%{SOURCE3}" %{buildroot}%{_licensedir}/%{name}/LICENSE

%files
%license %{_licensedir}/%{name}/LICENSE
%{_bindir}/t3code
%{_bindir}/t3
%{_prefix}/lib/t3code
%{_datadir}/applications/t3code.desktop
%{_datadir}/icons/hicolor/*/apps/t3code.png

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.0.45-2
- Package for Omadora, mirroring omarchy-pkgs.
