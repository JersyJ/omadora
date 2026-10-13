# Syncing upstream

`main` tracks upstream's `quattro` branch, pinned to one commit in `fedora/upstream.lock`. `quattro` moves about 200 commits every two weeks. Every second Monday the `fedora-sync` workflow syncs to the current `quattro` tip and opens a pull request `Sync upstream quattro (<sha>)`; it can also be started by hand from the Actions tab. You can sync by hand too.

Do not use GitHub's "Sync fork" button: it merges without updating `upstream.lock` or running the checks.

## Why syncing never conflicts

`fedora/bin/sync-upstream <ref>` records a real merge of `<ref>` (so `git log` shows every upstream commit) but builds the result tree mechanically: upstream-owned paths are taken verbatim from `<ref>`, fork-owned paths (`fedora/`, `.copr/`, `.github/workflows/`, `.github/README.md`) verbatim from the current branch. Nothing is ever merged hunk by hunk, so there is nothing to conflict, even when switching between upstream lines (the v4.0.x release branches diverge from `quattro`; a plain `git merge` between them conflicts in 20+ files), so moving `main` to a stable tag later stays possible.

The cost moves from merge conflicts to review: changes upstream made to files we override or patch must be ported by hand. The checks below find all of them.

## Runbook for one sync

A sync of about 60 upstream commits took an afternoon the first time (2026-10-13), most of it VM time. Do every step on a branch; `main` only changes by merging the pull request.

### 1. Sync on a branch

Take the `fedora-sync` bot's pull request branch, or start one by hand:

```bash
git switch -c sync/$(date +%F) main
fedora/bin/sync-upstream upstream/quattro     # a merge commit; never conflicts
fedora/tests/static.sh
```

### 2. Fix what the static checks report

| Failure | What to do |
| --- | --- |
| Override drifted | `git diff <pinned blob> <new blob>` (both printed). Port what applies into `fedora/overrides/<path>` (often nothing: a pacman-only change), reread the override's own comments, then `fedora/bin/pin-override <path>` |
| Patch no longer applies | Re-create it: copy the new upstream file into `a/<path>` and `b/<path>` in a scratch directory, make the Fedora change again in `b/` by hand, then `diff -u a/<path> b/<path>` below the patch's existing header lines. Keep the change the same size; the patch's comment says why it exists |
| Migration missing, changed or unreviewed | `fedora/bin/migrations-status --update`, then set each `unreviewed` row to `run`, `skip` or `replace:<file>` with a reason. Until then the build leaves the migration out, so it cannot run unreviewed. A replacement lives in `fedora/migrations/` and ships under the upstream name. Also check what a fresh install does: it marks every shipped migration done without running it, so a migration that removes or disables something only Arch's install leaves out (a package Fedora pulls in as a weak dependency, say) needs the same change in the kickstart. `cups-browsed` was one (2026-10-13) |
| A removed upstream command is still called | Upstream renamed or removed a command the Fedora layer uses (`omarchy-system-reboot` became `omarchy-system reboot` in the first sync). `git log -- bin/<name>` shows the replacement |
| Unmapped package | Add it to `fedora/packages/map.tsv`, following the source order in `DECISIONS.md` |
| Unclassified top-level path | Mark it `ship` or `repo-only` in `fedora/build/layout.tsv` |
| An omarchy-pkgs tarball from another commit | Run `fedora/bin/bump-pkgs-commit` (step 3) instead of editing pins by hand |

### 3. Check what the static checks cannot see

- **Arch-only references:** compare `fedora/bin/port-status --list` with `main`'s; a new file needs an override, a patch or a reason it never runs.
- **omarchy-pkgs:** in a clone of omacom/omarchy-pkgs, `git log <PKGS_COMMIT>..origin/master -- pkgbuilds/omarchy-dev pkgbuilds/omarchy-settings-dev` shows packaging changes to mirror into `fedora/rpm/omarchy*/`. Then `fedora/bin/recipe-status` lists every recipe whose PKGBUILD moved: port each (usually a version and checksums; `recipe-status` also flags a stale header line), then `fedora/bin/bump-pkgs-commit <omarchy-pkgs commit>` moves the pin, every recipe's `pkgs_commit` and the checksums of what they fetch from omarchy-pkgs. `fedora/bin/recipe-status --check` must pass.
- **Hyprland and Quickshell:** if upstream moved to a new version (`omarchy-hyprland-titlebars` pins Hyprland exactly), confirm nett00n/hyprland has it and move the lock in `fedora/repos/versionlock.toml`.

### 4. Pull request and CI

