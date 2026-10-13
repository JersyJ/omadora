# Mirrors omacom/omarchy-pkgs pkgbuilds/claude-desktop (2.31226.1-1): Anthropic's
# own Debian package (the Linux beta ships only through it), repacked with
# Omarchy's launcher.

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_check_rpaths %{nil}
%global _build_id_links none

Name:           claude-desktop
Version:        2.31226.1
Release:        1%{?dist}
Summary:        Official Claude desktop app with Claude Code
License:        LicenseRef-proprietary
URL:            https://claude.ai
Source0:        https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop/claude-desktop_%{version}_amd64.deb
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/claude-desktop/claude-desktop-launcher.sh

ExclusiveArch:  x86_64
AutoReqProv:    no

BuildRequires:  bsdtar

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       bash
Requires:       glibc
Requires:       libgcc
Requires:       gtk3
Requires:       libdrm
Requires:       libnotify
Requires:       libsecret
Requires:       libxcb
Requires:       libXtst
Requires:       mesa-libgbm
Requires:       nss
Requires:       libuuid
Requires:       xdg-desktop-portal
Requires:       xdg-utils
Recommends:     gnome-keyring
# Claude Code sandboxing.
Recommends:     bubblewrap
Recommends:     socat
# Cowork runs tasks in a local virtual machine.
Suggests:       qemu-system-x86
Suggests:       edk2-ovmf
Suggests:       virtiofsd

%description
The official Claude desktop app, with Claude Code and Cowork. Anthropic's
Debian package, repacked with Omarchy's launcher, which starts it on Wayland
and reads extra flags from ~/.config/claude-desktop-flags.conf.

%prep
%setup -q -c -T -n %{name}-%{version}
bsdtar -xOf "%{SOURCE0}" data.tar.xz | bsdtar --no-same-owner -xf -

%build
# Nothing to build: Anthropic's release.

%install
cp -a usr %{buildroot}/
# Upstream's /usr/bin/claude-desktop is a bare link to the Electron binary;
# Omarchy's launcher picks the Wayland platform instead.
rm -f %{buildroot}%{_bindir}/claude-desktop
install -m 0755 "%{SOURCE1}" %{buildroot}%{_bindir}/claude-desktop
install -D -m 0644 usr/share/doc/claude-desktop/copyright %{buildroot}%{_licensedir}/%{name}/copyright
# Cowork probes Debian's paths for its virtual machine stack. Fedora's
# virtiofsd already lives at /usr/libexec/virtiofsd; point the firmware paths
# at Fedora's OVMF. The links dangle until edk2-ovmf is installed.
install -d %{buildroot}%{_datadir}/edk2
ln -s ovmf/OVMF_CODE.fd %{buildroot}%{_datadir}/edk2/OVMF_CODE_4M.fd
ln -s ovmf/OVMF_VARS.fd %{buildroot}%{_datadir}/edk2/OVMF_VARS_4M.fd
# Chromium's sandbox helper stays setuid root, as in Anthropic's package.
chmod 4755 %{buildroot}%{_prefix}/lib/claude-desktop/chrome-sandbox
# Debian package-policy files.
rm -rf %{buildroot}%{_docdir} %{buildroot}%{_datadir}/lintian

%files
%license %{_licensedir}/%{name}/copyright
%{_bindir}/claude-desktop
%{_prefix}/lib/claude-desktop
%{_datadir}/applications/com.anthropic.Claude.desktop
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/edk2/OVMF_CODE_4M.fd
%{_datadir}/edk2/OVMF_VARS_4M.fd

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 2.31226.1-1
- Package for Omadora, mirroring omarchy-pkgs.
