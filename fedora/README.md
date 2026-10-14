# Fedora layer

This directory makes the fork Omarchy on Fedora. Upstream files outside it stay byte-identical to the upstream commit in `upstream.lock`. Because of this, upstream syncs have no merge conflicts.

## The one rule

Do not edit files outside `fedora/`, `.copr/`, `.github/workflows/` and `.github/README.md`. `fedora/bin/check-invariant` and CI fail if you do. To change an upstream file, use one of these tools:

| Need | Tool | Where |
| --- | --- | --- |
| Replace an Arch-specific upstream file (pacman helpers, update pipeline) | Full override, pinned to the reviewed upstream version | `overrides/<upstream path>` + `overrides.lock` (`bin/pin-override`) |
| Change some lines in a portable file that changes often | Patch | `patches/NNNN-name.patch` (applied with `patch -p1`, in name order) |
| Remove an Arch-only path | Exclusion | `build/exclude.txt` |
| Map an Arch package name to its Fedora source | Package map | `packages/map.tsv` |
| Decide if an upstream migration runs on Fedora | Review row | `migrations/classify.tsv` (`bin/migrations-status`) |
| Take one upstream fix before the next sync | Backport patch | `patches/backport-<sha>.patch`; delete it when the synced commit has the fix |

## Layout

| Path | Purpose |
| --- | --- |
| `upstream.lock` | Pinned upstream `quattro` commit, omarchy-pkgs commit, Fedora release |
| `bin/sync-upstream <ref>` | Sync the upstream paths to a commit (`docs/SYNC.md`) |
| `bin/check-invariant` | Check that the upstream paths match the pinned commit |
| `bin/pin-override <path>` | Record that an override was reviewed against the current upstream file |
| `bin/migrations-status` | Show (`--check`) or add (`--update`) migration review rows |
| `bin/port-status [--list]` | Porting backlog: shipped files that still use pacman, AUR, Limine, mkinitcpio or ufw |
| `bin/copr-build-changed <before> <after>` | Build in our COPR what these commits changed. CI runs it after each push to `main` |
| `bin/ci-changes <base> <head>` | Decide which CI checks a change needs. CI skips a check only if all changed files are paths that the check does not read |
| `bin/copr-build-core` | Build `omarchy`, `omarchy-settings` and `omadora-repos` in our COPR from the pushed commit |
| `bin/recipe-status [--check]` | Compare our recipes with the omarchy-pkgs PKGBUILDs and Arch packages |
| `bin/bump-pkgs-commit <commit>` | Move the omarchy-pkgs pin: `upstream.lock`, each recipe's `pkgs_commit`, and the checksums of its omarchy-pkgs sources |
| `bin/probe-hardware` | Read-only hardware report for a target laptop |
| `bin/kickstart` | Print the kickstart that installs Omadora from the Fedora netinst ISO |
| `bin/usb-image <iso> <ks.cfg> <out.img>` | Build a one-stick installer image: the ISO with the kickstart added (`docs/INSTALL.md`) |
| `build/assemble` | Build the installable tree in `.build/` from upstream and this layer |
| `build/layout.tsv` | Each upstream top-level path, marked `ship` or `repo-only` |
| `overrides/`, `patches/` | Fedora replacements for upstream files (table above) |
| `packages/map.tsv` | Arch package name to Fedora name and source |
| `lib/runtime/pkg.sh` | Package layer for the `omarchy-pkg-*` overrides; installed as `/usr/share/omarchy/fedora/pkg.sh` |
| `repos/` | Repository files, limits and version locks (`repos/README.md`) |
| `rpm/` | RPM recipes for our COPR, also `omarchy`, `omarchy-settings` and `omadora-repos` (`rpm/README.md`) |
| `docs/` | Research, decisions, sync runbook, hardware, laptop install (`INSTALL.md`), Intune requirements |

## Tests

| Test | Where it runs | What it does |
| --- | --- | --- |
| `tests/static.sh` | CI, each push | Fast checks |
| `tests/resolve.sh` | CI | Resolve the base and optional package sets in a Fedora container |
| `tests/rpm.sh` | CI | Build and install `omarchy`, `omarchy-settings` and `omadora-repos`, then run the package helpers |
| `tests/repos-check.sh` | CI, weekly (`.github/workflows/fedora-repos-check.yml`) | Compare repository signing keys with the published keys; check COPR activity and readiness for the next release |
| `tests/vm-install.sh` | Local VM | Install Omadora from the netinst ISO and report the first boot. `OMADORA_VM_PASSWORD_LOGIN=1` logs in as on a laptop and checks the login keyring across a `passwd` change |
| `tests/vm-password-login.sh` | Local VM | Unlock the disk, log in at SDDM, change the password, reboot, log in again; check the login keyring each time |
| `tests/vm-acceptance.sh` | Local VM | Run upstream's graphical acceptance suite in the desktop session. Expected failures and reasons: `tests/acceptance-expected-failures.txt` |
| `tests/vm-update.sh` | Local VM | Run `omarchy update` on a VM from the previous sync; check the version moved, with no failed units or SELinux denials |
| `tests/vm-extras.sh` | Local VM | Install each optional extra with Omarchy's package command; check that each starts |
| `tests/vm-console.py` | Local VM | Boot the VM and run commands on its serial console, its screen or its QEMU monitor |

## Common commands

```bash
fedora/tests/static.sh                     # all checks, as CI runs them
fedora/build/assemble                      # build fedora/.build/omarchy-<version>/
fedora/bin/port-status --list              # what is left to port
fedora/bin/sync-upstream upstream/quattro  # take upstream's latest quattro
fedora/bin/kickstart --user NAME --password-hash "$(openssl passwd -6)" >omadora.ks
fedora/tests/vm-install.sh Fedora-Everything-netinst-x86_64-45.iso  # full install test
```

## Remotes

- `origin`: this fork, https://github.com/JersyJ/omadora
- `upstream`: https://github.com/omacom/omarchy.git

On a new clone, add upstream before you sync: `git remote add upstream https://github.com/omacom/omarchy.git`.
