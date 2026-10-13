# Syncing upstream

`main` tracks upstream's `quattro` branch, pinned to one commit in `fedora/upstream.lock`. `quattro` moves about 200 commits every two weeks. Every second Monday the `fedora-sync` workflow syncs to the current `quattro` tip and opens a pull request `Sync upstream quattro (<sha>)`; it can also be started by hand from the Actions tab. You can sync by hand too.

Do not use GitHub's "Sync fork" button: it merges without updating `upstream.lock` or running the checks.

## Why syncing never conflicts

`fedora/bin/sync-upstream <ref>` records a real merge of `<ref>` (so `git log` shows every upstream commit) but builds the result tree mechanically: upstream-owned paths are taken verbatim from `<ref>`, fork-owned paths (`fedora/`, `.copr/`, `.github/workflows/`, `.github/README.md`) verbatim from the current branch. Nothing is ever merged hunk by hunk, so there is nothing to conflict, even when switching between upstream lines (the v4.0.x release branches diverge from `quattro`; a plain `git merge` between them conflicts in 20+ files), so moving `main` to a stable tag later stays possible.

The cost moves from merge conflicts to review: changes upstream made to files we override or patch must be ported by hand. The checks below find all of them.

## Runbook for one sync

1. Sync. Either merge the bot's pull request branch locally, or run:

   ```bash
   git switch -c sync/$(date +%F) main
   fedora/bin/sync-upstream upstream/quattro
   fedora/tests/static.sh
   ```

2. Work through what the static checks report:

   | Failure | What to do |
   | --- | --- |
   | Override drifted | `git diff <pinned blob> <new blob>` (both printed), port the relevant change into `fedora/overrides/<path>`, then `fedora/bin/pin-override <path>` |
   | Patch no longer applies | Re-create it against the new upstream file (`fedora/build/assemble` output is a convenient base) |
   | Migration missing, changed or unreviewed | `fedora/bin/migrations-status --update`, then review each `unreviewed` row and set `run`, `skip` or `replace:<file>` with a reason. Until then the build leaves the migration out, so it cannot run unreviewed. A replacement lives in `fedora/migrations/` and ships under the upstream name. Also check what a fresh install does: it marks every shipped migration done without running it, so a migration that removes or disables something only Arch's install leaves out (a package Fedora pulls in as a weak dependency, say) needs the same change in the kickstart. `cups-browsed` was one (2026-10-13) |
   | Unmapped package | Add it to `fedora/packages/map.tsv`, following the source order in `DECISIONS.md` |
   | Unclassified top-level path | Mark it `ship` or `repo-only` in `fedora/build/layout.tsv` |

3. Check what the static checks cannot see:
   - `fedora/bin/port-status --list` for new pacman, AUR, Limine, mkinitcpio or ufw references in files we neither override nor patch.
   - omarchy-pkgs: `git log <PKGS_COMMIT>..origin/master -- pkgbuilds/omarchy pkgbuilds/omarchy-settings` in a clone of omacom/omarchy-pkgs. Mirror packaging changes into `fedora/rpm/*.spec` (including Omarchy's apps, which our COPR builds), then bump `PKGS_COMMIT` in `upstream.lock`.
   - Hyprland and Quickshell: if upstream Omarchy moved to a new version (`omarchy-hyprland-titlebars` in omarchy-pkgs pins Hyprland exactly), confirm nett00n/hyprland has it, move the lock in `fedora/repos/versionlock.toml`, and rebuild `omarchy-hyprland-titlebars`.
   - Our COPR: for every recipe whose upstream PKGBUILD changed (`git log <PKGS_COMMIT>..origin/master -- pkgbuilds/<name>`), port the change into `fedora/rpm/<name>/`, update `sources.sha256`, push, then `copr-cli build-package jersyj/omadora --name <name>`. Recipes with `%global pkgs_commit` must move with `PKGS_COMMIT`; the static checks enforce it.

4. Build and test, all in VMs, never on a workstation:
   - Rebuild the COPR packages, then a fresh laptop-style install: `OMADORA_VM_PACKAGED=1 OMADORA_VM_SECURE_BOOT=1 OMADORA_VM_SB_VARS=<vars> OMADORA_VM_PASSWORD_LOGIN=1 fedora/tests/vm-install.sh <netinst.iso> <dir>`. It also checks the keyring, `passwd` and the lock screen (`tests/vm-password-login.sh`).
   - Upstream's graphical suite on that VM: `OMADORA_VM_PASSWORD=Kestrel-Window-2026 fedora/tests/vm-acceptance.sh <dir>` (the login test changed the password). Triage any new failure into a fix or a reasoned line in `tests/acceptance-expected-failures.txt`.
   - `omarchy update` on a VM installed from the previous sync, then `omarchy-snapshot restore` once.
   - Roll out to the pilot group before everyone else.

5. Merge the pull request with a merge commit. Never squash or rebase it: the sync merge commit is what keeps upstream history in the fork.

## One upstream fix before its release

Do not cherry-pick: that edits upstream files and breaks the invariant. Export the commit as a patch instead:

```bash
git format-patch -1 --stdout <sha> >fedora/patches/backport-<short-sha>.patch
```

Delete the patch once the synced commit contains it (`git merge-base --is-ancestor <sha> HEAD`).

## Between syncs

- **nett00n rebuilds Hyprland.** `omarchy-hyprland-titlebars` requires the exact Hyprland build it was compiled against, so dnf holds Hyprland back until the plugin is rebuilt: `copr-cli build-package jersyj/omadora --name omarchy-hyprland-titlebars`. Nothing breaks in the meantime; laptops just keep the previous build.
- **nett00n's packages miss dependencies.** Our `omarchy` spec requires `xorg-x11-server-Xwayland` and `python3-pyxdg` because nett00n's `hyprland` and `uwsm` don't (`DECISIONS.md`). Check now and then with `dnf repoquery --requires hyprland uwsm`; once they list them, remove the two lines from `fedora/rpm/omarchy/omarchy.spec`.
- **An app's upstream releases a fix.** Bump its recipe in `fedora/rpm/` and rebuild that one COPR package; the omarchy-pkgs pin moves with the next sync.

