# Research: Omarchy on Fedora

> **NOTE:** This is a snapshot from 2026-10-11 and 2026-10-12. Do not change its findings. For the current state, see `DECISIONS.md` (decisions), `HARDWARE.md` (the installed ZBook) and the team doc (status).

Sources: upstream Omarchy v4.0.4 and the `quattro` branch, omacom/omarchy-pkgs, other Fedora ports, and Fedora 45 package data (Koji, mdapi, COPR API, Bodhi).

## Result

The port is possible, and other ports show that it works. Estimate: 8 to 12 weeks for one engineer to a pilot on 5 to 10 laptops, then 1 to 2 days for each upstream stable release.

## Upstream (Omarchy 4)

| Fact | Number | Effect on the port |
| --- | --- | --- |
| `omarchy-*` commands | 529 on quattro (444 at v4.0.4); 521 are bash | Mostly portable |
| Files that call the `omarchy-pkg-*` helpers | Approximately 148 | One translation layer covers them |
| Non-migration files that use pacman, AUR, Limine, mkinitcpio or ufw | 74 at v4.0.4 (`fedora/bin/port-status`) | The porting backlog |
| Migrations | 106 at v4.0.4, 166 on quattro. On quattro: 107 distro-neutral, 36 only through `omarchy-pkg-*`, 23 Arch-specific | Review each migration. Do not skip them |
| Packages | 204 at v4.0.4 | Mapped in `fedora/packages/map.tsv` |
| Commit rate | Approximately 200 commits every 2 weeks on quattro; 6 to 40 for each stable tag | Pin a commit and sync every 2 weeks |

Omarchy 4 is more difficult to port than 3.x:

- Omarchy is package-based. A second repository (omacom/omarchy-pkgs, 178 PKGBUILDs) builds the `omarchy` and `omarchy-settings` Arch packages. Omarchy has its own pacman repository with approximately 249 packages.
- The desktop is a Quickshell (QML) shell.
- The Hyprland configuration is Lua and needs Hyprland 0.56.
- It boots with Limine and mkinitcpio.
- An ALPM hook stops a plain `pacman -Syu`.

Stable releases come from release branches (`v4-0-1` to `v4-0-4`) made from quattro at v4.0.0. On 2026-10-11, quattro was 836 commits ahead of v4.0.4.

Upstream's position: DHH answered a Fedora request with "No plans for that, but feel free to take what you'd like from here" (omacom/omarchy#353). Upstream closed the Fedora port pull requests. We maintain the port alone.

## Other Fedora ports

