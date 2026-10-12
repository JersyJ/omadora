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
   | Migration missing or changed | `fedora/bin/migrations-status --update`, then review each `unreviewed` row and set `run`, `skip` or `replace:<file>` with a reason |
   | Unmapped package | Add it to `fedora/packages/map.tsv`, following the source order in `DECISIONS.md` |
   | Unclassified top-level path | Mark it `ship` or `repo-only` in `fedora/build/layout.tsv` |

3. Check what the static checks cannot see:
   - `fedora/bin/port-status --list` for new pacman, AUR, Limine, mkinitcpio or ufw references in files we neither override nor patch.
   - omarchy-pkgs: `git log <PKGS_COMMIT>..origin/master -- pkgbuilds/omarchy pkgbuilds/omarchy-settings` in a clone of omacom/omarchy-pkgs. Mirror packaging changes into `fedora/rpm/*.spec` (including Omarchy's apps, which our COPR builds), then bump `PKGS_COMMIT` in `upstream.lock`.
   - Hyprland: if upstream Omarchy moved to a new Hyprland version, move the versionlock and confirm nett00n/hyprland has it.

4. Build and test (from Phase 2 on): RPMs, VM install, update from the previous pinned commit. Roll out to the pilot group before everyone else.

5. Merge the pull request with a merge commit. Never squash or rebase it: the sync merge commit is what keeps upstream history in the fork.

## One upstream fix before its release

Do not cherry-pick: that edits upstream files and breaks the invariant. Export the commit as a patch instead:

```bash
git format-patch -1 --stdout <sha> >fedora/patches/backport-<short-sha>.patch
```

Delete the patch once the synced commit contains it (`git merge-base --is-ancestor <sha> HEAD`).
