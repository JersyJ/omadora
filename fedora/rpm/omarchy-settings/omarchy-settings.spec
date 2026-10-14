# Mirrors omacom/omarchy-pkgs pkgbuilds/omarchy-settings-dev (the quattro
# package) over the assembled Fedora tree: fedora/build/assemble has already
# applied the fork's overrides, patches and exclusions (no mkinitcpio, Limine,
# pacman or ALPM files; Fedora keeps its own nsswitch.conf, cups-files.conf
# and os-release). build-srpm fills @VERSION@ and @RELEASE@.
#
# ALPM hooks become scriptlets: the passwordless-sudo revoke and the Hyprland
# reload pause run in %%pre, the resume and grant cleanup in %%posttrans.

%global omarchy_version @VERSION@
%global omarchy_release @RELEASE@

%global debug_package %{nil}
%global __brp_python_bytecompile %{nil}
%global __brp_mangle_shebangs %{nil}

# Files other Fedora packages own: shipped under etc-overrides and copied into
# place by %%post, as upstream's .install does.
%global etc_overrides security/faillock.conf cups/cups-browsed.conf plymouth/plymouthd.conf

Name:           omarchy-settings
Version:        %{omarchy_version}
Release:        %{omarchy_release}%{?dist}
Summary:        Omarchy user defaults, /etc/skel content, fonts, Plymouth theme and support helpers
License:        MIT
URL:            https://github.com/JersyJ/omadora
Source0:        omarchy-%{omarchy_version}.tar.gz
Source1:        omarchy-settings-transition
Source2:        omadora-authselect
BuildArch:      noarch

BuildRequires:  ImageMagick
BuildRequires:  systemd-rpm-macros

Requires:       bash
Requires:       curl
Requires:       gum
Requires:       sudo
Requires:       hicolor-icon-theme
Requires:       plymouth
Requires:       plymouth-plugin-script
# Arch's plymouth carries its text renderers (label-freetype, label-pango);
# Fedora splits them out. Without them plymouth 26.134.222 turns its console
# viewer off and then crashes drawing the Omarchy theme on real displays
# (fixed upstream in 88c8dd8, after that release).
Requires:       plymouth-plugin-label
Requires:       abattis-cantarell-vf-fonts
Requires:       util-linux
# omadora-authselect, run by the pam_intune.so file triggers
Requires:       authselect
# Reads the password policy drop-in in /etc/security/pwquality.conf.d
Requires:       libpwquality
# Without the dictionary pwquality rejects every password (only a weak dependency)
Requires:       cracklib-dicts
# Updates: snapper pre/post snapshots around every dnf transaction (actions
# plugin), daily security updates, and snapshot boot entries in GRUB
# (/etc/dnf, /etc/dracut.conf.d from fedora/lib/runtime/etc)
Requires:       snapper
Requires:       libdnf5-plugin-actions
Requires:       dnf5-plugin-automatic
Requires:       grub-btrfs
Requires(pre):  coreutils
Requires(post): systemd
Requires(post): coreutils
# semodule, restorecon and selinuxenabled for the /etc/xkb label
Requires(post): policycoreutils
Requires(post): libselinux-utils
Requires(posttrans): fontconfig

Provides:       omarchy-security-functions = %{version}-%{release}

%description
Everything that has to be on the system before the omarchy package and before
the first user is created: /etc/skel defaults, /etc drop-ins, systemd user
units, fonts, the Plymouth and SDDM themes, branding, the debug helpers, and
the temporary passwordless-sudo helper with its boot-time cleanup.

%prep
%setup -q -n omarchy-%{omarchy_version}

%build
# Nothing to build.

%install
share=%{buildroot}%{_datadir}/omarchy
skel=%{buildroot}%{_sysconfdir}/skel

# /etc/skel/.config and the resync source.
install -d "$skel/.config" "$share/config"
cp -a config/. "$skel/.config/"
cp -a config/. "$share/config/"

