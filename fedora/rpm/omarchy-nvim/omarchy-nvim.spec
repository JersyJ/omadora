# Mirrors omacom/omarchy-pkgs pkgbuilds/omarchy-nvim at the omarchy-pkgs commit
# pinned in fedora/upstream.lock (PKGS_COMMIT); keep pkgs_commit equal to it.
# The build runs LazyVim's plugin sync, so the COPR needs network access.
# Based on kamm3r/omadora-pkg (MIT).

%global debug_package %{nil}
%global pkgs_commit e499d021c69d27e0750f77f9af7cd68534c8016f
%global starter_commit 803bc181d7c0d6d5eeba9274d9be49b287294d99

Name:           omarchy-nvim
Version:        2026.9.21
Release:        5%{?dist}
Summary:        Pre-built LazyVim configuration with cached plugins
License:        MIT
URL:            https://github.com/LazyVim/LazyVim
Source0:        https://github.com/LazyVim/starter/archive/%{starter_commit}.tar.gz#/%{name}-starter-%{version}.tar.gz
Source1:        https://github.com/omacom/omarchy-pkgs/archive/%{pkgs_commit}.tar.gz#/omarchy-pkgs-%{pkgs_commit}.tar.gz
BuildArch:      noarch
BuildRequires:  git
BuildRequires:  gcc
BuildRequires:  nodejs
BuildRequires:  npm
BuildRequires:  tree-sitter-cli
BuildRequires:  neovim
Requires:       neovim >= 0.9.0
Requires:       git
Requires:       xdg-utils

%description
Omarchy's LazyVim configuration with its plugins cached, copied to new users
through /etc/skel.

%prep
%setup -q -c -T -a 0 -a 1

%build
slim_lazy_repos() {
  local data_dir="$1"
  local dir

  for dir in "$data_dir"/lazy/*/; do
    [[ -d "$dir/.git" ]] || continue

    # Exclude test suites via sparse-checkout rather than rm: the worktree
    # stays clean, so the restore pass in %%install does not resurrect them
    # and future :Lazy checkouts keep honoring the exclusion. snacks.nvim
    # alone ships 18 MB of tests.
    git -C "$dir" sparse-checkout set --no-cone '/*' '!/test/' '!/tests/' '!/spec/'

    # Cut history down to the checked-out tips: drop the refs that pin older
    # objects, mark every remaining tip as a shallow boundary, then gc. This
    # is half the package -- ~70 MB of .git across the plugins. `git fetch`
    # into a shallow repo stays shallow and re-fetches tags, so :Lazy update
    # still works.
    #
    # Keep refs/remotes/origin/HEAD. It pins no objects (it is a symref, and
    # stays readable after its target ref is gone), but lazy.nvim resolves the
    # default branch through it for plugins parked on a detached HEAD by a
    # version pin -- lazy.nvim, LazyVim and blink.cmp. Without it, get_branch()
    # returns nil and every lockfile write asserts, so :Lazy install/update/sync
    # dies with E5113 on a fresh install.
    git -C "$dir" for-each-ref --format='%%(refname)' refs/remotes refs/tags |
      while IFS= read -r ref; do
        [[ $ref == refs/remotes/origin/HEAD ]] && continue
        git -C "$dir" update-ref -d "$ref"
      done
    rm -f "$dir/.git/FETCH_HEAD" "$dir/.git/ORIG_HEAD"
    {
      git -C "$dir" rev-parse HEAD
      git -C "$dir" for-each-ref --format='%%(objectname)' refs/heads
    } | sort -u >"$dir/.git/shallow"
    git -C "$dir" reflog expire --expire=all --all

    # lazy.nvim clones with --filter=blob:none, which marks the pack as a
    # promisor pack that gc refuses to repack or prune. The repo is shallow
    # at its tips now, so everything reachable exists locally: drop the
    # promisor markers and the stale commit-graph, then gc for real. Future
    # fetches simply run unfiltered.
    git -C "$dir" config --unset-all remote.origin.promisor || true
    git -C "$dir" config --unset-all remote.origin.partialclonefilter || true
    rm -f "$dir/.git/objects/pack/"*.promisor "$dir/.git/objects/info/commit-graph"
    rm -rf "$dir/.git/objects/info/commit-graphs"
    git -C "$dir" -c gc.writeCommitGraph=false gc --prune=now --quiet
  done
}

export HOME="$PWD/nvim-build-home"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"
export XDG_CACHE_HOME="$HOME/.cache"

mkdir -p "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_STATE_HOME" "$XDG_CACHE_HOME"

# Setup LazyVim starter
cp -a "$PWD/starter-%{starter_commit}" "$XDG_CONFIG_HOME/nvim"
rm -rf "$XDG_CONFIG_HOME/nvim/.git"

# Omarchy's additions, verbatim from omarchy-pkgs (the PKGBUILD copies its
# lua/, plugin/ and lazyvim.json the same way)
recipe="$PWD/omarchy-pkgs-%{pkgs_commit}/pkgbuilds/omarchy-nvim"
cp -r "$recipe/lua" "$recipe/plugin" "$XDG_CONFIG_HOME/nvim/"
cp "$recipe/lazyvim.json" "$XDG_CONFIG_HOME/nvim/"

echo "Installing LazyVim plugins..."
nvim --headless \
  "+Lazy! sync" \
  "+qa!" || true

echo "Slimming plugin repos..."
slim_lazy_repos "$XDG_DATA_HOME/nvim"

%install
restore_lazy_worktrees() {
  local data_dir="$1"
  local dir

  for dir in "$data_dir"/lazy/*/; do
    [[ -d "$dir/.git" ]] || continue
    git --git-dir="$dir/.git" --work-tree="$dir" restore .
  done
}

