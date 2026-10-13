# Mirrors omacom/omarchy-pkgs pkgbuilds/voxtype-bin (1.1.0-2). Same release and
# binaries, taken from Voxtype's own signed release RPM, which Voxtype builds
# from the files upstream's PKGBUILD installs one by one; plus the
# "voxtype configure" launcher and desktop entry the PKGBUILD adds.

%global debug_package %{nil}
%global __strip /bin/true
%global __brp_check_rpaths %{nil}
%global _build_id_links none

Name:           voxtype-bin
Version:        1.1.0
Release:        2%{?dist}
Summary:        Push-to-talk voice-to-text for Linux (pre-built binaries)
License:        MIT
URL:            https://voxtype.io
Source0:        https://github.com/peteonrails/voxtype/releases/download/v%{version}/voxtype-%{version}-1.x86_64.rpm
Source1:        https://github.com/peteonrails/voxtype/releases/download/v%{version}/voxtype-%{version}-1.x86_64.rpm.asc
Source2:        https://raw.githubusercontent.com/peteonrails/voxtype/v%{version}/packaging/voxtype-configure.desktop
Source3:        https://raw.githubusercontent.com/peteonrails/voxtype/v%{version}/packaging/scripts/voxtype-configure-launcher
# Voxtype's CI release signing key, 9CCF7915B750CAE8B095ED1AA3FC9F33FD209279
# (the one upstream's PKGBUILD lists in validpgpkeys).
Source4:        voxtype-release-signing.asc

ExclusiveArch:  x86_64
AutoReqProv:    no
Provides:       voxtype = %{version}-%{release}
Conflicts:      voxtype

BuildRequires:  gnupg2
BuildRequires:  cpio

Requires:       glibc
Requires:       libgcc
Requires:       alsa-lib
Requires:       curl
# Voxtype records through ALSA; on PipeWire that needs the ALSA plugin.
Requires:       pipewire-alsa
Recommends:     wtype
Recommends:     wl-clipboard
Recommends:     libnotify
Recommends:     vulkan-loader
Recommends:     gtk4-layer-shell

%description
Voxtype is push-to-talk voice-to-text for Linux: hold a key, speak, and the
text is typed at the cursor. Fully offline transcription with Whisper or ONNX
engines; the /usr/bin/voxtype wrapper picks the binary that fits the CPU, and
"voxtype setup gpu --enable" switches to Vulkan.

%prep
%setup -q -c -T -n %{name}-%{version}
gpg --homedir "$PWD/.gnupg" --batch --quiet --import "%{SOURCE4}"
gpg --homedir "$PWD/.gnupg" --batch --verify "%{SOURCE1}" "%{SOURCE0}"
rpm2cpio "%{SOURCE0}" | cpio -idm --quiet
rm -rf usr/lib/.build-id

%build
# Nothing to build: Voxtype's release binaries.

%install
cp -a etc usr %{buildroot}/
install -D -m 0644 "%{SOURCE2}" %{buildroot}%{_datadir}/applications/voxtype-configure.desktop
install -D -m 0755 "%{SOURCE3}" %{buildroot}%{_bindir}/voxtype-configure-launcher

%post
# As Voxtype's own package does: the wrapper's SELinux label.
restorecon %{_bindir}/voxtype 2>/dev/null || :

%files
%config(noreplace) %{_sysconfdir}/voxtype/config.toml
%dir %{_sysconfdir}/voxtype
%{_bindir}/voxtype
%{_bindir}/voxtype-audio-bridge
%{_bindir}/voxtype-osd
%{_bindir}/voxtype-configure-launcher
%{_prefix}/lib/voxtype
%{_userunitdir}/voxtype.service
%{_datadir}/voxtype
%{_datadir}/applications/voxtype-configure.desktop
%{_datadir}/bash-completion/completions/voxtype
%{_datadir}/zsh/site-functions/_voxtype
%{_datadir}/fish/vendor_completions.d/voxtype.fish
%{_docdir}/voxtype

%changelog
* Tue Oct 13 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 1.1.0-2
- Package for Omadora from Voxtype's signed release RPM, mirroring omarchy-pkgs.
