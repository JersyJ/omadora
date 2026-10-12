# shellcheck shell=bash
# Shared helpers for the Fedora fork tooling. Sourced, never executed.

FEDORA_ROOT=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)
FEDORA_DIR="$FEDORA_ROOT/fedora"
FEDORA_LOCK="$FEDORA_DIR/upstream.lock"

# Paths this fork owns. Everything else belongs to upstream and must stay
# byte-identical to the commit pinned in fedora/upstream.lock. Fedora changes to
# upstream files live in fedora/overrides and fedora/patches instead.
FORK_OWNED_PATHS=(fedora .copr .github/workflows .github/README.md)

die() {
  echo -e "\033[31merror:\033[0m $*" >&2
  exit 1
}

warn() {
  echo -e "\033[33mwarning:\033[0m $*" >&2
}

info() {
  echo -e "\033[1m==>\033[0m $*"
}

load_lock() {
  [[ -f $FEDORA_LOCK ]] || die "missing $FEDORA_LOCK"
  # shellcheck source=/dev/null
  source "$FEDORA_LOCK"
  [[ -n ${UPSTREAM_COMMIT:-} ]] || die "UPSTREAM_COMMIT is not set in $FEDORA_LOCK"
}

set_lock_value() {
  local key=$1 value=$2

  if grep -q "^$key=" "$FEDORA_LOCK"; then
    sed -i "s|^$key=.*|$key=$value|" "$FEDORA_LOCK"
  else
    echo "$key=$value" >>"$FEDORA_LOCK"
  fi
}

# RPM version of the pinned upstream commit, in upstream's own omarchy-dev
# format: <last release>.r<total commits>.g<short hash>, e.g. 4.0.0.r6912.gdefbf90.
# Needs load_lock. Uses no tags, so it works in clones without them.
omadora_version() {
  local count

  count=$(git -C "$FEDORA_ROOT" rev-list --count "$UPSTREAM_COMMIT") || return 1
  echo "${UPSTREAM_VERSION%%-*}.r$count.g${UPSTREAM_COMMIT:0:7}"
}

# RPM release for the fork's HEAD: fork commits since the pinned upstream
# commit, then HEAD's short hash, e.g. 26.g98bd9ac. It only grows on main.
omadora_release() {
  local count

  count=$(git -C "$FEDORA_ROOT" rev-list --count "$UPSTREAM_COMMIT..HEAD") || return 1
  echo "$count.g$(git -C "$FEDORA_ROOT" rev-parse --short=7 HEAD)"
}

# Pathspecs that select upstream-owned paths only, one per line.
upstream_pathspec() {
  local path

  echo "."
  for path in "${FORK_OWNED_PATHS[@]}"; do
    echo ":(exclude)$path"
  done
}

# Package names from the upstream lists that apply to x86_64 at HEAD, one per
# line: the base list, the x86_64-only list and the hardware-dependent "other"
# list. The aarch64 lists are out of scope for this fork.
upstream_package_names() {
  local list

  for list in base other x86_64-only; do
    git -C "$FEDORA_ROOT" show "HEAD:install/omarchy-$list.packages" 2>/dev/null
  done | sed -e 's/[[:space:]]*#.*$//' -e '/^[[:space:]]*$/d' | sort -u
}

# Arch package names mapped in fedora/packages/map.tsv, one per line.
mapped_package_names() {
  grep -v '^#' "$FEDORA_DIR/packages/map.tsv" | tail -n +2 | cut -f1 | sort -u
}