export HOME="$PWD/nvim-build-home"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share"

install -dm755 %{buildroot}%{_datadir}/%{name}

cp -a "$XDG_CONFIG_HOME/nvim" %{buildroot}%{_datadir}/%{name}/config
cp -a "$XDG_DATA_HOME/nvim" %{buildroot}%{_datadir}/%{name}/data

# Remove everything from site/ directory but keep the directory to prevent error
rm -rf %{buildroot}%{_datadir}/%{name}/data/site/*
mkdir -p %{buildroot}%{_datadir}/%{name}/data/site

# Fix permissions to be readable by all users
chmod -R 755 %{buildroot}%{_datadir}/%{name}
find %{buildroot}%{_datadir}/%{name} -type f -exec chmod 644 {} \;

# Restore plugin worktree modes after the package-wide chmod so users seeded
# from /etc/skel do not need a first-login omarchy-nvim-setup cleanup pass.
restore_lazy_worktrees %{buildroot}%{_datadir}/%{name}/data

# Cached plugins contain development scripts with /usr/bin/env python.
# Normalize their shebangs to Fedora's Python 3 before the RPM policy check.
find %{buildroot}%{_datadir}/%{name} -type f -name "*.py" \
  -exec sed -i '1s|^#!/usr/bin/env python$|#!/usr/bin/python3|' {} +

# Seed new users via /etc/skel. The installer installs omarchy-nvim before
# creating the first user, so this handles initial ISO installs and future
# users without an extra overwrite step.
install -dm755 %{buildroot}/etc/skel/.config %{buildroot}/etc/skel/.local/share
cp -a %{buildroot}%{_datadir}/%{name}/config %{buildroot}/etc/skel/.config/nvim
cp -a %{buildroot}%{_datadir}/%{name}/data %{buildroot}/etc/skel/.local/share/nvim
ln -snf "../../../../.local/state/omarchy/current/theme/neovim.lua" \
  %{buildroot}/etc/skel/.config/nvim/lua/plugins/theme.lua

# Ship the plugin cache once, now that /etc/skel has its copy. Keeping a
# second one under /usr/share made omarchy-nvim the largest package in an
# Omarchy install after noto-fonts-cjk — ~116 MiB installed, ~88 MB of it read
# off the ISO on every install. config/ stays: migrations read it from there.
rm -rf %{buildroot}%{_datadir}/%{name}/data

# Install setup/refresh commands to /usr/bin. setup fills missing pieces;
# refresh explicitly backs up and overwrites with the same /etc/skel defaults
# used for newly-created users.
install -Dm755 "$PWD/omarchy-pkgs-%{pkgs_commit}/pkgbuilds/omarchy-nvim/omarchy-nvim-setup" %{buildroot}%{_bindir}/omarchy-nvim-setup
ln -s omarchy-nvim-setup %{buildroot}%{_bindir}/omarchy-nvim-refresh

%files
%license starter-%{starter_commit}/LICENSE
%{_datadir}/%{name}/config
%{_bindir}/omarchy-nvim-setup
%{_bindir}/omarchy-nvim-refresh
/etc/skel/.config/nvim
/etc/skel/.local/share/nvim

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 2026.9.21-5
- Package for Omadora from omarchy-pkgs 87ed2a7e, based on kamm3r/omadora-pkg.
