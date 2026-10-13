# Fedora fork: Fedora's snapper reads its configuration list from
# /etc/sysconfig/snapper (Arch: /etc/conf.d/snapper). Boot entries for
# snapshots come from grub-btrfs instead of limine-snapper-sync: its section
# goes into grub.cfg once, then grub-btrfsd keeps grub-btrfs.cfg current.
SNAPPER_CONFIG_PATH="${OMARCHY_SNAPPER_CONFIG_PATH:-/etc/snapper/configs/root}"
SNAPPER_CONF_PATH="${OMARCHY_SNAPPER_CONF_PATH:-/etc/sysconfig/snapper}"
template="${OMARCHY_SNAPPER_TEMPLATE:-${OMARCHY_PATH:-/usr/share/omarchy}/default/snapper/root}"

echo "Configuring Omarchy Snapper snapshot retention"

if [[ ! -f $SNAPPER_CONFIG_PATH ]]; then
  mkdir -p "$(dirname "$SNAPPER_CONFIG_PATH")"

  if [[ ${OMARCHY_SNAPPER_CONFIGURE_TEST:-0} == "1" ]]; then
    : >"$SNAPPER_CONFIG_PATH"
  else
    snapper --no-dbus -c root create-config / >/dev/null 2>&1 || snapper -c root create-config / >/dev/null
  fi
fi

install -m 0644 "$template" "$SNAPPER_CONFIG_PATH"
# Every dnf transaction leaves a pre/post pair (libdnf5 actions, including the
# daily security updates), so keep ten numbered snapshots instead of five.
sed -i 's/^NUMBER_LIMIT=.*/NUMBER_LIMIT="10"/' "$SNAPPER_CONFIG_PATH"

mkdir -p "$(dirname "$SNAPPER_CONF_PATH")"
if [[ -f $SNAPPER_CONF_PATH ]] && grep -q '^SNAPPER_CONFIGS=' "$SNAPPER_CONF_PATH"; then
  sed -i 's/^SNAPPER_CONFIGS=.*/SNAPPER_CONFIGS="root"/' "$SNAPPER_CONF_PATH"
else
  printf '%s\n' 'SNAPPER_CONFIGS="root"' >>"$SNAPPER_CONF_PATH"
fi
chmod 0644 "$SNAPPER_CONF_PATH"

systemctl disable --now snapper-timeline.timer >/dev/null 2>&1 || true
systemctl enable --now snapper-cleanup.timer >/dev/null 2>&1 || true

if [[ ${OMARCHY_SNAPPER_CONFIGURE_TEST:-0} != "1" && -x /etc/grub.d/41_snapshots-btrfs ]]; then
  grub2-mkconfig -o /boot/grub2/grub.cfg >/dev/null 2>&1 || echo "Could not add the snapshot entries to the GRUB menu" >&2
fi
