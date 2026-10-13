#!/bin/bash

# Update a test VM installed from an earlier release with `omarchy update`, the
# way a person runs it (the password typed at its sudo prompt), and check the
# result: the omarchy packages moved to the current build, the update finished,
# no failed units, no SELinux denials. Use it on every sync: keep the VM of the
# previous sync and its snapshot.
#
# Needs a VM installed with OMADORA_VM_PASSWORD_LOGIN=1 (fedora/tests/vm-install.sh)
# and, by default, its "tested" snapshot (vm-install's state after the login
# test), which is restored first so the run always starts from the old release.
#
# Usage: fedora/tests/vm-update.sh <workdir> [snapshot]
#   OMADORA_VM_PASSWORD=<text>  the test user's password (default Kestrel-Window-2026,
#                               what the login test leaves)
#   OMADORA_VM_SB_VARS=<file>   boot with Secure Boot on (see vm-console.py)

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

work=$(realpath "${1:?usage: fedora/tests/vm-update.sh <workdir> [snapshot]}")
snapshot=${2:-tested}
password=${OMADORA_VM_PASSWORD:-Kestrel-Window-2026}
export OMADORA_VM_DIR=$work OMADORA_VM_LUKS=omadora-disk OMADORA_VM_PASSWORD=$password

qemu-img snapshot -a "$snapshot" "$work/disk.qcow2" || die "no snapshot '$snapshot' in $work/disk.qcow2"

session='export XDG_RUNTIME_DIR=/run/user/$(id -u) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus; eval "$(systemctl --user show-environment | grep -E "^(WAYLAND_DISPLAY|HYPRLAND_INSTANCE_SIGNATURE|PATH)=" | sed "s/^/export /")"'
# omarchy update revokes sudo's cached password and asks for it once on its own
# terminal: give it one (script) and type the password into it.
update="$session; (sleep 5; printf '%s\\n' '$password') | timeout 3000 script -qefc 'OMARCHY_UPDATE_UNATTENDED=1 omarchy update -y' ~/update.log >/dev/null; echo \"UPDATE exit=\$?\"; sed 's/\\x1b\\[[0-9;?]*[a-zA-Z]//g' ~/update.log | tr -d '\\r' | grep -E 'Running migration|Reboot\\?|Something went wrong|Error|error:' | tail -20"
after="echo \"BEFORE \$(cat ~/before-version)\"; echo \"AFTER \$(rpm -q --qf '%{VERSION}-%{RELEASE}' omarchy)\"; echo \"FAILED_UNITS \$(systemctl --failed --no-legend | wc -l)\"; echo \"AVC \$(printf '%s\\n' '$password' | sudo -S -p '' ausearch -m avc -ts boot 2>/dev/null | grep -c type=AVC)\"; echo \"USER_AVC \$(printf '%s\\n' '$password' | sudo -S -p '' ausearch -m user_avc -ts boot 2>/dev/null | grep -c denied)\""

OMADORA_VM_COMMAND_TIMEOUT=3600 "$FEDORA_DIR/tests/vm-console.py" --sddm-login \
  "rpm -q --qf '%{VERSION}-%{RELEASE}' omarchy >~/before-version; cat ~/before-version" \
  "$update" "$after" | tee "$work/update.log" | grep -aoE '(UPDATE|BEFORE|AFTER|FAILED_UNITS|AVC|USER_AVC) .*|Running migration.*|Linux kernel.*|Something went wrong.*' || true

# Terminal replies can precede a marker on its line, so markers match anywhere.
grep -aq 'UPDATE exit=0' "$work/update.log" || die "omarchy update failed; see $work/update.log"
before=$(grep -aoE 'BEFORE [^ ]+' "$work/update.log" | tail -1 | cut -d' ' -f2)
after=$(grep -aoE 'AFTER [^ ]+' "$work/update.log" | tail -1 | cut -d' ' -f2)
[[ -n $after && $after != "$before" ]] || die "omarchy did not move from $before"
grep -aqE 'FAILED_UNITS 0$' "$work/update.log" || die "units failed after the update; see $work/update.log"
grep -aqE '(^|[^_])AVC 0$' "$work/update.log" || die "SELinux denials after the update; see $work/update.log"
# systemd's own SELinux checks (USER_AVC) can deny a package scriptlet while
# selinux-policy reloads in the same transaction (seen: moby-engine's
# mark-restart against selinux-policy 45.21, "Failed to set unit properties on
# docker.service: Access denied"). That is Fedora's, and transient: report it.
grep -aqE 'USER_AVC 0$' "$work/update.log" || warn "systemd SELinux denials (USER_AVC) during the update; see ausearch -m user_avc in the VM"
info "omarchy update: $before -> $after, no failed units, no SELinux denials"