| Project | Method | State (2026-10-11) | Lesson |
| --- | --- | --- | --- |
| [whelanh/omarchy-fedora](https://github.com/whelanh/omarchy-fedora) (MIT) | Git subtree of unchanged upstream and a `fedora/` adapter. An install script copies files and writes shims. COPR whelanh/omarchy has Omarchy's apps | Active each day. Runs on F44 and Rawhide | The unchanged-upstream model works. Skips all migrations. Uses plain JetBrains Mono (icons break). No RPMs of Omarchy |
| [kamm3r/omadora](https://github.com/kamm3r/omadora) and [omadora-pkg](https://github.com/kamm3r/omadora-pkg) (MIT) | Separate repository without upstream history. COPR kammer/omadora has approximately 120 RPMs, also `omarchy` and `omarchy-settings` | F44 only. The COPR keeps only the latest build | Good spec files. Not a fork |
| [elpritchos/omadora](https://github.com/elpritchos/omadora) | Rewrite with Waybar, wofi and mako | Follows Omarchy 3.8 | Rewrites drift from upstream |
| malik-na/omadora | Fedora Asahi Remix (Apple Silicon) | Merges omarchy-mac | Not our hardware |
| djdanielsson/omarchy-fedora, R-Dson/omazzite, wayblue | bootc and Universal Blue images | Small, or not Omarchy | Immutable images conflict with Omarchy's runtime installs and migrations |

## Fedora 45 package sources (204 v4.0.4 packages)

| Source | Count |
| --- | --- |
| Fedora 45, same name | 100 |
| Fedora 45, different name (`fd-find`, `google-noto-*`, `python3-gobject`, `firewalld` for ufw, others) | 35 |
| nett00n/hyprland COPR (Hyprland stack, Quickshell 0.3.2; Fedora has 0.2.1) | 7 |
| whelanh/omarchy COPR (Omarchy's apps; 10 more come with 4.1). Later moved to our COPR | 10 |
| Other COPRs with F45 builds (lazygit, gpu-screen-recorder, moonlight-qt, lazydocker) | 4 |
| RPM Fusion (NVIDIA, full codecs), the mise vendor repository, `usage` through mise | 7 |
| Flathub (obsidian, localsend, pinta) | 3 |
| Our COPR (omarchy-nvim, starship, tzupdate, JetBrains Mono Nerd, iA Writer fonts), and `omarchy` and `omarchy-settings` | 5 |
| Removed: Arch-only tools, or hardware that the fork does not support | 32 |
| Unknown until the hardware probe (IPU7 camera) | 1 |
| **Total** | **204** |

Added to upstream's list: grub-btrfs (jmarcoshp/grub-btrfs, F45) for snapshot boot entries.

- Fedora removed Hyprland after F42. solopasha/hyprland is abandoned. nett00n/hyprland builds F43 to F45 and Rawhide (last build 2026-10-09).
- Limine has no usable Fedora package. ericzhang456/limine is a 2023 v4 build. boredsquirrel/limine has no successful build.

## Architecture

- **Fork, do not edit upstream files.** All Fedora work is in `fedora/`: pinned overrides, small patches, exclusions, the package map, migration reviews. CI enforces this.
- **Sync without conflicts.** `fedora/bin/sync-upstream` records a real merge but takes upstream paths unchanged. Tested: v4.0.3 to v4.0.4 to the quattro tip, with 0 conflicts and 0 drift. A plain merge from v4.0.4 to quattro conflicts in 20+ files.
- **Assembly at build time.** `fedora/build/assemble` combines upstream and the Fedora layer. The RPMs and the installer use the result.
- **Package translation at run time.** The Fedora `omarchy-pkg-*` helpers read `map.tsv`. Upstream code that calls `omarchy-pkg-add <arch-name>` works unchanged.
- **System.** Fedora 45 Everything, GRUB2, dracut, snapper, grub-btrfs, firewalld, SELinux enforcing, Secure Boot on.

## Risks

| Risk | Mitigation |
| --- | --- |
| Each third-party COPR has one maintainer | `includepkgs=` on each repository, a version lock on the Hyprland stack, MIT specs ready to build in our COPR |
| Hyprland or Qt updates break Quickshell, the titlebars plugin or the Lua configuration | Version lock. Change it only in a tested sync |
| The ZBook has a MIPI camera | Probe first. (Result: USB camera, `HARDWARE.md`) |
| Upstream security defaults do not suit a company laptop | Reviewed in `DECISIONS.md` (keyring, sudoers, log upload, sshd migration) |
| Upstream changes shipped migrations | Reviews use the content hash. A change sends the migration back to review |
| One failing migration stops `omarchy update` | CI runs each shipped migration in a Fedora container (Phase 3) |

## Phases

| Phase | Work | Done when |
| --- | --- | --- |
| 0. Scaffold (1 to 2 weeks) | Fork, sync, assembly, lock files, static CI, package map, migration reviews, docs | The pinned `quattro` commit syncs and assembles the same each time. CI fails on drift and unmapped packages |
| 1. Repositories and our COPR (2 to 3 weeks) | Repository files with `includepkgs`, version locks, our COPR with the missing packages and Omarchy's apps, map of the 104 optional packages | The full base set resolves on F45 with only the allowed repositories |
| 2. RPMs, overrides, patches (3 to 5 weeks) | `omarchy` and `omarchy-settings` specs, approximately 40 overrides and 20 patches, authselect and PAM, firewalld, ZBook probe | A VM, then a ZBook: no failed setup steps, 0 AVC denials, lock and unlock work, upstream shell tests pass except listed tests |
| 3. Updates and migrations (2 weeks) | Update pipeline, snapper and grub-btrfs, migration test | `omarchy update` across one sync works. Rollback tested |
| 4. Pilot (2 weeks) | Installer, docs, Intune enrollment | 5 to 10 ZBooks through 2 upstream syncs (later changed to one user, no pilot group: `DECISIONS.md`) |
