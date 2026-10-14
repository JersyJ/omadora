# Decisions

Each row gives the decision date. `RESEARCH.md` has the evidence for the 2026-10-12 decisions.

## Platform

| Topic | Decision | Reason |
| --- | --- | --- |
| Base | Fedora 45 Everything, minimal install, x86_64 (2026-10-12) | Company policy requires Fedora. Fedora 45 (release 2026-10-20) has gum 2.0, Font Awesome 7, Lua 5.5 and `libdnf5-plugin-actions`. A minimal install has no desktop leftovers |
| Hardware | HP ZBook 8 G2i 14" only (2026-10-12) | `HARDWARE.md` |
| NVIDIA | Not supported. All NVIDIA packages are removed. RPM Fusion supplies only codecs and Steam (2026-10-12) | The company buys the ZBook without the RTX PRO 500. No akmod, MOK or Secure Boot signing work |
| Boot loader | GRUB2, snapper and grub-btrfs. No Limine (2026-10-12) | Fedora has no Limine package. Limine needs Secure Boot off or keys per machine. GRUB keeps Secure Boot, TPM2 unlock and fwupd |
| Initramfs | dracut (2026-10-12) | Fedora default. Omarchy's mkinitcpio drop-ins become dracut configuration |
| Firewall | firewalld (2026-10-12) | Fedora's default. Fedora's ufw is 0.35, and `ufw-docker` has no package. Cost: 1 override (`install/config/firewall.sh`) and 4 patches |
| System files | Keep Fedora's `os-release`, `nsswitch.conf` and `cups-files.conf` (2026-10-12) | Upstream's files set `ID_LIKE=arch` (breaks dnf copr, toolbox and management agents), conflict with authselect, and use Arch's cups user 209 |

## Repository and upstream

| Topic | Decision | Reason |
| --- | --- | --- |
| Repository | Public GitHub fork of omacom/omarchy, named `omadora`. Upstream files are not edited (2026-10-12) | Syncs have no conflicts and keep the history. All Fedora work is in one place |
| Upstream line | `main` follows upstream's `quattro` branch at a pinned commit. Sync every 2 weeks; `fedora-sync` opens the pull request (2026-10-12) | Stable tags are on release branches that diverge from `quattro`, and 4.1 comes from `quattro`. The pin makes builds reproducible |
| Upstream bugs | Wait for upstream to correct a bug, and take the fix with a sync. Exceptions need approval and a pinned override (2026-10-13) | Fewer differences from upstream. Approved exception: the sleep hook's resume step (2026-10-14, "Desktop" below) |
| Migrations | Upstream migrations run after review (`migrations/classify.tsv`). Unreviewed and skipped migrations are not built. The 164 migrations up to upstream `defbf90e` are `baseline` (2026-10-12) | whelanh's port skips all migrations, so existing installs never get upstream's configuration changes. A fresh install marks each shipped migration done. The package-removing migrations were checked on a fresh install (2026-10-13) |

## Package sources

