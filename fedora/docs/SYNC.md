# Syncing upstream

`main` follows upstream's `quattro` branch, pinned to one commit in `fedora/upstream.lock`. `quattro` gets approximately 200 commits every 2 weeks.

- **Automatic:** each second Monday, the `fedora-sync` workflow syncs to the `quattro` tip and opens the pull request `Sync upstream quattro (<sha>)`. You can also start it from the Actions tab.
- **Manual:** the runbook below.

> **CAUTION:** Do not use GitHub's "Sync fork" button. It merges without a change to `upstream.lock` and without the checks.

## Why a sync has no conflicts

`fedora/bin/sync-upstream <ref>` records a real merge of `<ref>`, so `git log` shows all upstream commits. But the script builds the result tree mechanically:

- Upstream paths come unchanged from `<ref>`.
- Fork paths (`fedora/`, `.copr/`, `.github/workflows/`, `.github/README.md`) come unchanged from the current branch.

Nothing merges line by line, so nothing conflicts. This also works between upstream lines: a plain `git merge` from a v4.0.x release branch to `quattro` conflicts in 20+ files.

The work moves from conflicts to review. You must port by hand the upstream changes to files that we override or patch. The checks below find all of them.

## Runbook

The first sync (2026-10-13, approximately 60 commits) took one afternoon, mostly VM time. Do all steps on a branch. Change `main` only by merging the pull request.

### 1. Sync on a branch

Use the bot's pull request branch, or start a branch:

```bash
git switch -c sync/$(date +%F) main
fedora/bin/sync-upstream upstream/quattro     # a merge commit, no conflicts
fedora/tests/static.sh
```

### 2. Correct the static check failures

| Failure | Action |
| --- | --- |
| Override drifted | Run `git diff <pinned blob> <new blob>` (the check prints both). Port what applies into `fedora/overrides/<path>`; a pacman-only change needs nothing. Read the override's comments again. Run `fedora/bin/pin-override <path>` |
| Patch does not apply | Copy the new upstream file to `a/<path>` and `b/<path>` in a scratch directory. Make the Fedora change again in `b/`. Put `diff -u a/<path> b/<path>` below the patch's header lines. Keep the change the same size |
| Migration missing, changed or unreviewed | Run `fedora/bin/migrations-status --update`. Set each `unreviewed` row to `run`, `skip` or `replace:<file>`, with a reason. Until then, the build does not include the migration |
| Removed upstream command still called | `git log -- bin/<name>` shows the replacement. Example: `omarchy-system-reboot` became `omarchy-system reboot` |
| Unmapped package | Add it to `fedora/packages/map.tsv`. Use the source order in `DECISIONS.md` |
| Unclassified top-level path | Mark it `ship` or `repo-only` in `fedora/build/layout.tsv` |
| omarchy-pkgs tarball from another commit | Run `fedora/bin/bump-pkgs-commit` (step 3). Do not change the pins by hand |

For each new migration, also check a fresh install. A fresh install marks all shipped migrations done and does not run them. If a migration removes something that only Arch's install leaves out (for example a Fedora weak dependency), make the same change in the kickstart. Example: `cups-browsed` (2026-10-13).

### 3. Check what the static checks cannot see

- **Arch-only references:** compare `fedora/bin/port-status --list` with the output on `main`. A new file needs an override, a patch, or a reason why it never runs.
- **omarchy-pkgs:**
  1. In a clone of omacom/omarchy-pkgs, run `git log <PKGS_COMMIT>..origin/master -- pkgbuilds/omarchy-dev pkgbuilds/omarchy-settings-dev`. Copy the packaging changes into `fedora/rpm/omarchy*/`.
  2. Run `fedora/bin/recipe-status`. Port each recipe whose PKGBUILD changed (usually a version and checksums).
  3. Run `fedora/bin/bump-pkgs-commit <omarchy-pkgs commit>`. This moves the pin, each recipe's `pkgs_commit` and the checksums.
  4. `fedora/bin/recipe-status --check` must pass.
- **Hyprland and Quickshell:** if upstream uses a new version, make sure that nett00n/hyprland has it. Then move the lock in `fedora/repos/versionlock.toml`. `omarchy-hyprland-titlebars` pins the exact Hyprland version.

### 4. Pull request and CI

1. Push the branch. Open a pull request with the title `Sync upstream quattro (<sha>)`. The bot opens its pull request itself, but CI starts only when you push to its branch.
2. CI must pass. The `upstream-tests` job names each upstream test that fails only on the Fedora tree. A new upstream test often checks pacman, Limine, mkinitcpio or an ALPM hook.
3. Correct the test failure, or add the test to `fedora/tests/upstream-expected-failures.txt` with the reason. If the test also fails at random on Arch, start the reason with `flaky:`.

### 5. Merge and build

1. Merge with a merge commit. Do not squash or rebase: the merge commit keeps the upstream history.
2. On `main`, CI's `copr` job builds the 3 core packages and each changed recipe (`fedora/bin/copr-build-changed`).
3. If a build fails, read its log:
   - Failure before the build: `https://download.copr.fedorainfracloud.org/results/jersyj/omadora/srpm-builds/<build id>/builder-live.log.gz`
   - Failure in the build: `fedora-45-x86_64/<build id>-<name>/` in the same location
