# RPM recipes

Recipes for the packages our COPR, [jersyj/omadora](https://copr.fedorainfracloud.org/coprs/jersyj/omadora/), builds: the packages with `ours` as their source in `fedora/packages/map.tsv`. One directory per package:

| File | Purpose |
| --- | --- |
| `<name>/<name>.spec` | The spec |
| `<name>/sources.sha256` | SHA-256 of every remote source, checked before the SRPM is packed. Required |
| `<name>/cargo-vendor` | Marker for Rust recipes: vendor the locked crates into the SRPM so the binary build needs no network. Its content, if any, names the archive's top directory (`%version` is substituted) |
| other files | Patches and local sources, copied next to the spec |

## Conventions

- `Version` is upstream's `pkgver` and `Release` is upstream's `pkgrel`, so a version check written for Arch (`2026.9.21-5 or newer`) means the same build here. A Fedora-only rebuild appends `.1`, `.2`, … to `Release`.
- Recipes built from omacom/omarchy-pkgs pin it with `%global pkgs_commit`, which must equal `PKGS_COMMIT` in `fedora/upstream.lock` (`fedora/tests/static.sh` checks this).
- Sources are pinned to tags or commits, never to a moving branch.

## Building

COPR builds each package as an SCM package: clone `https://github.com/JersyJ/omadora.git`, spec `fedora/rpm/<name>/<name>.spec`, method `make_srpm`. The repository root's `.copr/Makefile` (COPR only looks there) calls `build-srpm`, which downloads and verifies the sources, vendors crates and packs the SRPM. On a Fedora machine:

```bash
fedora/rpm/build-srpm fedora/rpm/tzupdate/tzupdate.spec /tmp/srpm
rpmbuild --rebuild /tmp/srpm/tzupdate-*.src.rpm
```

The project has network access enabled because `omarchy-nvim` runs LazyVim's plugin sync during its build. Rust recipes still build offline from their vendored crates.

## Credits

Several recipes and `build-srpm` start from [kamm3r/omadora-pkg](https://github.com/kamm3r/omadora-pkg) and [whelanh/omarchy-fedora](https://github.com/whelanh/omarchy-fedora), both MIT licensed. Each spec names its origin in its header.