install -D -m 0644 etc/fastfetch/config.jsonc %{buildroot}%{_sysconfdir}/fastfetch/config.jsonc

# Package-owned defaults with real system/XDG locations.
install -D -m 0644 default/uwsm/env.d/10-omarchy %{buildroot}%{_datadir}/uwsm/env.d/10-omarchy
install -D -m 0644 default/environment.d/10-omarchy-fcitx.conf %{buildroot}%{_prefix}/lib/environment.d/10-omarchy-fcitx.conf
install -D -m 0644 default/fontconfig/conf.avail/50-omarchy.conf %{buildroot}%{_datadir}/fontconfig/conf.avail/50-omarchy.conf
install -d %{buildroot}%{_sysconfdir}/fonts/conf.d
ln -sfn %{_datadir}/fontconfig/conf.avail/50-omarchy.conf %{buildroot}%{_sysconfdir}/fonts/conf.d/50-omarchy.conf
install -D -m 0644 default/xdg-terminal-exec/hyprland-xdg-terminals.list %{buildroot}%{_datadir}/xdg-terminal-exec/hyprland-xdg-terminals.list
# Fedora's shared-mime-info owns /usr/share/applications/mimeapps.list. The
# desktop-specific list in the same directory takes precedence over it in the
# Hyprland session (XDG_CURRENT_DESKTOP=Hyprland) and leaves other desktops alone.
install -D -m 0644 default/applications/mimeapps.list %{buildroot}%{_datadir}/applications/hyprland-mimeapps.list
for unit in bt-agent omarchy-sleep-lock omarchy-recover-internal-monitor omarchy-migrate-notify \
            omarchy-tailscale-receive omarchy-fcitx5 omarchy-crash-watch \
            omarchy-brightness-keyboard-auto omarchy-usb-authorization omarchy-thunderbolt-authorization; do
  [[ -f default/systemd/user/$unit.service ]] || continue
  install -D -m 0644 "default/systemd/user/$unit.service" %{buildroot}%{_userunitdir}/"$unit.service"
done
ln -sfn omarchy-migrate-notify.service %{buildroot}%{_userunitdir}/omarchy-update-user-notify.service
install -D -m 0644 default/systemd/user/app.slice.d/10-oomd.conf %{buildroot}%{_userunitdir}/app.slice.d/10-oomd.conf
install -D -m 0644 default/systemd/zram-generator.conf.d/90-omarchy.conf %{buildroot}%{_prefix}/lib/systemd/zram-generator.conf.d/90-omarchy.conf
install -D -m 0644 default/systemd/system/plocate-updatedb.service.d/10-omarchy.conf %{buildroot}%{_unitdir}/plocate-updatedb.service.d/10-omarchy.conf

# applications/** for the resync and install commands.
install -d "$share/applications"
cp -a applications/. "$share/applications/"
rm -rf "$share/applications/icons"

# The /etc tree, minus the files other packages own.
cp -a etc/. %{buildroot}%{_sysconfdir}/
install -d "$share/etc-overrides"
for path in %{etc_overrides}; do
  mv %{buildroot}%{_sysconfdir}/"$path" "$share/etc-overrides/${path//\//-}"
