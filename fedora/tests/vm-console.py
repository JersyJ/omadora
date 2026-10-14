#!/usr/bin/env python3
"""Run shell commands on the VM that fedora/tests/vm-install.sh installed.

Boots the installed disk (fedora/.build/vm) with its serial console on a Unix
socket, logs in on that console as the test user, runs each command given and
prints its output, then powers the VM off. For debugging an install without
reinstalling.

Usage: fedora/tests/vm-console.py [--root] [--screenshot] [--sddm-login] 'command' ['command' ...]
  --root        run the commands through sudo
  --screenshot  save the screen to <vm dir>/console-screen.png afterwards
  --sddm-login  first log in at SDDM as a person would, typing the password on
                the VM's keyboard (a --test-password-login install, which
                reports the greeter and the session on the serial console)

A command starting with @ acts on the VM's screen and keyboard instead:
  @type TEXT    type TEXT and Enter
  @key COMBO    press one QEMU key combination, e.g. @key meta_l-ctrl-l
  @sleep N      wait N seconds
  @shot NAME    save the screen to <vm dir>/NAME.png
  @monitor CMD  send CMD to the QEMU monitor, e.g. @monitor system_wakeup

  OMADORA_VM_SB_VARS=<file>  boot with Secure Boot on, using these OVMF variables
                             (Microsoft's keys enrolled; a copy is used)
  OMADORA_VM_COMMAND_TIMEOUT=<seconds>  time each command may take (default 300)
  OMADORA_VM_DIR=<dir>       the VM to boot (default fedora/.build/vm)
  OMADORA_VM_PASSWORD=<text> the test user's password (default omadora-test)
  OMADORA_VM_LUKS=<text>     answer the disk's LUKS prompt on the serial console
                             with this passphrase
"""
import os
import re
import socket
import subprocess
import sys
import time

WORK = os.environ.get("OMADORA_VM_DIR") or os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".build", "vm")
USER = "omatest"
PASSWORD = os.environ.get("OMADORA_VM_PASSWORD", "omadora-test")
LUKS = os.environ.get("OMADORA_VM_LUKS")
SOCK = os.path.join(WORK, "console.sock")
MONITOR = os.path.join(WORK, "console-monitor.sock")


def monitor(command):
    conn = socket.socket(socket.AF_UNIX)
    conn.connect(MONITOR)
    time.sleep(0.3)
    conn.sendall((command + "\n").encode())
    time.sleep(1.5)
    conn.close()


# QEMU sendkey names for the characters a test password may hold (US layout).
KEYS = {"-": "minus", "_": "shift-minus", ".": "dot", "!": "shift-1", "@": "shift-2", " ": "spc"}


def type_text(text):
    """Type text and Enter on the VM's keyboard, as a person at the laptop would."""
    keys = []
    for char in text:
        if char.isascii() and (char.islower() or char.isdigit()):
            keys.append(char)
        elif char.isascii() and char.isupper():
            keys.append("shift-" + char.lower())
        else:
            keys.append(KEYS[char])
    conn = socket.socket(socket.AF_UNIX)
    conn.connect(MONITOR)
    for key in keys + ["ret"]:
        conn.sendall(f"sendkey {key}\n".encode())
        time.sleep(0.15)
    time.sleep(0.5)
    conn.close()


TRANSCRIPT = open(os.path.join(WORK, "console.log"), "ab")


def clean(text):
    """Drop terminal control sequences (CSI and OSC) and carriage returns."""
    text = re.sub(r"\x1b\][^\x07\x1b]*(\x07|\x1b\\)", "", text)
    text = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)
    return text.replace("\r", "")


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
        text = clean(data.decode(errors="replace"))
        for pattern in patterns:
            if re.search(pattern, text):
                return text
    return clean(data.decode(errors="replace"))


