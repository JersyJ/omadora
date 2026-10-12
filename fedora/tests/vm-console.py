#!/usr/bin/env python3
"""Run shell commands on the VM that fedora/tests/vm-install.sh installed.

Boots the installed disk (fedora/.build/vm) with its serial console on a Unix
socket, logs in on that console as the test user, runs each command given and
prints its output, then powers the VM off. For debugging an install without
reinstalling.

Usage: fedora/tests/vm-console.py [--root] 'command' ['command' ...]
  --root  run the commands through sudo
"""
import os
import re
import socket
import subprocess
import sys
import time

WORK = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".build", "vm")
USER, PASSWORD = "omatest", "omadora-test"
SOCK = os.path.join(WORK, "console.sock")


TRANSCRIPT = open(os.path.join(WORK, "console.log"), "ab")


def read_until(conn, patterns, timeout):
    data = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        conn.settimeout(max(0.1, deadline - time.time()))
        try:
            chunk = conn.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        TRANSCRIPT.write(chunk)
        TRANSCRIPT.flush()
        data += chunk
        text = data.decode(errors="replace")
        for pattern in patterns:
            if re.search(pattern, text):
                return text
    return data.decode(errors="replace")


def main():
    args = sys.argv[1:]
    root = False
    if args and args[0] == "--root":
        root, args = True, args[1:]
    if not args:
        sys.exit(__doc__)

    if os.path.exists(SOCK):
        os.unlink(SOCK)
    qemu = subprocess.Popen([
        "qemu-system-x86_64", "-enable-kvm", "-machine", "q35", "-cpu", "host", "-smp", "4", "-m", "6144",
        "-drive", "if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd",
        "-drive", f"if=pflash,format=raw,file={WORK}/vars.fd",
        "-drive", f"file={WORK}/disk.qcow2,if=virtio,format=qcow2",
        "-netdev", "user,id=net0", "-device", "virtio-net-pci,netdev=net0",
        "-device", "virtio-vga", "-display", "none",
        "-serial", f"unix:{SOCK},server,nowait",
    ])
    try:
        for _ in range(100):
            if os.path.exists(SOCK):
                break
            time.sleep(0.2)
        conn = socket.socket(socket.AF_UNIX)
        conn.connect(SOCK)

        # Wait for the serial getty, then log in.
        for _ in range(30):
            conn.sendall(b"\r")
            if re.search(r"login: *$", read_until(conn, [r"login: *$"], 10)):
                break
        conn.sendall(USER.encode() + b"\r")
        read_until(conn, [r"Password: *$"], 15)
        conn.sendall(PASSWORD.encode() + b"\r")
        read_until(conn, [r"[$>] *$"], 30)
        # Omarchy's prompt (starship) rewrites PS1, so continue in a plain shell.
        conn.sendall(b"stty -echo cols 250; exec env PS1='OMADORA$ ' bash --norc --noprofile\r")
        read_until(conn, [r"OMADORA\$ *$"], 10)

        for command in args:
            line = command
            if root:
                line = f"echo {PASSWORD} | sudo -S -p '' bash -c {shlex_quote(command)}"
            conn.sendall(line.encode() + b"; echo __DONE__\r")
            out = read_until(conn, [r"__DONE__\s*OMADORA\$ *$"], 300)
            out = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", out).replace("\r", "")
            out = out.rsplit("__DONE__", 1)[0]
            print(f"{'#' if root else '$'} {command}")
            print(out.strip())
            print()
        conn.sendall(b"echo " + PASSWORD.encode() + b" | sudo -S -p '' systemctl poweroff\r")
        time.sleep(5)
    finally:
        try:
            qemu.wait(timeout=60)
        except subprocess.TimeoutExpired:
            qemu.kill()


def shlex_quote(text):
    return "'" + text.replace("'", "'\"'\"'") + "'"


if __name__ == "__main__":
    main()