done
rmdir %{buildroot}%{_sysconfdir}/security %{buildroot}%{_sysconfdir}/cups %{buildroot}%{_sysconfdir}/plymouth 2>/dev/null || :
install -m 0644 default/bashrc "$share/etc-overrides/dot.bashrc"
# Omadora's own system configuration (fedora/lib/runtime/etc).
cp -a fedora/etc/. %{buildroot}%{_sysconfdir}/
chmod 0644 "$share/etc-overrides"/*

# /etc/skel/.local/share/applications.
install -d "$skel/.local/share/applications"
cp applications/*.desktop "$skel/.local/share/applications/"
if compgen -G 'applications/hidden/*.desktop' >/dev/null; then
  cp applications/hidden/*.desktop "$skel/.local/share/applications/"
fi

# Application icons in hicolor, named as upstream does.
install -d %{buildroot}%{_datadir}/icons/hicolor/{256x256,48x48,scalable}/apps
for icon in applications/icons/*; do
  [[ -f $icon ]] || continue
  icon_name=$(basename "$icon")
  icon_id=$(printf '%%s\n' "${icon_name%%.*}" | tr '[:upper:]' '[:lower:]' | sed 's/[^[:alnum:]]\+/-/g; s/^-//; s/-$//')
  case $icon_name in
    *.svg)
      install -m 0644 "$icon" %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/"$icon_id.svg"
      ;;
    *)
      for size in 256 48; do
        magick "$icon" -thumbnail ${size}x${size} -background transparent -gravity center -extent ${size}x${size} \
          "PNG32:%{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/$icon_id.png"
      done
      ;;
  esac
done

# default/** and the Snapper template.
install -d "$share/default"
cp -a default/. "$share/default/"
install -D -m 0644 default/snapper/root %{buildroot}%{_sysconfdir}/snapper/config-templates/omarchy

# SDDM theme and session. Fedora packages may not install to /usr/local, so the
# session goes to /usr/share/wayland-sessions, which SDDM reads as well.
install -d %{buildroot}%{_datadir}/sddm/themes
cp -a default/sddm/omarchy %{buildroot}%{_datadir}/sddm/themes/
install -m 0644 default/sddm/hyprland.lua %{buildroot}%{_datadir}/sddm/hyprland.lua
install -D -m 0644 default/wayland-sessions/omarchy.desktop %{buildroot}%{_datadir}/wayland-sessions/omarchy.desktop

# Plymouth theme.
install -d %{buildroot}%{_datadir}/plymouth/themes/omarchy
cp -a default/plymouth/. %{buildroot}%{_datadir}/plymouth/themes/omarchy/

# System font.
install -D -m 0644 default/fonts/omarchy/omarchy.ttf %{buildroot}%{_datadir}/fonts/omarchy/omarchy.ttf

# systemd sleep hook.
install -D -m 0755 default/systemd/system-sleep/unmount-fuse %{buildroot}%{_prefix}/lib/systemd/system-sleep/unmount-fuse

# Temporary passwordless sudo: the grant command and its library live here.
install -d %{buildroot}%{_bindir} "$share/bin"
for helper in omarchy-sudo-passwordless omarchy-security-functions; do
  install -m 0755 "bin/$helper" %{buildroot}%{_bindir}/"$helper"
  ln -s %{_bindir}/"$helper" "$share/bin/$helper"
done
install -D -m 0755 %{SOURCE1} %{buildroot}%{_libexecdir}/omadora/omarchy-settings-transition
install -D -m 0755 %{SOURCE2} %{buildroot}%{_libexecdir}/omadora/omadora-authselect

# Branding.
install -m 0644 logo.txt logo.svg icon.txt icon.png "$share/"
install -D -m 0644 icon.png %{buildroot}%{_datadir}/pixmaps/omarchy.png
install -D -m 0644 icon.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/omarchy.png
install -D -m 0644 logo.txt "$skel/.config/omarchy/branding/screensaver.txt"
install -D -m 0644 icon.txt "$skel/.config/omarchy/branding/about.txt"

# Other per-user defaults seeded through /etc/skel.
install -D -m 0644 default/hypr/toggles/flags.lua "$skel/.local/state/omarchy/toggles/hypr/flags.lua"
install -D -m 0644 default/nautilus-python/extensions/localsend.py "$skel/.local/share/nautilus-python/extensions/localsend.py"
install -D -m 0644 default/nautilus-python/extensions/transcode.py "$skel/.local/share/nautilus-python/extensions/transcode.py"
install -D -m 0644 default/tensaku/state.toml "$skel/.local/state/tensaku/state.toml"

# Fedora compatibility: Omarchy calls Chromium `chromium` and its entry
# chromium.desktop; Fedora's are chromium-browser and chromium-browser.desktop.
ln -s chromium-browser %{buildroot}%{_bindir}/chromium
install -D -m 0644 fedora/compat/chromium.desktop %{buildroot}%{_datadir}/applications/chromium.desktop

# Support binaries needed before the full omarchy package is installed.
for helper in omarchy-upload-log omarchy-debug omarchy-debug-idle; do
  install -m 0755 "bin/$helper" %{buildroot}%{_bindir}/"$helper"
done

# SELinux: /etc/xkb holds Omarchy's XKB rules, which libxkbcommon reads before
# /usr/share/X11/xkb. Label it like those (usr_t); as etc_t, systemd-localed
# may not map it and `localectl set-x11-keymap` cannot check a layout.
install -d %{buildroot}%{_datadir}/selinux/packages/omarchy-settings
cat >%{buildroot}%{_datadir}/selinux/packages/omarchy-settings/omarchy_xkb.cil <<'CIL'
(filecon "/etc/xkb(/.*)?" any (system_u object_r usr_t ((s0) (s0))))
CIL

# File list: /etc files are configuration (sudoers.d at 0440), /etc/skel is
# seed content, and these directory trees are wholly ours. Paths are quoted:
# some launchers have spaces in their names.
cd %{buildroot}
{
  for dir in %{_datadir}/omarchy %{_datadir}/sddm/themes/omarchy %{_datadir}/plymouth/themes/omarchy \
             %{_datadir}/fonts/omarchy %{_libexecdir}/omadora; do
    echo "\"$dir\""
  done
  find ./%{_sysconfdir}/skel -mindepth 1 -type d -printf '%%P\n' | sort | while read -r path; do
    echo "%%dir \"%{_sysconfdir}/skel/$path\""
  done
  find ./%{_sysconfdir} \( -type f -o -type l \) -printf '%%P\n' | sort | while read -r path; do
    case $path in
      skel/* | fonts/conf.d/*) echo "\"%{_sysconfdir}/$path\"" ;;
      sudoers.d/*) echo "%%attr(0440,root,root) %%config(noreplace) \"%{_sysconfdir}/$path\"" ;;
      *) echo "%%config(noreplace) \"%{_sysconfdir}/$path\"" ;;
    esac
  done
  find ./usr \( -type f -o -type l \) -printf '/usr/%%P\n' | sort | grep -v \
    -e '^%{_datadir}/omarchy/' -e '^%{_datadir}/sddm/themes/omarchy/' -e '^%{_datadir}/plymouth/themes/omarchy/' \
    -e '^%{_datadir}/fonts/omarchy/' -e '^%{_libexecdir}/omadora/' | sed 's/.*/"&"/'
} >%{_builddir}/omarchy-settings.files
cd -