def main():
    args = sys.argv[1:]
    root = screenshot = sddm_login = False
    while args and args[0] in ("--root", "--screenshot", "--sddm-login"):
        if args[0] == "--root":
            root = True
        elif args[0] == "--screenshot":
            screenshot = True
        else:
            sddm_login = True
        args = args[1:]
    if not args:
        sys.exit(__doc__)

    if os.path.exists(SOCK):
        os.unlink(SOCK)
    firmware = ["-machine", "q35",
                "-drive", "if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd",
                "-drive", f"if=pflash,format=raw,file={WORK}/vars.fd"]
    sb_vars = os.environ.get("OMADORA_VM_SB_VARS")
    if sb_vars:
        subprocess.run(["cp", sb_vars, f"{WORK}/vars-secboot.fd"], check=True)
        firmware = ["-machine", "q35,smm=on", "-global", "driver=cfi.pflash01,property=secure,value=on",
                    "-drive", "if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.secboot.4m.fd",
                    "-drive", f"if=pflash,format=raw,file={WORK}/vars-secboot.fd"]
    qemu = subprocess.Popen([
        "qemu-system-x86_64", "-enable-kvm", "-cpu", "host", "-smp", "4", "-m", "6144", *firmware,
        "-drive", f"file={WORK}/disk.qcow2,if=virtio,format=qcow2",
        "-netdev", "user,id=net0", "-device", "virtio-net-pci,netdev=net0",
        "-device", "virtio-vga", "-display", "none",
        "-serial", f"unix:{SOCK},server,nowait",
        "-monitor", f"unix:{MONITOR},server,nowait",
    ])
    try:
        for _ in range(100):
            if os.path.exists(SOCK):
                break
            time.sleep(0.2)
        conn = socket.socket(socket.AF_UNIX)
        conn.connect(SOCK)

        if LUKS:
            # The disk's passphrase prompt (plymouth also shows it here when
            # the kernel's console list includes the serial port).
            text = read_until(conn, [r"[Pp]assphrase.*: *$"], 180)
            if not re.search(r"[Pp]assphrase", text):
                sys.exit("no LUKS passphrase prompt on the serial console within 3 minutes")
            conn.sendall(LUKS.encode() + b"\r")

        if sddm_login:
            if "=== OMADORA GREETER" not in read_until(conn, [r"=== OMADORA GREETER"], 300):
                sys.exit("SDDM's greeter did not start within 5 minutes")
            # The greeter process starts before its QML has the password field.
            for attempt in range(3):
                time.sleep(15)
                type_text(PASSWORD)
                if "=== OMADORA SESSION" in read_until(conn, [r"=== OMADORA SESSION"], 60):
                    break
            else:
                sys.exit("no session after typing the password at SDDM three times")
            print("Logged in at SDDM.")
            # Let the desktop start before the serial login below.
            time.sleep(60)

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
            if command.startswith("@"):
                action, _, value = command[1:].partition(" ")
                if action == "type":
                    type_text(value)
                elif action == "key":
                    monitor(f"sendkey {value}")
                elif action == "monitor":
                    monitor(value)
                elif action == "sleep":
                    time.sleep(float(value))
                elif action == "shot":
                    ppm = os.path.join(WORK, value + ".ppm")
                    monitor(f"screendump {ppm}")
                    subprocess.run(["magick", ppm, os.path.join(WORK, value + ".png")], check=False)
                    os.unlink(ppm)
                else:
                    sys.exit(f"unknown action {command}")
                print(f"@ {command[1:]}")
                print()
                continue
            line = command
            if root:
                line = f"echo {PASSWORD} | sudo -S -p '' bash -c {shlex_quote(command)}"
            # Quoted apart so the echoed command line never contains the marker.
            conn.sendall(line.encode() + b"; echo __DO''NE__\r")
            out = read_until(conn, [r"__DONE__\s*OMADORA\$ *$"], int(os.environ.get("OMADORA_VM_COMMAND_TIMEOUT", "300")))
            out = out.rsplit("__DONE__", 1)[0]
            print(f"{'#' if root else '$'} {command}")
            print(out.strip())
            print()
        if screenshot:
            ppm = os.path.join(WORK, "console-screen.ppm")
            monitor(f"screendump {ppm}")
            subprocess.run(["magick", ppm, os.path.join(WORK, "console-screen.png")], check=False)
            print(f"Screenshot: {os.path.join(WORK, 'console-screen.png')}")
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
