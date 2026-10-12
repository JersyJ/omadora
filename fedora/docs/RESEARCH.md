# Research: Omarchy on Fedora

Research done 2026-10-11 and 2026-10-12 against upstream Omarchy v4.0.4 and the `quattro` branch, omacom/omarchy-pkgs, existing Fedora ports, and Fedora 45 package data (Koji, mdapi, COPR API, Bodhi).

This is a research snapshot. Decisions made after it (tracking `quattro` instead of stable tags, building the other ports' packages in our own COPR, the keyring, the postponed hardware probe) are in `DECISIONS.md`.

## Verdict

Feasible, and already shown to work by others. Medium effort: about 8–12 weeks for one engineer to a pilot on 5–10 laptops, then about 1–2 days per upstream stable release.

## What upstream looks like (Omarchy 4)

| Fact | Number | Why it matters |
| --- | --- | --- |
| `omarchy-*` commands | 529 on quattro (444 at v4.0.4), 521 of them bash | Mostly portable |
| Files calling the `omarchy-pkg-*` helpers | about 148 | One translation layer covers them |
| Non-migration files referencing pacman, AUR, Limine, mkinitcpio or ufw | 74 at v4.0.4 (`fedora/bin/port-status`) | The real porting backlog |
| Migrations | 106 at v4.0.4, 166 on quattro; on quattro 107 distro-neutral, 36 only through `omarchy-pkg-*`, 23 Arch-specific | They must be reviewed, not skipped |
| Package list | 204 packages at v4.0.4 | Mapped in `fedora/packages/map.tsv` |
| Commit rate | about 200 commits every two weeks on quattro; 6–40 per stable tag | Pin a commit and sync every two weeks |

Omarchy 4 is harder to port than 3.x:
- It is package-based. The `omarchy` and `omarchy-settings` Arch packages are built from a second repository (omacom/omarchy-pkgs, 178 PKGBUILDs), and Omarchy runs its own pacman repository of about 249 packages.
- The desktop is a Quickshell (QML) shell.
- The Hyprland config is Lua and needs Hyprland 0.56.
- It boots with Limine plus mkinitcpio.
- An ALPM hook blocks plain `pacman -Syu`.

Stable releases come from linear release branches (`v4-0-1` … `v4-0-4`) cut from quattro at v4.0.0; quattro was 836 commits ahead of v4.0.4 on 2026-10-11.

Upstream's stance: DHH answered a Fedora request with "No plans for that, but feel free to take what you'd like from here" (omacom/omarchy#353). Fedora port PRs were closed. Expect to maintain the port alone.

## Existing ports

| Project | Approach | State (2026-10-11) | Lesson |
| --- | --- | --- | --- |
| [whelanh/omarchy-fedora](https://github.com/whelanh/omarchy-fedora) (MIT) | Squashed git subtree of unmodified upstream + `fedora/` adapter; install script copies files and writes shims; COPR whelanh/omarchy with Omarchy's apps | Active daily; runs on F44 and Rawhide; "in development" | Proves the unmodified-upstream model. Skips every upstream migration; maps JetBrains Mono Nerd to plain JetBrains Mono (breaks icons); no RPMs of Omarchy itself |
| [kamm3r/omadora](https://github.com/kamm3r/omadora) + [omadora-pkg](https://github.com/kamm3r/omadora-pkg) (MIT) | Separate repo without upstream history; COPR kammer/omadora with about 120 RPMs including `omarchy` and `omarchy-settings` | F44 only; COPR keeps only the latest build | Useful spec files; not a fork model |
| [elpritchos/omadora](https://github.com/elpritchos/omadora) | Rewrite with Waybar, wofi and mako | Tracks Omarchy 3.8 | Rewrites drift from upstream |
| malik-na/omadora | Fedora Asahi Remix (Apple Silicon) | Merges omarchy-mac | Not our hardware |
| djdanielsson/omarchy-fedora, R-Dson/omazzite, wayblue | bootc / Universal Blue images | Small or not Omarchy | Immutable images fight Omarchy's runtime installs and migrations |

## Fedora 45 availability (all 204 v4.0.4 packages)

| Outcome | Count |
| --- | --- |
| Fedora 45 official, same name | 100 |
| Fedora 45 official, different name (`fd-find`, `google-noto-*`, `python3-gobject`, `firewalld` for ufw, …) | 35 |
| nett00n/hyprland COPR (Hyprland stack incl. Quickshell 0.3.2; Fedora's own Quickshell is 0.2.1) | 7 |
| whelanh/omarchy COPR (Omarchy's apps; 10 more arrive with 4.1). Since moved to our COPR | 10 |
| Other COPRs with F45 builds (lazygit, gpu-screen-recorder, moonlight-qt, lazydocker) | 4 |
| RPM Fusion (NVIDIA, full codecs), the mise vendor repo, and `usage` through mise | 7 |
| Flathub (obsidian, localsend, pinta) | 3 |
| Our COPR (omarchy-nvim, starship, tzupdate, JetBrains Mono Nerd, iA Writer fonts), plus `omarchy` and `omarchy-settings` themselves | 5 |
| Dropped: Arch-only tooling, or hardware this fork does not support | 32 |
| Unknown until the hardware probe (IPU7 camera) | 1 |
| **Total** | **204** |

grub-btrfs (jmarcoshp/grub-btrfs, F45) is added on top of upstream's list for snapshot boot entries.

Fedora retired Hyprland after F42; solopasha/hyprland is abandoned. nett00n/hyprland builds F43–F45 and Rawhide and was rebuilt 2026-10-09. Limine has no usable Fedora package (ericzhang456/limine is a 2023 v4 build; boredsquirrel/limine has no successful build).

## Architecture

- **Fork, never edit upstream files.** All Fedora work is in `fedora/` (overrides pinned to the upstream version they were reviewed against, small patches, exclusions, package map, migration reviews). CI enforces it.
- **Conflict-free sync.** `fedora/bin/sync-upstream` records a real merge but takes upstream paths verbatim. Tested: v4.0.3 → v4.0.4 → quattro tip with zero conflicts and zero drift; a plain merge from v4.0.4 to quattro conflicts in 20+ files.
- **Build-time assembly.** `fedora/build/assemble` turns pristine upstream plus the Fedora layer into the tree that RPMs (`omarchy`, `omarchy-settings`, mirroring upstream's PKGBUILDs) and the installer use.
- **Runtime package translation.** Fedora versions of the `omarchy-pkg-*` helpers read `map.tsv`, so upstream code and migrations calling `omarchy-pkg-add <arch-name>` work unchanged.
- **System.** Fedora 45 Everything, GRUB2 + dracut + snapper + grub-btrfs, firewalld, SELinux enforcing, Secure Boot on.

## Risks

| Risk | Mitigation |
| --- | --- |
| Third-party COPRs are single-maintainer | `includepkgs=` per repo, versionlock on the Hyprland stack, pilot group, specs (MIT) ready to rebuild in our COPR |
| Hyprland or Qt updates break Quickshell, the titlebars plugin or the Lua config | Versionlock; bump only during a sync after testing |
| MIPI camera on the ZBook | Probe first; if MIPI, budget extra time for the IPU7 akmod |
| Upstream security defaults that do not fit a company laptop | Reviewed in `DECISIONS.md` (keyring, sudoers, log upload, sshd migration) |
| Upstream edits shipped migrations | Migration reviews are keyed by content hash; any change returns a migration to review |
| A single failing migration stops `omarchy update` | Every shipped migration runs in a Fedora container in CI (Phase 3) |

## Phases

| Phase | Work | Done when |
| --- | --- | --- |
| 0. Scaffold (1–2 weeks) | Fork, sync, assemble, lock files, static CI, package map, migration review table, docs | The pinned `quattro` commit syncs and assembles reproducibly; CI fails on drift and unmapped packages |
| 1. Repositories and our COPR (2–3 weeks) | Repo files with `includepkgs`, versionlocks, our COPR with the gap packages and Omarchy's apps, map the 104 optional-install packages | The whole base set resolves on F45 with only the allowed repositories |
| 2. RPMs, overrides, patches (3–5 weeks) | `omarchy`/`omarchy-settings` specs, about 40 overrides and 20 patches, authselect and PAM, firewalld, hardware probe of a real ZBook | Kickstarted VM, then a real ZBook: no failed setup steps, zero AVC denials, lock and unlock work, upstream shell tests pass apart from listed exceptions |
| 3. Updates and migrations (2 weeks) | Update pipeline, snapper and grub-btrfs, migration harness | `omarchy update` across one two-week sync works; rollback tested |
| 4. Pilot (2 weeks) | Kickstart (optionally an ISO), docs, Intune enrollment to IT's requirements | 5–10 ZBooks through two upstream syncs |