%pre
# Upgrade: revoke temporary sudo grants before settings change (ALPM
# 05-omarchy-passwordless-revoke.hook, AbortOnFail).
if [ "$1" -ge 2 ]; then
  if [ -x %{_libexecdir}/omadora/omarchy-settings-transition ]; then
    %{_libexecdir}/omadora/omarchy-settings-transition begin || exit 1
  elif [ -x %{_bindir}/omarchy-sudo-passwordless ]; then
    %{_bindir}/omarchy-sudo-passwordless __package-removing || exit 1
  fi
fi
# Pause Hyprland's config auto-reload while files are replaced
# (10-omarchy-hyprland-reload-pause.hook).
if [ -x %{_bindir}/omarchy-hyprland-reload-guard ]; then
  %{_bindir}/omarchy-hyprland-reload-guard pause >/dev/null 2>&1 || :
fi

%preun
if [ "$1" -eq 0 ]; then
  %{_libexecdir}/omadora/omarchy-settings-transition begin || exit 1
fi

%post
# Installing a module rebuilds the whole policy (seconds), so only once.
if command -v selinuxenabled >/dev/null 2>&1 && selinuxenabled; then
  if ! semodule -l 2>/dev/null | grep -qx omarchy_xkb; then
    semodule -i %{_datadir}/selinux/packages/omarchy-settings/omarchy_xkb.cil >/dev/null 2>&1 || :
  fi
  restorecon -R /etc/xkb >/dev/null 2>&1 || :
