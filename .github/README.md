# Omadora: Omarchy for Fedora

Omadora is a Fedora 45 fork of [Omarchy](https://github.com/omacom/omarchy), the Hyprland desktop by DHH. It is for a team whose policy permits only Fedora-based systems. The supported laptop is the HP ZBook 8 G2i 14" (Intel Panther Lake).

## Status

**In use on one ZBook since 2026-10-14.** All hardware checks pass. The laptop has Secure Boot on, an encrypted disk and 0 SELinux denials.

| Phase | State |
| --- | --- |
| 0 to 3: fork, repositories, packages, installer, updates | Done |
| 4: company use | One user, no pilot group. Intune enrollment is next |

## Documents

| Document | Contents |
| --- | --- |
| [`fedora/docs/INSTALL.md`](../fedora/docs/INSTALL.md) | Install a ZBook from one USB stick |
| [`fedora/docs/HARDWARE.md`](../fedora/docs/HARDWARE.md) | The ZBook, test results, known messages |
| [`fedora/docs/INTUNE.md`](../fedora/docs/INTUNE.md) | Company compliance and Intune enrollment |
| [`fedora/docs/DECISIONS.md`](../fedora/docs/DECISIONS.md) | All decisions, with reasons |
| [`fedora/docs/SYNC.md`](../fedora/docs/SYNC.md) | Upstream sync runbook |
| [`fedora/README.md`](../fedora/README.md) | The Fedora layer: tools, tests, layout |
| [`fedora/docs/RESEARCH.md`](../fedora/docs/RESEARCH.md) | The original research (2026-10-12) |

## How the fork works

- **Upstream files do not change.** They stay identical to the upstream commit in [`fedora/upstream.lock`](../fedora/upstream.lock). Thus upstream syncs have no conflicts, and `git log` keeps the full upstream history.
- **All Fedora work is in [`fedora/`](../fedora/README.md):** overrides for Arch-only scripts, small patches, an Arch-to-Fedora package map, migration reviews, RPM specs and the installer.
- **`main` follows upstream's `quattro` branch.** Every 2 weeks, a workflow opens a pull request that syncs to the latest `quattro` commit.
- **Package sources:** Fedora, RPM Fusion, the nett00n/hyprland COPR and Flathub. Our COPR, [`jersyj/omadora`](https://copr.fedorainfracloud.org/coprs/jersyj/omadora/), builds the packages that nobody else builds for Fedora 45, also Omarchy's own apps.

> **NOTE:** GitHub shows this file in place of upstream's `README.md` in the repository root. That file describes Arch-based Omarchy. Do not change it.