Push the branch and open a pull request titled `Sync upstream quattro (<sha>)` (the bot opens it itself; GitHub starts no CI run for a pull request the bot's token opened, so CI first runs when you push your fixes to its branch). CI must pass. Its `upstream-tests` job names every upstream test that fails only on the Fedora tree: a new upstream test usually asserts pacman, Limine, mkinitcpio or an ALPM hook (the first sync added four). Fix it, or list it in `fedora/tests/upstream-expected-failures.txt` with the reason; a test that fails at random on Arch too gets a reason starting with `flaky:`.

### 5. Merge, then let CI build

Merge with a merge commit. Never squash or rebase: the sync merge commit is what keeps upstream history in the fork. On `main`, CI's `copr` job builds the three core packages together and every recipe the merge changed (`fedora/bin/copr-build-changed`). If a build fails, its log is at `https://download.copr.fedorainfracloud.org/results/jersyj/omadora/srpm-builds/<build id>/builder-live.log.gz` (failed before building) or under `fedora-45-x86_64/<build id>-<name>/`; fix on a branch and merge again. By hand: `fedora/bin/copr-build-core`, never one core package alone (`omarchy` requires `omarchy-settings` of its exact release; dnf and the installer quietly keep the old pair otherwise).

### 6. Test in VMs, never on a workstation

```bash
sb=OMADORA_VM_SB_VARS=$HOME/.cache/omadora/OVMF_VARS.secboot-ms.4m.fd
iso=Fedora-Everything-netinst-x86_64-45.iso   # verified against Fedora's CHECKSUM

# A fresh laptop-style install: Secure Boot, LUKS, password typed at SDDM,
# keyring across passwd, lock screen (about 40 minutes)
env $sb OMADORA_VM_PACKAGED=1 OMADORA_VM_SECURE_BOOT=1 OMADORA_VM_PASSWORD_LOGIN=1 \
  fedora/tests/vm-install.sh $iso fedora/.build/vm-<date>
qemu-img snapshot -c tested fedora/.build/vm-<date>/disk.qcow2

# Upstream's graphical suite on it (the login test changed the password)
env $sb OMADORA_VM_PASSWORD=Kestrel-Window-2026 fedora/tests/vm-acceptance.sh fedora/.build/vm-<date>

# omarchy update on the previous sync's VM, from its "tested" snapshot
env $sb fedora/tests/vm-update.sh fedora/.build/vm-<previous date>

# When recipes of Omarchy's optional extras changed
env $sb OMADORA_VM_PASSWORD=Kestrel-Window-2026 fedora/tests/vm-extras.sh fedora/.build/vm-<date>
```

Triage a new acceptance failure like a test failure in step 4: a fix, or a line in `fedora/tests/acceptance-expected-failures.txt`. Upstream's acceptance tests lag its own changes now and then (the first sync moved the Apps menu to a new layer the test does not know yet); a failure that also happens on Arch is upstream drift, and the line says so. Keep this sync's VM: it is the next sync's update test. Delete older ones.

The update test fails on kernel SELinux denials (AVC) and only warns on systemd's own (USER_AVC). Fedora's package scriptlets can trip those while selinux-policy reloads in the same transaction: the first sync's update printed "Failed to set unit properties on docker.service: Access denied" (moby-engine's restart marker, rpm_script_t denied `start` on container_unit_file_t, during the selinux-policy 45.20 → 45.21 upgrade). It is harmless, since docker only misses its needs-restart marker, and reinstalling moby-engine without a policy change runs clean. A warning that persists without a policy update is ours to look at.

### What the first sync (2026-10-13) needed

| Found by | Issue | Change |
| --- | --- | --- |
| Static checks | `omarchy-update-keyring` drifted (pacman-only change) | Override reviewed, re-pinned |
| Static checks | Patches 0002 (menu guards) and 0007 (update restart) no longer applied | Re-created against the new files |
| Static checks | New migration 1791875754 | Reviewed: `run` |
| Review | `omarchy-system-reboot` was removed upstream, still called by our snapshot override | Fixed; a static check now catches this |
| `recipe-status` | Titlebars 0.2.2, Superwhisper 1.0.2 | Ported; the pin moved |
| CI's `copr` job | `omarchy-nvim` still had the old omarchy-pkgs tarball checksum | `bump-pkgs-commit` now does the whole pin move |
| CI's `upstream-tests` | Four new upstream tests assert pacman, Limine or ALPM hooks | Listed with reasons |
| VM acceptance suite | Upstream's Apps menu check is stale | Listed as upstream drift |

## One upstream fix before its release

Do not cherry-pick: that edits upstream files and breaks the invariant. Export the commit as a patch instead:

```bash
git format-patch -1 --stdout <sha> >fedora/patches/backport-<short-sha>.patch
```

Delete the patch once the synced commit contains it (`git merge-base --is-ancestor <sha> HEAD`).

## Between syncs

- **nett00n rebuilds Hyprland.** `omarchy-hyprland-titlebars` requires the exact Hyprland build it was compiled against, so dnf holds Hyprland back until the plugin is rebuilt: `copr-cli build-package jersyj/omadora --name omarchy-hyprland-titlebars`. Nothing breaks in the meantime; laptops just keep the previous build.
- **nett00n's Hyprland misses a dependency.** Our `omarchy` spec requires `xorg-x11-server-Xwayland` because nett00n's `hyprland` doesn't (`DECISIONS.md`). Check now and then with `dnf repoquery --requires hyprland`; once it lists it, remove the line from `fedora/rpm/omarchy/omarchy.spec`.
- **uwsm releases.** We build `uwsm` ourselves (`fedora/rpm/uwsm`, Arch's build options). When Arch's `extra/uwsm` moves to a new version, bump `Version`, `Release` and `sources.sha256`, then `copr-cli build-package jersyj/omadora --name uwsm`.
- **An app's upstream releases a fix.** Bump its recipe in `fedora/rpm/` and rebuild that one COPR package; the omarchy-pkgs pin moves with the next sync.
- **The weekly repository check fails** (`fedora-repos-check`, every Monday). A changed signing key: compare the new key with the repository's announcement, then replace it in `fedora/repos/keys/` (laptops get it with the next `omadora-repos`). A package set that no longer resolves: a third-party repository dropped a package or a build; find a replacement source (`DECISIONS.md`, source order). The run summary also lists COPRs that stopped building and which ones build for the next Fedora release.