fi
overrides=%{_datadir}/omarchy/etc-overrides
install -d /etc/security /etc/plymouth /etc/skel
cp -f "$overrides/security-faillock.conf" /etc/security/faillock.conf
cp -f "$overrides/plymouth-plymouthd.conf" /etc/plymouth/plymouthd.conf
if [ -f /etc/cups/cups-browsed.conf ]; then
  cp -f "$overrides/cups-cups-browsed.conf" /etc/cups/cups-browsed.conf
fi
cp -f "$overrides/dot.bashrc" /etc/skel/.bashrc
chmod 0644 /etc/security/faillock.conf /etc/plymouth/plymouthd.conf /etc/skel/.bashrc
# pacman's systemd hooks do these for every package; Fedora's triggers only
# watch /usr/lib, so the /etc drop-ins are applied here.
systemd-sysusers /etc/sysusers.d/omarchy-cups-browsed.conf >/dev/null 2>&1 || :
systemd-tmpfiles --create /etc/tmpfiles.d/omarchy-nopasswd-sudo.conf /etc/tmpfiles.d/omarchy-zswap.conf >/dev/null 2>&1 || :
systemctl daemon-reload >/dev/null 2>&1 || :
udevadm control --reload >/dev/null 2>&1 || :

%posttrans
fc-cache -f %{_datadir}/fonts/omarchy >/dev/null 2>&1 || :
%{_libexecdir}/omadora/omarchy-settings-transition installed || \
  echo "ERROR: Temporary Omarchy sudo grants remain or their boot cleanup is missing; passwordless sudo stays disabled until this package installs cleanly." >&2
# Installs from before plymouth-plugin-label was required have an initramfs
# without it, which crashes the boot splash: rebuild once. The installer builds
# a fresh install's initramfs after the packages, and its running kernel has
# no initramfs in /boot, so this skips there.
initramfs=/boot/initramfs-$(uname -r).img
if [ -f "$initramfs" ] && [ -f %{_libdir}/plymouth/label-freetype.so ] &&
   ! lsinitrd "$initramfs" 2>/dev/null | grep -q 'plymouth/label-freetype\.so'; then
  echo "Rebuilding the initramfs to add Plymouth's text renderer"
  dracut --force --regenerate-all >/dev/null 2>&1 || echo "WARNING: dracut failed; run: sudo dracut --force --regenerate-all" >&2
fi
# 90-omarchy-hyprland-reload-resume.hook
if [ -x %{_bindir}/omarchy-hyprland-reload-guard ]; then
  %{_bindir}/omarchy-hyprland-reload-guard resume >/dev/null 2>&1 || :
fi

%postun
if [ "$1" -eq 0 ]; then
  semodule -r omarchy_xkb >/dev/null 2>&1 || :
  rm -f /etc/sudoers.d/99-omarchy-nopasswd-*
fi

# intune-portal's scriptlets reselect the authselect profile without our
# features, and its upgrades end on plain sssd (omadora-authselect).
%transfiletriggerin -- %{_libdir}/security/pam_intune.so
%{_libexecdir}/omadora/omadora-authselect || :

%transfiletriggerpostun -- %{_libdir}/security/pam_intune.so
%{_libexecdir}/omadora/omadora-authselect || :

%files -f %{_builddir}/omarchy-settings.files
%license LICENSE

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - @VERSION@-@RELEASE@
- Package omarchy-settings for Omadora from the assembled Fedora tree.
