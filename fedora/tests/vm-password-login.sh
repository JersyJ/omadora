#!/bin/bash

# Log in to a --test-password-login VM as a person would and check the login
# keyring follows the password: the disk passphrase on the console, the
# password typed at SDDM, the login keyring unlocked; then `passwd` in that
# session, a reboot, the new password at SDDM, and the keyring unlocked again.
# In that second session it locks the screen (Super+Ctrl+L), checks a wrong
# password keeps it locked and the right one unlocks it, then waits for the
# idle lock (5 minutes) and unlocks again.
# fedora/tests/vm-install.sh runs it after an OMADORA_VM_PASSWORD_LOGIN=1
# install; run it again on that VM after reverting it to a snapshot taken
# before the first login (qemu-img snapshot -a).
#
# Usage: fedora/tests/vm-password-login.sh [workdir]
#   OMADORA_VM_SB_VARS=<file>  boot with Secure Boot on (see vm-console.py)

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

work=$(realpath "${1:-$FEDORA_DIR/.build/vm}")
password=omadora-test
luks_passphrase=omadora-disk
new_password=Kestrel-Window-2026
console=("$FEDORA_DIR/tests/vm-console.py")
export OMADORA_VM_DIR=$work OMADORA_VM_LUKS=$luks_passphrase

cd "$work"

info "Booting, unlocking the disk, logging in at SDDM, then changing the password with passwd"
OMADORA_VM_PASSWORD=$password "${console[@]}" --sddm-login --screenshot \
  "sudo -S -p '' /usr/local/sbin/omadora-selftest <<<'$password'" \
  "printf '%s\n' '$password' '$new_password' '$new_password' | passwd" \
  "journalctl -b --no-pager -o short-monotonic | grep gkr-pam" | tee login1.log
grep -q -- "--- login keyring locked: b false" login1.log || die "the login keyring is not unlocked after logging in at SDDM"
grep -q "passwd: .*success\|all authentication tokens updated successfully" login1.log || die "passwd did not change the password"

# Prints "locked-state=0" while the session is locked, 1 when it is not.
lock_state='export XDG_RUNTIME_DIR=/run/user/$(id -u) HYPRLAND_INSTANCE_SIGNATURE=$(ls -t /run/user/$(id -u)/hypr | head -1); omarchy-hyprland-session-locked; echo "locked-state=$?"'

info "Rebooting, logging in at SDDM with the new password, then locking and unlocking the screen"
OMADORA_VM_COMMAND_TIMEOUT=600 OMADORA_VM_PASSWORD=$new_password "${console[@]}" --sddm-login \
  "sudo -S -p '' /usr/local/sbin/omadora-selftest <<<'$new_password'" \
  "@key meta_l-ctrl-l" "@sleep 6" "@shot lock-1-locked" "$lock_state" \
  "@key shift" "@sleep 2" "@type Wrong-Password-1" "@sleep 6" "@shot lock-2-wrong" "$lock_state" \
  "@key shift" "@sleep 2" "@type $new_password" "@sleep 6" "@shot lock-3-unlocked" "$lock_state" \
  "@sleep 340" "@shot lock-4-idle" "$lock_state" \
  "@key shift" "@sleep 2" "@type $new_password" "@sleep 6" "@shot lock-5-unlocked" "$lock_state" \
  "sudo -S -p '' ausearch -m avc -ts boot <<<'$new_password' 2>&1 | grep -c type=AVC" | tee login2.log
grep -q -- "--- login keyring locked: b false" login2.log || die "the login keyring is not unlocked with the new password: passwd did not change the keyring's password"
states=$(grep -o 'locked-state=[0-9]' login2.log | cut -d= -f2 | tr -d '\n')
# Locked, still locked after the wrong password, unlocked, locked when idle, unlocked.
[[ $states == "00101" ]] || die "lock screen states were $states, expected 00101 (screenshots: $work/lock-*.png)"

info "Keyring: unlocked at the SDDM login, and again with the new password after passwd"
info "Lock screen: locks on Super+Ctrl+L and when idle, refuses a wrong password, unlocks with the right one"