4. Correct the failure on a branch and merge again.

> **CAUTION:** To build by hand, use `fedora/bin/copr-build-core`. Do not build one core package alone. `omarchy` requires `omarchy-settings` of the same release. Without it, dnf and the installer keep the old pair without a message.

### 6. Test in VMs

> **WARNING:** Do not run these tests on a workstation. Use VMs only.

```bash
sb=OMADORA_VM_SB_VARS=$HOME/.cache/omadora/OVMF_VARS.secboot-ms.4m.fd
iso=Fedora-Everything-netinst-x86_64-45.iso   # verified against Fedora's CHECKSUM

# Fresh install as on a laptop: Secure Boot, LUKS, typed password,
# keyring across passwd, lock screen (approximately 40 minutes)
env $sb OMADORA_VM_PACKAGED=1 OMADORA_VM_SECURE_BOOT=1 OMADORA_VM_PASSWORD_LOGIN=1 \
  fedora/tests/vm-install.sh $iso fedora/.build/vm-<date>
qemu-img snapshot -c tested fedora/.build/vm-<date>/disk.qcow2

# Upstream's graphical suite (the login test changed the password)
env $sb OMADORA_VM_PASSWORD=Kestrel-Window-2026 fedora/tests/vm-acceptance.sh fedora/.build/vm-<date>

# omarchy update on the VM of the previous sync, from its "tested" snapshot
env $sb fedora/tests/vm-update.sh fedora/.build/vm-<previous date>

# Only if the recipes of Omarchy's optional extras changed
env $sb OMADORA_VM_PASSWORD=Kestrel-Window-2026 fedora/tests/vm-extras.sh fedora/.build/vm-<date>
```

- **Acceptance failure:** correct it, or add a line to `fedora/tests/acceptance-expected-failures.txt`. If the failure also occurs on Arch, the line says "upstream drift". Example: the first sync moved the Apps menu to a layer that the test does not know.
- **VM to keep:** keep this sync's VM for the next sync's update test. Delete older VMs.
- **SELinux in the update test:** kernel denials (AVC) fail the test. systemd's own denials (USER_AVC) give a warning only.
  - Fedora's package scriptlets can cause a USER_AVC while selinux-policy reloads in the same transaction. Example from the first sync: "Failed to set unit properties on docker.service: Access denied" during the selinux-policy 45.20 to 45.21 upgrade. This is harmless.
  - If a warning occurs without a policy update, examine it.

> **NOTE:** The VMs do not find all defects. The first ZBook found 7 defects that the VMs did not show (`HARDWARE.md`). The VMs have no Wi-Fi, no Bluetooth and no graphical boot screen.

### First sync (2026-10-13)

| Found by | Problem | Change |
| --- | --- | --- |
| Static checks | `omarchy-update-keyring` drifted (pacman-only change) | Reviewed, pinned again |
| Static checks | Patches 0002 (menu guards) and 0007 (update restart) did not apply | Made again for the new files |
| Static checks | New migration 1791875754 | Reviewed: `run` |
| Review | Our snapshot override called `omarchy-system-reboot`, removed upstream | Corrected. A static check now finds this |
| `recipe-status` | Titlebars 0.2.2, Superwhisper 1.0.2 | Ported. The pin moved |
| CI `copr` job | `omarchy-nvim` had the old omarchy-pkgs tarball checksum | `bump-pkgs-commit` now moves all of the pin |
| CI `upstream-tests` | 4 new upstream tests check pacman, Limine or ALPM hooks | Listed with reasons |
| VM acceptance suite | Upstream's Apps menu check is out of date | Listed as upstream drift |

## One upstream fix before the next sync

Do not cherry-pick: a cherry-pick changes upstream files. Export the commit as a patch:

```bash
git format-patch -1 --stdout <sha> >fedora/patches/backport-<short-sha>.patch
```

When the synced commit contains the fix (`git merge-base --is-ancestor <sha> HEAD`), delete the patch.

## Between syncs

| Event | Action |
| --- | --- |
| nett00n builds a new Hyprland | `omarchy-hyprland-titlebars` needs the exact Hyprland build, so dnf keeps the old Hyprland. Build the plugin again: `copr-cli build-package jersyj/omadora --name omarchy-hyprland-titlebars`. Until then, laptops keep the previous Hyprland |
| nett00n's Hyprland adds Xwayland | Run `dnf repoquery --requires hyprland` from time to time. If it lists `xorg-x11-server-Xwayland`, remove that line from `fedora/rpm/omarchy/omarchy.spec` |
| Arch's `extra/uwsm` has a new version | In `fedora/rpm/uwsm`, change `Version`, `Release` and `sources.sha256`. Run `copr-cli build-package jersyj/omadora --name uwsm` |
| An app releases a fix | Change its recipe in `fedora/rpm/` and build that package. The omarchy-pkgs pin moves with the next sync |
| Weekly repository check fails (`fedora-repos-check`, each Monday) | Changed signing key: compare the key with the repository's announcement, then replace it in `fedora/repos/keys/`. Package set does not resolve: a repository removed a package or build; find a new source (`DECISIONS.md`). The summary also lists COPRs that stopped building and COPRs that build for the next Fedora release |
