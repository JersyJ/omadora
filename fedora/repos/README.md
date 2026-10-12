# Repositories

Every package Omadora installs comes from Fedora, from a repository in this directory, or from Flathub. `fedora/packages/map.tsv` says which; each third-party repository is limited with `includepkgs=` to exactly the packages taken from it, so none of them can replace a Fedora package such as sudo, glibc or the kernel.

| File | Installed as | Contents |
| --- | --- | --- |
| `omadora.repo` | `/etc/yum.repos.d/` | Our COPR, [jersyj/omadora](https://copr.fedorainfracloud.org/coprs/jersyj/omadora/) (`ours` in the map) |
| `nett00n-hyprland.repo` | `/etc/yum.repos.d/` | The Hyprland stack and Quickshell |
| `coprs.repo` | `/etc/yum.repos.d/` | Single-app COPRs: lazygit, lazydocker, gpu-screen-recorder, moonlight-qt |
| `mise.repo` | `/etc/yum.repos.d/` | mise's vendor repository |
| `repos.override.d/50-omadora-rpmfusion.repo` | `/etc/dnf/repos.override.d/` | Limits for RPM Fusion, whose own release packages own its repo files |
| `versionlock.toml` | `/etc/dnf/versionlock.toml` | Hyprland held at 0.56.2, Quickshell at 0.3 |
| `on-demand/*.repo` | `/etc/yum.repos.d/`, when an app needs it | Vendor repositories and app COPRs for Omarchy's optional installers; see `on-demand/README.md` |

## Checks

- `fedora/tests/static.sh` fails when a package the map assigns to a repository is missing from that repository's `includepkgs`.
- `fedora/tests/resolve.sh` (CI, in a `fedora:45` container) installs these files, fails when a limited repository offers anything its `includepkgs` does not allow, and resolves the base package set; `--optional` adds the on-demand repositories and resolves the optional set. It also lists which repository each package comes from.

## Changing a limit

Add the package to the map, then to the repository's `includepkgs` (globs are fine for subpackage families such as `kmod-v4l2loopback*`). When a new dependency from a limited repository appears, the resolution test names it.

## After Fedora 45's release (2026-10-20)

RPM Fusion moves Fedora 45 from `development/45` to `releases/45`, and `updates-testing` stops being enabled by default. Update the COPR build repositories (see `fedora/rpm/README.md`); the files here need no change.
