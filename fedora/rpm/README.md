# RPM recipes

These recipes are for the packages that our COPR, [jersyj/omadora](https://copr.fedorainfracloud.org/coprs/jersyj/omadora/), builds: the packages with the source `ours` in `fedora/packages/map.tsv`. Each package has one directory:

| File | Purpose |
| --- | --- |
| `<name>/<name>.spec` | The spec |
| `<name>/sources.sha256` | SHA-256 of each remote source. `build-srpm` checks the sources before it packs the SRPM. Required |
| `<name>/cargo-vendor` | Marker for Rust recipes: put the locked crates into the SRPM, so the build needs no network. If the file has content, the content is the top directory of the archive (`%version` is replaced) |
| Other files | Patches and local sources, copied next to the spec |

## Rules

- `Version` is upstream's `pkgver` and `Release` is upstream's `pkgrel`. Thus an Arch version check (`2026.9.21-5 or newer`) means the same build here. For a Fedora-only rebuild, add `.1`, `.2` and so on to `Release`.
- Recipes built from omacom/omarchy-pkgs pin it with `%global pkgs_commit`. The value must be `PKGS_COMMIT` from `fedora/upstream.lock`. `fedora/tests/static.sh` checks this.
- Pin sources to tags or commits. Do not use a branch.

## Build

CI builds what a push to `main` changed, after all checks pass. See the `copr` job in `.github/workflows/fedora-ci.yml` and `fedora/bin/copr-build-changed`. CI needs the `COPR_CONFIG` secret.

To add a new recipe:

1. Register the package one time:

   ```bash
   copr-cli add-package-scm jersyj/omadora --name <name> --clone-url https://github.com/JersyJ/omadora.git \
     --commit main --subdir fedora/rpm --spec <name>/<name>.spec --method make_srpm
   ```

2. Build it one time by hand. Then CI's package checks can resolve it.

COPR builds each package as an SCM package:

- It clones `https://github.com/JersyJ/omadora.git` and uses the spec `fedora/rpm/<name>/<name>.spec` with the method `make_srpm`.
- `.copr/Makefile` in the repository root calls `build-srpm`. COPR looks only there. `build-srpm` downloads and checks the sources, puts in the crates and packs the SRPM.

To build on a Fedora computer:

```bash
fedora/rpm/build-srpm fedora/rpm/tzupdate/tzupdate.spec /tmp/srpm
rpmbuild --rebuild /tmp/srpm/tzupdate-*.src.rpm
```

## Build environment

- **Network:** on. `omarchy-nvim` syncs LazyVim's plugins during its build. Rust recipes still build offline from their crates.
- **Extra repositories in the build root:**
  - nett00n/hyprland: `hyprland-devel` for `omarchy-hyprland-titlebars`, which pins the exact Hyprland build.
  - RPM Fusion free: full `ffmpeg`, whose H.264 encoder the `owe` tests need.

> **NOTE:** Until the Fedora 45 release (2026-10-20), RPM Fusion serves Fedora 45 from `development/45` and `updates/testing/45`. After the release, change the project to `releases/45/Everything/$basearch/os/` and `updates/45/$basearch/` with `copr-cli modify jersyj/omadora --repo ...`.

## Credits

Some recipes and `build-srpm` start from [kamm3r/omadora-pkg](https://github.com/kamm3r/omadora-pkg) and [whelanh/omarchy-fedora](https://github.com/whelanh/omarchy-fedora), both MIT licensed. Each spec gives its origin in its header.
