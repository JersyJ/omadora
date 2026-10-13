# Mirrors omacom/omarchy-pkgs pkgbuilds/hermes-desktop (2026.9.7-5): built
# from the release tag with the repository's own npm workspace (which fetches
# Electron and rebuilds node-pty, so the COPR build needs network access).
# Omarchy's Hermes installer seeds this prebuilt release into the user's
# Hermes checkout so its updater can rebuild it in place.
# Not registered in COPR and "todo" in the package map: its Vite build segfaults in the Fedora 45 build environment.

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
# The tag's commit: the app pins its first-launch bootstrap to it.
%global hermes_commit 2237be355906fbe6065ce1815711eee52b2d646e
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_check_rpaths %{nil}
%global _build_id_links none

Name:           hermes-desktop
Version:        2026.9.7
Release:        5%{?dist}
Summary:        Native desktop shell for Hermes Agent
License:        MIT
URL:            https://github.com/NousResearch/hermes-agent
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/hermes-desktop/hermes-desktop.sh
Source2:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/hermes-desktop/hermes-desktop.desktop
Source3:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/hermes-desktop/hermes-desktop.png
Source4:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/hermes-desktop/runtime.patch
Source5:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/hermes-desktop/runtime-test.py

ExclusiveArch:  x86_64
AutoReqProv:    no

# Vite's native bundler crashes under Fedora's default Node.js 22; build with 24.
BuildRequires:  nodejs24
BuildRequires:  nodejs24-npm
BuildRequires:  python3
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  git
BuildRequires:  ImageMagick

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       cairo
Requires:       dbus-libs
Requires:       expat
Requires:       curl
Requires:       gcc
Requires:       gdk-pixbuf2
Requires:       git
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
Requires:       make
Requires:       mesa-libgbm
Requires:       nodejs
Requires:       npm
Requires:       nspr
Requires:       nss
Requires:       pango
# The launcher runs /usr/bin/python, which Fedora ships apart from python3.
Requires:       /usr/bin/python
Requires:       systemd-libs
Requires:       util-linux
Requires:       xdg-utils

%description
Hermes Desktop is the native desktop shell for Nous Research's Hermes Agent.
A prebuilt release under /opt/hermes-desktop, with Omarchy's launcher.

%prep
%autosetup -n hermes-agent-%{version}

%build
mkdir -p ../node-bin
ln -sf %{_bindir}/node-24 ../node-bin/node
export PATH="$PWD/../node-bin:$PATH"
# Hermes refuses npm 11.10 to 11.16, which is what Fedora's Node.js 24 has;
# use a current npm, fetched with that one.
%{_bindir}/npm-24 install --prefix ../npm --no-audit --no-fund 'npm@>=11.17.0 <12'
ln -sf "$PWD/../npm/node_modules/npm/bin/npm-cli.js" ../node-bin/npm
ln -sf "$PWD/../npm/node_modules/npm/bin/npx-cli.js" ../node-bin/npx
node --version
npm --version
export GITHUB_SHA=%{hermes_commit}
export GITHUB_REF_NAME=main
# The desktop workspace resolves against the repository root.
npm ci
cd apps/desktop
npm run pack

%check
export PATH="$PWD/../node-bin:$PATH"
python3 "%{SOURCE5}" "$PWD" "%{SOURCE4}" "%{SOURCE1}"

%install
install -d %{buildroot}/opt/%{name}
cp -a apps/desktop/release/linux-unpacked/. %{buildroot}/opt/%{name}/
install -D -m 0755 "%{SOURCE1}" %{buildroot}%{_bindir}/%{name}
install -D -m 0644 scripts/install.sh %{buildroot}%{_datadir}/%{name}/install.sh
# Omarchy's installer still requires this patch; the release includes the fix,
# which the installer recognizes with a reverse-apply check.
install -D -m 0644 "%{SOURCE4}" %{buildroot}%{_datadir}/%{name}/runtime.patch
install -D -m 0644 "%{SOURCE2}" %{buildroot}%{_datadir}/applications/%{name}.desktop
install -D -m 0644 "%{SOURCE3}" %{buildroot}%{_datadir}/icons/hicolor/1024x1024/apps/%{name}.png
for size in 512 256 128 64 48; do
  install -d %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps
  magick "%{SOURCE3}" -resize "${size}x${size}" %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/%{name}.png
done
install -D -m 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE
install -D -m 0644 %{buildroot}/opt/%{name}/LICENSE.electron.txt %{buildroot}%{_licensedir}/%{name}/LICENSE.electron.txt
# The launcher requires the namespace sandbox, never a setuid helper.
chmod 0755 %{buildroot}/opt/%{name}/chrome-sandbox

%files
%license %{_licensedir}/%{name}/LICENSE
%license %{_licensedir}/%{name}/LICENSE.electron.txt
%{_bindir}/%{name}
/opt/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 2026.9.7-5
- Package for Omadora, mirroring omarchy-pkgs.
