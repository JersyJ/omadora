# Omadora: Omarchy for Fedora

A Fedora 45 fork of [Omarchy](https://github.com/omacom/omarchy), the Hyprland desktop by DHH, for a team whose policy allows only Fedora-based systems. The supported laptop is the HP ZBook 8 G2i 14" (Intel Panther Lake).

**Status: Phase 0 (scaffolding). Not installable yet.** See [`fedora/docs/RESEARCH.md`](../fedora/docs/RESEARCH.md) for the plan and [`fedora/docs/DECISIONS.md`](../fedora/docs/DECISIONS.md) for what has been decided.

## How the fork works

- Upstream's files are never edited. They stay identical to the upstream commit pinned in [`fedora/upstream.lock`](../fedora/upstream.lock), so every upstream sync is free of conflicts and full upstream history stays in `git log`.
- Everything Fedora-specific lives in [`fedora/`](../fedora/README.md): overrides for Arch-only scripts, small patches, an Arch-to-Fedora package map, migration reviews, RPM specs and the installer.
- `main` tracks upstream's `quattro` branch. Every two weeks a workflow opens a pull request that syncs to the newest `quattro` commit.
- Packages come from Fedora, RPM Fusion, the nett00n/hyprland COPR and Flathub; what nobody else builds for Fedora 45, including Omarchy's own apps, is built in our `omadora` COPR.

GitHub shows this file instead of upstream's `README.md` in the repository root, which describes Arch-based Omarchy and stays unchanged.
