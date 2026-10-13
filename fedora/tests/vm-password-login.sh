#!/bin/bash

# Log in to a --test-password-login VM as a person would and check the login
# keyring follows the password: the disk passphrase on the console, the
# password typed at SDDM, the login keyring unlocked; then `passwd` in that
# session, a reboot, the new password at SDDM, and the keyring unlocked again.
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

info "Rebooting and logging in at SDDM with the new password"
OMADORA_VM_PASSWORD=$new_password "${console[@]}" --sddm-login \
  "sudo -S -p '' /usr/local/sbin/omadora-selftest <<<'$new_password'" | tee login2.log
grep -q -- "--- login keyring locked: b false" login2.log || die "the login keyring is not unlocked with the new password: passwd did not change the keyring's password"

info "Keyring: unlocked at the SDDM login, and again with the new password after passwd"
