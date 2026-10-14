# Repositories

Each Omadora package comes from Fedora, from a repository in this directory, or from Flathub. `fedora/packages/map.tsv` gives the source of each package.

Each third-party repository has an `includepkgs=` limit with only the packages that we take from it. Thus no repository can replace a Fedora package such as sudo, glibc or the kernel.

| File | Installed as | Contents |
| --- | --- | --- |
| `omadora.repo` | `/etc/yum.repos.d/` | Our COPR, [jersyj/omadora](https://copr.fedorainfracloud.org/coprs/jersyj/omadora/) (`ours` in the map) |
| `nett00n-hyprland.repo` | `/etc/yum.repos.d/` | The Hyprland stack and Quickshell |
| `coprs.repo` | `/etc/yum.repos.d/` | Single-app COPRs: lazygit, gpu-screen-recorder, moonlight-qt |
| `mise.repo` | `/etc/yum.repos.d/` | mise's vendor repository |
| `microsoft.repo`, `microsoft-edge.repo` | `/etc/yum.repos.d/` | Intune Portal, its identity broker, Defender for Endpoint (Microsoft's RHEL 10 repository) and Edge. Company compliance requires them (`docs/INTUNE.md`) |
| `repos.override.d/50-omadora-rpmfusion.repo` | `/etc/dnf/repos.override.d/` | Limits for RPM Fusion. RPM Fusion's release packages own its repository files |
| `keys/*.asc` | `/etc/pki/rpm-gpg/omadora/` | Signing keys of the repositories above (`keys/sources.tsv` gives where each key is published) |
| `versionlock.toml` | `/etc/dnf/versionlock.toml` | Hyprland at 0.56.2, Quickshell at 0.3 |
| `on-demand/*.repo` | `/etc/yum.repos.d/`, when an app needs it | Vendor repositories and app COPRs for Omarchy's optional installers (`on-demand/README.md`) |

## Signing keys

`omadora-repos` imports the keys after each install or upgrade, together with Fedora's and RPM Fusion's keys. dnf5-automatic cannot answer a key prompt. Without the keys, the daily security updates fail on a fresh install. The weekly repository check compares the keys with the published keys.

## Checks

- `fedora/tests/static.sh` fails if a package that the map gives to a repository is not in that repository's `includepkgs`.
- `fedora/tests/resolve.sh` runs in CI, in a `fedora:45` container:
  - It installs these files.
  - It fails if a limited repository offers a package that its `includepkgs` does not allow.
  - It resolves the base package set. With `--optional`, it adds the on-demand repositories and resolves the optional set.
  - It lists the repository of each package.

## Change a limit

1. Add the package to the map.
2. Add the package to the repository's `includepkgs`. Globs are permitted for subpackage families, for example `kmod-v4l2loopback*`.

If a new dependency from a limited repository occurs, the resolution test gives its name.

## After the Fedora 45 release (2026-10-20)

RPM Fusion moves Fedora 45 from `development/45` to `releases/45`, and Fedora disables `updates-testing` by default. Update the COPR build repositories (`fedora/rpm/README.md`). The files in this directory need no change.
