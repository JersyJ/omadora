# shellcheck shell=bash
# Omadora's package layer, sourced by the Fedora overrides of omarchy-pkg-*.
#
# Omarchy names Arch packages. fedora/packages/map.tsv, installed at
# /usr/share/omarchy/fedora/packages/map.tsv, says where each comes from on
# Fedora: Fedora itself, a COPR, RPM Fusion, our COPR, a vendor repository,
# Flathub or mise; or that it is not needed (drop) or not packaged yet (todo).
# A name the map does not know is taken as a Fedora package name.
#
# Installed at /usr/share/omarchy/fedora/pkg.sh.

OMADORA_PKG_MAP=${OMADORA_PKG_MAP:-/usr/share/omarchy/fedora/packages/map.tsv}
OMADORA_ON_DEMAND_REPOS=${OMADORA_ON_DEMAND_REPOS:-/usr/share/omadora/repos/on-demand}
OMADORA_FLATHUB_URL=https://dl.flathub.org/repo/flathub.flatpakrepo

omadora_pkg_error() {
  echo -e "\033[31mError: $*\033[0m" >&2
}

omadora_as_root() {
  if (( EUID == 0 )); then
    "$@"
  else
    sudo "$@"
  fi
}

# Print "<source>\t<name>\t<note>" for every Fedora package, Flathub app or
# mise tool behind the Arch names given. drop prints nothing; todo prints one
# line with an empty name.
omadora_pkg_resolve() {
  local pkg row source names note name

  for pkg in "$@"; do
    # awk splits the row: bash's read would merge empty tab-separated columns.
    row=$(awk -F'\t' -v pkg="$pkg" '!/^#/ && $1 == pkg { print $3 "\x1f" $2 "\x1f" $4; exit }' "$OMADORA_PKG_MAP" 2>/dev/null)
    if [[ -z $row ]]; then
      printf 'fedora\t%s\t\n' "$pkg"
      continue
    fi
    IFS=$'\x1f' read -r source names note <<<"$row"
    case $source in
      drop) ;;
      todo) printf 'todo\t\t%s (%s)\n' "$pkg" "$note" ;;
      *)
        for name in $names; do
          printf '%s\t%s\t%s\n' "$source" "$name" "$note"
        done
        ;;
    esac
  done
}

# True when one resolved package is installed.
omadora_pkg_installed() {
  local source=$1 name=$2

  case $source in
    todo) return 1 ;;
    flatpak) flatpak info --system "$name" &>/dev/null ;;
    mise:*) command -v mise &>/dev/null && mise ls --global "${source#mise:}" 2>/dev/null | grep -q . ;;
    *) rpm -q --quiet "$name" ;;
  esac
}

# The repository section a dnf source needs, or nothing for Fedora's own.
omadora_pkg_repo_section() {
  local source=$1 copr

  case $source in
    copr:*)
      copr=${source#copr:}
      echo "copr:copr.fedorainfracloud.org:${copr%%/*}:${copr#*/}"
      ;;
    ours) echo "copr:copr.fedorainfracloud.org:jersyj:omadora" ;;
    repo:*) echo "${source#repo:}" ;;
  esac
}

# Make sure the repository a dnf source needs is configured, copying an
# on-demand repository file from omadora-repos when it is not.
omadora_pkg_enable_repo() {
  local section file

  section=$(omadora_pkg_repo_section "$1")
  [[ -n $section ]] || return 0
  grep -qxF "[$section]" /etc/yum.repos.d/*.repo 2>/dev/null && return 0

  file=$(grep -lxF "[$section]" "$OMADORA_ON_DEMAND_REPOS"/*.repo 2>/dev/null | head -n 1)
  if [[ -z $file ]]; then
    omadora_pkg_error "Repository '$section' is neither configured nor shipped by omadora-repos"
    return 1
  fi
  echo "Adding repository $section from $(basename "$file")"
  omadora_as_root install -m 0644 "$file" "/etc/yum.repos.d/omadora-$(basename "$file")"
}

omadora_pkg_flathub() {
  omadora_as_root flatpak remote-add --system --if-not-exists flathub "$OMADORA_FLATHUB_URL"
}

# Install every missing package behind the Arch names given.
omadora_pkg_add() {
  local source name note
  local -a dnf_names=() flatpak_ids=() mise_tools=() todo=()
  local -A repos=()

  while IFS=$'\t' read -r source name note; do
    [[ -n $source ]] || continue
    if [[ $source == "todo" ]]; then
      todo+=("$note")
      continue
    fi
    omadora_pkg_installed "$source" "$name" && continue
    case $source in
      flatpak) flatpak_ids+=("$name") ;;
      mise:*) mise_tools+=("${source#mise:}") ;;
      *)
        dnf_names+=("$name")
        repos[$source]=1
        ;;
    esac
  done < <(omadora_pkg_resolve "$@")

  if (( ${#todo[@]} > 0 )); then
    omadora_pkg_error "Not packaged for Omadora yet: ${todo[*]}"
    return 1
  fi

  for source in "${!repos[@]}"; do
    omadora_pkg_enable_repo "$source" || return 1
  done
  if (( ${#dnf_names[@]} > 0 )); then
    omadora_as_root dnf install -y "${dnf_names[@]}" || return 1
  fi
  if (( ${#flatpak_ids[@]} > 0 )); then
    omadora_pkg_flathub || return 1
    omadora_as_root flatpak install --system -y --noninteractive flathub "${flatpak_ids[@]}" || return 1
  fi
  for name in "${mise_tools[@]}"; do
    mise use --global "$name" || return 1
  done

  # pacman can fail without an error; dnf can too (a skipped broken package).
  while IFS=$'\t' read -r source name note; do
    [[ -n $source ]] || continue
    if ! omadora_pkg_installed "$source" "$name"; then
      omadora_pkg_error "Package '$name' did not install"
      return 1
    fi
  done < <(omadora_pkg_resolve "$@")
}

# True when every package behind the Arch names given is installed.
omadora_pkg_present() {
  local source name note

  while IFS=$'\t' read -r source name note; do
    [[ -n $source ]] || continue
    omadora_pkg_installed "$source" "$name" || return 1
  done < <(omadora_pkg_resolve "$@")
}

# Remove whatever is installed of the packages behind the Arch names given.
omadora_pkg_drop() {
  local source name note
  local -a dnf_names=() flatpak_ids=() mise_tools=()

  while IFS=$'\t' read -r source name note; do
    [[ -n $source && $source != "todo" ]] || continue
    omadora_pkg_installed "$source" "$name" || continue
    case $source in
      flatpak) flatpak_ids+=("$name") ;;
      mise:*) mise_tools+=("${source#mise:}") ;;
      *) dnf_names+=("$name") ;;
    esac
  done < <(omadora_pkg_resolve "$@")

  if (( ${#dnf_names[@]} > 0 )); then
    omadora_as_root dnf remove -y "${dnf_names[@]}" || return 1
  fi
  if (( ${#flatpak_ids[@]} > 0 )); then
    omadora_as_root flatpak uninstall --system -y --noninteractive "${flatpak_ids[@]}" || return 1
  fi
  for name in "${mise_tools[@]}"; do
    mise unuse --global "$name" || return 1
  done
}
