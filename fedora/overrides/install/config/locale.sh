# Fedora fork: Fedora has no locale-gen; a locale is available once its glibc
# langpack is installed. Same rule as upstream: repair only an unset LANG or
# the bare C/POSIX, and leave any named locale alone. Anaconda normally sets
# LANG from the kickstart, so this rarely does anything.
locale_conf=/etc/locale.conf
if (( EUID != 0 )); then
  locale_conf=${OMARCHY_LOCALE_CONF:-$locale_conf}
fi

current=$(sed -n 's/^LANG=//p' "$locale_conf" 2>/dev/null | tail -1 | tr -d '"') || current=""

case ${current:-C} in
  C | POSIX) ;;
  *)
    echo "Leaving the locale as $current"
    return 0 2>/dev/null || exit 0
    ;;
esac

echo "Setting up locale (en_US.UTF-8)..."

if ! locale -a 2>/dev/null | grep -qi "en_US.utf-\?8"; then
  dnf install -y glibc-langpack-en >/dev/null
fi

if grep -q '^LANG=' "$locale_conf" 2>/dev/null; then
  sed -i 's/^LANG=.*/LANG=en_US.UTF-8/' "$locale_conf"
else
  echo "LANG=en_US.UTF-8" >>"$locale_conf"
fi

export LANG=en_US.UTF-8

echo "Locale set to en_US.UTF-8"
