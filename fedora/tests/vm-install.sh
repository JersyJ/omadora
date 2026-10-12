#!/bin/bash

# Install Omadora into a throwaway QEMU/KVM virtual machine and report how its
# first boot went.
#
# Installs from the Fedora netinst ISO with a test kickstart (fedora/bin/kickstart
# --test: no disk encryption, SDDM logs the test user in), using UEFI firmware.
# Then boots the installed disk, waits for the self-test the kickstart adds
# (failed units, SDDM, Hyprland and Quickshell processes, SELinux denials,
# install log failures), prints it, and saves a screenshot of the screen.
#
# Needs qemu-system-x86_64, qemu-img, edk2-ovmf, bsdtar, python3, openssl and
# /dev/kvm. Downloads nothing: pass the ISO (verify it against Fedora's signed
# CHECKSUM first). Omadora's packages come from its COPR, so the result tests
# what COPR built from the pushed main branch.
#
# Usage: fedora/tests/vm-install.sh <Fedora-Everything-netinst.iso> [workdir]
#   OMADORA_VM_SECURE_BOOT=1  boot the installed system with Secure Boot on
#                             (needs OVMF_VARS with Microsoft's keys enrolled at
#                             $OMADORA_VM_SB_VARS)

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

iso=$(realpath "${1:?usage: fedora/tests/vm-install.sh <netinst.iso> [workdir]}")
work=$(realpath -m "${2:-$FEDORA_DIR/.build/vm}")
ovmf_code=${OMADORA_VM_OVMF_CODE:-/usr/share/edk2/x64/OVMF_CODE.4m.fd}
ovmf_vars=${OMADORA_VM_OVMF_VARS:-/usr/share/edk2/x64/OVMF_VARS.4m.fd}
user=omatest
password=omadora-test

for tool in qemu-system-x86_64 qemu-img bsdtar python3 openssl; do
  command -v "$tool" >/dev/null || die "$tool is missing"
done
[[ -w /dev/kvm ]] || die "/dev/kvm is not usable"
[[ -f $ovmf_code && -f $ovmf_vars ]] || die "OVMF firmware not found (edk2-ovmf)"

rm -rf "$work"
mkdir -p "$work"
cd "$work"

info "Generating the test kickstart"
"$FEDORA_DIR/bin/kickstart" --user "$user" --password-hash "$(openssl passwd -6 "$password")" \
  --disk vda --reboot --test >omadora.ks

info "Extracting the installer kernel"
bsdtar -xf "$iso" images/pxeboot/vmlinuz images/pxeboot/initrd.img
label=$(dd if="$iso" bs=1 skip=32808 count=32 status=none | tr -d ' ')
[[ -n $label ]] || die "cannot read the ISO's volume label"

port=$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 -m http.server --bind 127.0.0.1 "$port" --directory "$work" >http.log 2>&1 &
http_pid=$!
trap 'kill "$http_pid" 2>/dev/null || true' EXIT

qemu-img create -q -f qcow2 disk.qcow2 40G
cp "$ovmf_vars" vars.fd

# shellcheck disable=SC2054 # QEMU options are comma-separated within one argument
qemu_common=(
  qemu-system-x86_64 -enable-kvm -machine q35 -cpu host -smp 4 -m 6144
  -drive "if=pflash,format=raw,readonly=on,file=$ovmf_code"
  -drive if=pflash,format=raw,file=vars.fd
  -drive file=disk.qcow2,if=virtio,format=qcow2
  -netdev user,id=net0 -device virtio-net-pci,netdev=net0
  -device virtio-vga -display none
)

info "Installing (log: $work/install.log); this downloads and installs about 3 GB"
"${qemu_common[@]}" \
  -cdrom "$iso" -kernel images/pxeboot/vmlinuz -initrd images/pxeboot/initrd.img \
  -append "inst.stage2=hd:LABEL=$label inst.ks=http://10.0.2.2:$port/omadora.ks inst.text inst.notmux console=ttyS0" \
  -serial file:install.log -no-reboot

if ! grep -q "reboot: Restarting system\|reboot: Power down\|Restarting system" install.log; then
  tail -n 40 install.log
  die "the installer stopped without finishing; see $work/install.log"
fi
if grep -q "%post.*failed\|The installation was stopped due to an error" install.log; then
  tail -n 60 install.log
  die "a kickstart %post section failed; see $work/install.log"
fi

if [[ ${OMADORA_VM_SECURE_BOOT:-0} == "1" ]]; then
  info "Switching to Secure Boot firmware"
  cp "${OMADORA_VM_SB_VARS:?set OMADORA_VM_SB_VARS}" vars.fd
  qemu_common=("${qemu_common[@]/$ovmf_code//usr/share/edk2/x64/OVMF_CODE.secboot.4m.fd}")
  # shellcheck disable=SC2054
  qemu_common+=(-global driver=cfi.pflash01,property=secure,value=on)
fi

info "Booting the installed system (log: $work/boot.log)"
"${qemu_common[@]}" -serial file:boot.log -monitor "unix:$work/monitor.sock,server,nowait" &
qemu_pid=$!

monitor() {
  python3 - "$work/monitor.sock" "$1" <<'PY'
import socket, sys, time
s = socket.socket(socket.AF_UNIX)
s.connect(sys.argv[1])
time.sleep(0.3)
s.sendall((sys.argv[2] + "\n").encode())
time.sleep(1)
s.close()
PY
}

for _ in $(seq 1 120); do
  grep -q "=== OMADORA SELFTEST END" boot.log 2>/dev/null && break
  kill -0 "$qemu_pid" 2>/dev/null || die "the VM stopped before the self-test; see $work/boot.log"
  sleep 10
done

monitor "screendump $work/screen.ppm" || true
monitor "quit" || true
wait "$qemu_pid" 2>/dev/null || true

if ! grep -q "=== OMADORA SELFTEST END" boot.log; then
  tail -n 40 boot.log
  die "no self-test report within 20 minutes; see $work/boot.log"
fi

sed -n '/=== OMADORA SELFTEST BEGIN/,/=== OMADORA SELFTEST END/p' boot.log
if command -v magick >/dev/null && [[ -f screen.ppm ]]; then
  magick screen.ppm screen.png && echo "Screenshot: $work/screen.png"
fi
