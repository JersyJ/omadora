# Mirrors omacom/omarchy-pkgs pkgbuilds/lmstudio-bin (0.4.26-1): LM Studio's
# release AppImage under /opt/lm-studio, run as an AppImage (FUSE 2).
# Not registered in COPR and "todo" in the package map: dropped from the extras for now (decided 2026-10-13).

%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global lmstudio_build 4
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_check_rpaths %{nil}
%global _build_id_links none

Name:           lmstudio-bin
Version:        0.4.26
Release:        1%{?dist}
Summary:        Desktop app for exploring and running large language models locally
License:        LicenseRef-proprietary
URL:            https://lmstudio.ai
Source0:        https://installers.lmstudio.ai/linux/x64/%{version}-%{lmstudio_build}/LM-Studio-%{version}-%{lmstudio_build}-x64.AppImage
Source1:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/lmstudio-bin/lmstudio.png
Source2:        https://raw.githubusercontent.com/omacom/omarchy-pkgs/%{pkgs_commit}/pkgbuilds/lmstudio-bin/lmstudio.desktop

ExclusiveArch:  x86_64
AutoReqProv:    no
Provides:       lmstudio = %{version}-%{release}
Conflicts:      lmstudio

Requires:       fuse-libs
Requires:       zlib
Requires:       hicolor-icon-theme
Requires:       gtk3
Requires:       nss
Requires:       libxcrypt-compat

%description
LM Studio runs large language models locally. The release AppImage, installed
under /opt/lm-studio with a desktop entry and the lm-studio command.

%prep
# Nothing to unpack: the AppImage runs as it is.

%build
# Nothing to build.

%install
install -D -m 0755 "%{SOURCE0}" %{buildroot}/opt/lm-studio/lm-studio.AppImage
install -D -m 0644 "%{SOURCE1}" %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/lmstudio-bin.png
install -D -m 0644 "%{SOURCE1}" %{buildroot}%{_datadir}/pixmaps/lmstudio-bin.png
install -D -m 0644 "%{SOURCE2}" %{buildroot}%{_datadir}/applications/ai.elementlabs.lmstudio.desktop
install -d %{buildroot}%{_bindir}
ln -s /opt/lm-studio/lm-studio.AppImage %{buildroot}%{_bindir}/lm-studio

%files
/opt/lm-studio
%{_bindir}/lm-studio
%{_datadir}/icons/hicolor/512x512/apps/lmstudio-bin.png
%{_datadir}/pixmaps/lmstudio-bin.png
%{_datadir}/applications/ai.elementlabs.lmstudio.desktop

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 0.4.26-1
- Package for Omadora, mirroring omarchy-pkgs.