| Topic | Decision | Reason |
| --- | --- | --- |
| Order | 1. Fedora. 2. A maintained third-party repository with a Fedora 45 build. 3. Our COPR (2026-10-12) | Use what other people maintain. Exception: packages from the other Omarchy-on-Fedora ports (kammer, whelanh) are built in our COPR, so the company does not depend on their single maintainers |
| Our COPR | [`jersyj/omadora`](https://copr.fedorainfracloud.org/coprs/jersyj/omadora/), public, signed by COPR, fedora-45-x86_64 (2026-10-12) | Builds `omarchy`, `omarchy-settings`, `omadora-repos`, Omarchy's apps, `omarchy-hyprland-titlebars`, `omarchy-nvim`, fonts, `tzupdate`, `starship`, `uwsm`, `lazydocker` (`ours` in `packages/map.tsv`). Specs start from kamm3r and whelanh (MIT; keep their notices) |
| Fedora package splits | If an Arch package contains files that Fedora puts in other packages, require those packages (2026-10-14) | Arch's `plymouth`, `linux-firmware`, `networkmanager` and `sushi` include parts that Fedora ships separately. The first ZBook found each one (`HARDWARE.md`) |
| Hyprland stack | nett00n/hyprland COPR (hyprland, quickshell, portals, hypr tools), with a version lock on the Hyprland version that upstream pins (2026-10-12) | The most complete and current Fedora Hyprland COPR. Fedora removed Hyprland after Fedora 42 |
| Gaps in nett00n's packages | `omarchy` requires `xorg-x11-server-Xwayland`. `uwsm` comes from our COPR (2026-10-12) | Without Xwayland, X11 apps such as Intune Portal crash. Remove each requirement when nett00n's packages have it (`SYNC.md`) |
| uwsm | Our COPR (`rpm/uwsm`), built with Arch's options (2026-10-13) | nett00n's build has no `uwsm-app`, so no app started. Its build also does not require `python3-pyxdg` and `python3-dbus`. `omarchy` requires `/usr/bin/uwsm-app` |
| Omarchy's apps | Our COPR, specs from whelanh (MIT) (2026-10-12) | Approximately 20 apps. Each app release needs a spec change |
| Packages from this tree | `omarchy` and `omarchy-settings` follow upstream's `omarchy-dev` and `omarchy-settings-dev` recipes. `omadora-repos` installs the repositories, limits and version locks. ALPM hooks become RPM scriptlets (2026-10-12) | The version is upstream's (`4.0.0.r6912.gdefbf90`). The release counts fork commits |
| Theme wallpapers | Stay in `omarchy`, as upstream ships them (2026-10-14) | Each new build downloads 162 MB. That is acceptable with a sync every 2 weeks |
| Package helpers | `omarchy-pkg-*` translate Arch names through `packages/map.tsv` (`lib/runtime/pkg.sh`). The menu guards use the same layer (2026-10-12) | If the map has no row for a name, the name is used as a Fedora name |

## Security

| Topic | Decision | Reason |
| --- | --- | --- |
| SELinux | Enforcing. A release must have 0 AVC denials (2026-10-12) | Company laptops |
| Local SELinux modules | `omarchy-settings` installs small CIL modules. Allow access that is harmless and expected; hide (`dontaudit`) access that a program does not need (2026-10-14) | `omarchy_xkb`: labels `/etc/xkb` as `usr_t` for `systemd-localed`. `omadora_denials`: lets `systemd-sleep` read fs sysctls and hides user lookups of `power-profiles-daemon` |
| Third-party repositories | `includepkgs=` on each third-party repository, RPM Fusion also (dnf5 `repos.override.d`). Version lock on Hyprland and Quickshell (2026-10-12) | A COPR must not replace sudo, glibc or the kernel. CI checks each limit (`repos/README.md`) |
| Keyring | GNOME Keyring with an encrypted `login` keyring. The SDDM password unlocks it through `pam_gnome_keyring`. No passwordless keyring, no autologin (2026-10-12) | Intune's identity broker keeps its tokens there. Overrides: `install/user/default-keyring.sh`, `install/login/sddm.sh`. Tested 2026-10-13: first login, `passwd` and reboot (`tests/vm-password-login.sh`) |
| Passwordless sudo | Keep Omarchy's NOPASSWD rules (2026-10-12) | The company guide discourages them for daily use. Accepted |
| sshd migration `1788124236` | Run it: SSH password login off, or sshd off when no key is authorized (2026-10-12) | |
| Log upload | Do not upload to logs.omarchy.org. Save the log in the home directory (2026-10-12) | Upstream's service supports Arch Omarchy, not forks. Overrides: `bin/omarchy-upload-log`, `bin/omarchy-debug` |
| Printer discovery | No `cups-browsed`. The kickstart removes it, and `exclude_from_weak_autodetect` stops CUPS from adding it again (2026-10-13) | Upstream removed it after the 2024 vulnerabilities (migration 1788009111). CUPS still finds driverless printers |

## Install

| Topic | Decision | Reason |
| --- | --- | --- |
| Installer | Fedora Everything netinst with a generated kickstart (`bin/kickstart`): btrfs on LUKS2, Omarchy's system setup, then its user setup. The kickstart records the user as SDDM's last user (2026-10-12) | Omarchy's SDDM theme has only a password field. Tested in a VM with an encrypted disk, Secure Boot and a typed password (2026-10-13) |
| USB stick | One stick: `bin/usb-image` adds the kickstart to the ISO's EFI partition as an extra initrd. A second stick with the label `OEMDRV` also works (2026-10-14) | The first ZBook was installed with it, with Secure Boot on (`INSTALL.md`) |
| RPM Fusion updates during install | Not in the kickstart until RPM Fusion opens them for Fedora 45 | Before the release they do not exist, and the installer stops on them. The installed system keeps them |

## Updates

| Topic | Decision | Reason |
| --- | --- | --- |
| Update pipeline | `omarchy update` keeps upstream's steps. The package steps use dnf: `dnf upgrade --refresh` in its own scope, `dnf autoremove`, Flatpak updates in place of AUR updates (2026-10-13) | Overrides: `overrides/bin/omarchy-update-*`, `omarchy-version*`, `omarchy-reinstall-pkgs`. Patches 0007 (reboot prompt after a kernel update) and 0008 (migrations wait for dnf) |
| Automatic updates | Security updates each day (`dnf5-automatic.timer`), no automatic reboot. All other updates through `omarchy update` (2026-10-13) | Company compliance (`INTUNE.md`) |
| Snapshots | snapper pre and post snapshots around each dnf transaction (libdnf5 actions plugin), and upstream's snapshot before `omarchy update`. Keep 10 snapshots (2026-10-13) | Covers automatic updates and `omarchy-pkg-add` too |
| Snapshot boot and restore | grub-btrfs (COPR `jmarcoshp/grub-btrfs`) adds a GRUB snapshot menu. Snapshots boot read-only with an overlay. `omarchy-snapshot restore` makes a snapshot the `root` subvolume and keeps the old root as `root.old-<time>` (2026-10-13) | Snapper's rollback needs a subvolume layout that Fedora does not use. Tested in the VM |
| Update guard and channels | Not ported (2026-10-13) | On Fedora, automatic updates and IT tools run dnf directly. Omadora has 1 channel (our COPR from `main`) |
| Staged rollout | None. Each build goes to each laptop (2026-10-13) | One user for now. A testing COPR comes with a pilot group |
| COPR builds | CI builds what a push to `main` changed, after all checks pass. The VM tests stay local (2026-10-13) | `SYNC.md` |

## Desktop and apps

| Topic | Decision | Reason |
| --- | --- | --- |
| Chromium names | `/usr/bin/chromium` links to Fedora's `chromium-browser`. A hidden `chromium.desktop` replaces `chromium-browser.desktop` (2026-10-12) | Omarchy uses the Arch names in 17 commands and in its MIME defaults |
| MIME defaults | Omarchy's list is `/usr/share/applications/hyprland-mimeapps.list` (2026-10-12) | Fedora's `shared-mime-info` owns `mimeapps.list`. The Hyprland list applies in the Hyprland session only |
| Arch-only menu entries | Hidden: Reset Computer, AUR, update channels (patch 0005) (2026-10-13) | Install > Package covers all repositories |
| Login screen scale | Opt-in: `/etc/omadora/greeter-scale` sets the scale. Automatic scale when the file is absent (2026-10-14) | The login screen runs as the `sddm` user and cannot read the user's monitor settings. The user writes the file one time (`INSTALL.md`) |
| Sleep hook resume step | `omadora-gvfs-resume.service` restores the gvfs FUSE mount after resume. The overridden hook keeps only its pre-sleep step (2026-10-14) | systemd stops the hook's background job, also on Arch. Approved exception to "Upstream bugs" |
| Proprietary apps with a vendor repository | The vendor's repository, added on demand and limited to that app: Chrome, VS Code, 1Password, Brave, Sublime Text, NordVPN, Dropbox, Symfony CLI, Cursor (2026-10-12) | The vendor updates the native package |
| Apps without a vendor repository | A maintained COPR if one exists (Zen Browser: sneexy, Zed: che, Sunshine: LizardByte, xpadneo: neovi). Otherwise Flathub: Spotify, Signal, Slack, Bitwarden, Heroic, Minecraft (2026-10-12) | |
| Obsidian, LocalSend, Pinta | Flathub. An RPM is also acceptable from a maintained source other than our COPR (2026-10-13) | |
| Codecs | RPM Fusion `ffmpeg` and `intel-media-driver` (2026-10-13) | Full H.264 and HEVC. Screen recording uses them |
| Omarchy's optional extras | Install through Omarchy's Install menu, vendor sources first (2026-10-13) | Details below |
| Slack | Not offered on company laptops | The company stopped using Slack |

### Optional extras

| Extra | Source |
| --- | --- |
| ChatGPT | OpenAI's RPM, which adds OpenAI's repository (`url:` in the map) |
| Grok Bot | xAI's repository |
| Ghostty | `mineiro/ghostty` COPR |
| Claude, Voxtype | Our COPR, repacks of the vendor builds. A URL install would pin one version that `omarchy update` never updates |
| umu-launcher, ONCE, Emacs and Zed integrations | Our COPR, built from source. umu's own RPMs need Fedora 44's Python 3.14 |
| Perplexity, T3 Code, LM Studio | Not offered (`todo`). Recipes stay in `rpm/`, not registered in COPR |
| Hermes Desktop | Not offered (`todo`). No Linux build, and its Vite build fails in the Fedora 45 build environment |
| `elsewhen`, `omarchy-herdr` | `drop`: Omarchy no longer installs them |

`tests/vm-extras.sh` installs each extra in a VM and checks that it starts. `bin/recipe-status` reports new upstream versions. A recipe builds again only when its version changes.

## Intune

| Topic | Decision | Reason |
| --- | --- | --- |
| Intune | Phase 4. Requirements in `INTUNE.md` (received 2026-10-12): Edge and Defender in the base install, Intune Portal, a 12-character password policy, automatic security updates, a full update every 2 weeks | Secure Boot, disk encryption, GNOME Keyring and the polkit prompt are in place. Edge, Defender and Intune Portal are in `packages/extra.txt` |
| Intune Portal build | Microsoft's RHEL 10 repository, which uses Fedora's WebKitGTK 6.0 and libsoup 3 (2026-10-13) | Replaces dwrobel's WebKitGTK 4.0 COPR. WebKitGTK 2.52 removed the 4.0 API, so a 4.0 build gets no security fixes |

## Open

Nothing.
