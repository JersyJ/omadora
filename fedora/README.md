# Fedora layer

Everything that makes this fork Omarchy-on-Fedora lives here. Upstream files elsewhere in the repo are never edited; they stay byte-identical to the upstream commit pinned in `upstream.lock`, which is what lets the fork take every upstream sync without merge conflicts.

## The one rule

Do not edit files outside `fedora/`, `.copr/`, `.github/workflows/` and `.github/README.md`. `fedora/bin/check-invariant` (and CI) fails if you do. To change an upstream file, use one of the tools below.

| Need | Tool | Where |
| --- | --- | --- |
| Replace an upstream file that is wholly Arch-specific (pacman helpers, update pipeline) | Full override, pinned to the upstream version it was reviewed against | `overrides/<upstream path>` + `overrides.lock` (`bin/pin-override`) |
| Change a few lines in an otherwise portable, fast-moving file | Patch | `patches/NNNN-name.patch` (applied with `patch -p1` in name order) |
| Drop an Arch-only path | Exclusion | `build/exclude.txt` |
| Map an Arch package name to its Fedora source | Package map | `packages/map.tsv` |
| Decide whether an upstream migration runs on Fedora | Review row | `migrations/classify.tsv` (`bin/migrations-status`) |
| Take one upstream fix before the next sync | Backport patch | `patches/backport-<sha>.patch`, deleted once the synced commit contains it |

## Layout

| Path | Purpose |
| --- | --- |
| `upstream.lock` | Pinned upstream `quattro` commit, omarchy-pkgs commit, Fedora release |
| `bin/sync-upstream <ref>` | Sync upstream-owned paths to a commit (see `docs/SYNC.md`) |
| `bin/check-invariant` | Verify upstream-owned paths match the pinned commit |
| `bin/pin-override <path>` | Record that an override was reviewed against the current upstream file |
| `bin/migrations-status` | Summarize, check (`--check`) or add (`--update`) migration review rows |
| `bin/port-status [--list]` | Porting backlog: shipped files still referencing pacman, AUR, Limine, mkinitcpio or ufw |
| `bin/copr-build-changed <before> <after>` | Build in our COPR what those commits changed (CI runs it after a push to `main`) |
| `bin/recipe-status [--check]` | Our recipes against the omarchy-pkgs PKGBUILDs and Arch packages they mirror |
| `bin/bump-pkgs-commit <commit>` | Move the omarchy-pkgs pin: `upstream.lock`, every recipe's `pkgs_commit`, and the checksums of what they fetch from omarchy-pkgs |
| `bin/copr-build-core` | Build `omarchy`, `omarchy-settings` and `omadora-repos` in our COPR from the pushed commit, together |
| `bin/probe-hardware` | Read-only hardware report for a target laptop |
| `bin/kickstart` | Print the Anaconda kickstart that installs Omadora from the Fedora netinst ISO |
| `build/assemble` | Build the installable tree in `.build/` from upstream + this layer |
| `build/layout.tsv` | Every upstream top-level path, marked `ship` or `repo-only` |
| `overrides/`, `patches/` | Fedora replacements for upstream files (see the table above) |
| `packages/map.tsv` | Arch package name to Fedora name and source |
| `lib/runtime/pkg.sh` | The package layer behind the `omarchy-pkg-*` overrides; installed at `/usr/share/omarchy/fedora/pkg.sh` |
| `repos/` | Repository files, limits and version locks (`repos/README.md`) |
| `rpm/` | RPM recipes for our COPR, including `omarchy`, `omarchy-settings` and `omadora-repos` built from this tree (`rpm/README.md`) |
| `tests/static.sh` | The fast checks CI runs on every push |
| `tests/resolve.sh` | CI: resolve the base and optional package sets in a Fedora container |
| `tests/rpm.sh` | CI: build and install omarchy, omarchy-settings and omadora-repos, then exercise the package helpers |
| `tests/repos-check.sh` | Weekly (`.github/workflows/fedora-repos-check.yml`): repository signing keys against the published ones, COPR activity and next-release readiness |
| `tests/vm-install.sh` | Local: install Omadora into a KVM virtual machine from the netinst ISO and report its first boot; `OMADORA_VM_PASSWORD_LOGIN=1` installs and logs in as on a laptop and checks the login keyring across a `passwd` change |
| `tests/vm-password-login.sh` | Local: on such a VM, unlock the disk, log in at SDDM, change the password with `passwd`, reboot and log in again, checking the login keyring each time |
| `tests/vm-acceptance.sh` | Local: run upstream's graphical acceptance suite inside such a VM's desktop session; expected failures with reasons in `tests/acceptance-expected-failures.txt` |
| `tests/vm-extras.sh` | Local: install each of Omarchy's optional extras in such a VM through Omarchy's own package command, and check each starts |
| `tests/vm-console.py` | Local: boot that virtual machine and run commands on its serial console |
| `docs/` | Research, decisions, sync runbook, hardware notes, installing a laptop (`INSTALL.md`), Intune requirements |

## Common commands

```bash
fedora/tests/static.sh                     # all checks, as CI runs them
fedora/build/assemble                      # build fedora/.build/omarchy-<version>/
fedora/bin/port-status --list              # what is left to port
fedora/bin/sync-upstream upstream/quattro  # take upstream's latest quattro
fedora/bin/kickstart --user NAME --password-hash "$(openssl passwd -6)" >omadora.ks
fedora/tests/vm-install.sh Fedora-Everything-netinst-x86_64-45.iso  # full install test
```

Remotes: `origin` is this fork (https://github.com/JersyJ/omadora), `upstream` is https://github.com/omacom/omarchy.git. A fresh clone needs `git remote add upstream https://github.com/omacom/omarchy.git` before syncing.
