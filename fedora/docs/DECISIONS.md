# Decisions

Decided 2026-10-12 unless noted. Reasons are kept short; `RESEARCH.md` has the evidence.

## Decided

| Topic | Decision | Why |
| --- | --- | --- |
| Base | Fedora 45 Everything, minimal install, x86_64 | Company policy requires a Fedora base. F45 (GA 2026-10-20) ships gum 2.0, Font Awesome 7, Lua 5.5 and `libdnf5-plugin-actions`, which closes gaps F44 has. Minimal avoids desktop-spin leftovers (portals, keyring, autostarts) |
| Repository model | Public GitHub fork of omacom/omarchy named `omadora`; upstream files never edited | Upstream syncs without conflicts and keeps full history; Fedora work stays reviewable in one place |
| Upstream line | `main` tracks upstream's `quattro` branch at a pinned commit, synced every two weeks (`fedora-sync` opens the pull request) | Decided 2026-10-12. Stable tags (v4.0.x) live on release branches that diverge from `quattro`, and the next minor release is cut from `quattro`; porting against a tag would mean redoing the work for 4.1. The pin keeps every build reproducible, and a pilot group takes each sync first |
| Package sources, in order | Fedora official, then a maintained third-party repo with an F45 build, then our own COPR | Prefer what others maintain. Exception (2026-10-12): packages from the other Omarchy-on-Fedora ports (kammer/omadora, whelanh/omarchy) are built in our COPR instead, so the company does not depend on another port's single maintainer |
| Hyprland stack | nett00n/hyprland COPR (hyprland, uwsm, quickshell, portals, hypr* tools), versionlocked to the Hyprland version upstream Omarchy pins | Most complete and most current Fedora Hyprland COPR; rebuilds Quickshell against Fedora's Qt. Fedora retired Hyprland after F42 |
| Omarchy's own apps | Our COPR, starting from whelanh's MIT specs | Decided 2026-10-12. About 20 apps (aether, hype, monologue, omasnap, …); each upstream app release means a spec bump |
| Our COPR `omadora` (public, signed by COPR) | `omarchy`, `omarchy-settings`, Omarchy's apps (above), `omarchy-hyprland-titlebars`, `omarchy-nvim`, `ttf-jetbrains-mono-nerd-basic`, `ttf-ia-writer`, `tzupdate`, `starship` (`source` = `ours` in `packages/map.tsv`) | Specs start from kamm3r/omadora-pkg and whelanh/omarchy-fedora (both MIT; keep their notices). atim/starship has no F45 build. The titlebars plugin must match nett00n's Hyprland build exactly |
| Third-party repo hardening | `includepkgs=` on every third-party repo; versionlock on the Hyprland stack; pilot group first | A COPR must never be able to replace sudo, glibc or the kernel |
| Bootloader | GRUB2 (Fedora default) + snapper + grub-btrfs; no Limine | Limine is not packaged for Fedora, needs Secure Boot off or per-machine keys (Omarchy's manual says to disable Secure Boot), and its Omarchy glue is mkinitcpio-only. GRUB keeps Secure Boot, TPM2 unlock and fwupd working |
| Initramfs | dracut | Fedora default; Omarchy's mkinitcpio drop-ins become dracut config |
| Firewall | firewalld | Fedora's maintained default; ufw on Fedora is 0.35 and `ufw-docker` has no package anywhere. Costs one override (`install/config/firewall.sh`) and four small patches |
| Migrations | Upstream migrations run, each reviewed (`migrations/classify.tsv`) | whelanh's port skips all of them, so existing installs never get upstream's config changes |
| System files | Keep Fedora's `os-release`, `nsswitch.conf` and `cups-files.conf` | Upstream's versions set `ID_LIKE=arch` (breaks dnf copr, toolbox and management agents), fight authselect, and hardcode Arch's cups user 209 |
| SELinux | Enforcing; releases gated on zero AVC denials | Company laptops; RPM installs label files correctly |
| Hardware | HP ZBook 8 G2i 14" only | See `HARDWARE.md` |
| Hardware probe | Postponed to Phase 2 (decided 2026-10-12) | Phases 1 and most of 2 do not depend on it; it is needed before the first install on a real ZBook, and it decides only the camera package and which `install/hardware` scripts ship |
| Keyring | GNOME Keyring with an encrypted `login` keyring, unlocked by the SDDM password through `pam_gnome_keyring`; no passwordless `Default_keyring` and no autologin | Decided 2026-10-12. Microsoft Intune's identity broker stores its tokens in GNOME Keyring through libsecret. Overrides: `install/user/default-keyring.sh` (creates nothing), `install/login/sddm.sh` (keeps the PAM lines upstream deletes). To verify in Phase 2: the keyring password follows `passwd` changes (Fedora's sddm PAM has no `password` line for it) |
| Passwordless sudo rules | Keep upstream's NOPASSWD rules | Decided 2026-10-12 |
| Log upload | Never upload to logs.omarchy.org; save the log in the home directory instead | Decided 2026-10-12: upstream's support service is for Arch-based Omarchy, not forks. Overrides: `bin/omarchy-upload-log`, `bin/omarchy-debug` |
| mise | Keep `install/user/mise.sh` (about 20 CLIs from the internet) | Decided 2026-10-12 |
| sshd migration `1788124236` | Run it (disables SSH password logins, or sshd when no key is authorized) | Decided 2026-10-12 |

## Open

| Topic | Options | Notes |
| --- | --- | --- |
| Intune client | Ship `intune-portal` and Microsoft Edge from Microsoft's RHEL repo in the base install, or leave enrollment to IT | Microsoft supports Intune on Ubuntu and RHEL, not Fedora; needs a test enrollment on F45. The keyring decision above is the prerequisite |
| Flatpak or RPM for obsidian, localsend, pinta | Flathub (current map) or RPMs in our COPR (kamm3r specs) | Flatpaks need small wrappers where Omarchy launches the apps by command name |
| Codecs | RPM Fusion `ffmpeg` and `intel-media-driver` (current map) or Fedora's free builds | Full H.264/HEVC encode needs RPM Fusion; screen recording uses it |
| Camera | Depends on the hardware probe (Phase 2) | MIPI/IPU7 cameras need an akmod plus closed-source userspace (the hardest item in the port); USB cameras need nothing |
| Optional installers | 104 package names used by Omarchy's optional install menu are not mapped yet | Phase 1 |
