"""Edit the EFI partition image of a Fedora netinst ISO for fedora/bin/usb-image.

Adds the kickstart initrd as /EFI/BOOT/omadora-ks.img, makes GRUB load it with
every install entry (inst.ks=file:/ks.cfg) and makes "Install" the default
entry instead of "Test this media", whose checksum no longer matches the
changed stick. The signed boot files (shim, GRUB) are not touched.

Usage: python3 usb-image-esp.py <esp.img> <ks-initrd.img>
"""

import re
import sys

import fs

KS_IMG = "/EFI/BOOT/omadora-ks.img"
CONFIGS = ("/EFI/BOOT/GRUB.CFG", "/EFI/BOOT/BOOT.conf")


def edit_config(text):
    if 'set default="1"' not in text:
        sys.exit("unexpected GRUB config: no 'set default=\"1\"' (a new ISO layout?)")
    text = text.replace('set default="1"', 'set default="0"', 1)
    # $cmdpath is empty in Fedora's GRUB on a USB stick: find the partition by
    # the file instead, so it works whatever disk number the stick gets.
    anchor = "search --no-floppy --set=root -l "
    if text.count(anchor) != 1:
        sys.exit("unexpected GRUB config: no single 'search ... -l <label>' line")
    end = text.index("\n", text.index(anchor)) + 1
    text = text[:end] + f"search --no-floppy --set=ksdev --file {KS_IMG}\n" + text[end:]
    out, entries, pending = [], 0, False
    for line in text.splitlines(keepends=True):
        if re.match(r"\s*linux\s", line) and "inst.rescue" not in line:
            line = re.sub(r"(inst\.stage2=\S+)", r"\1 inst.ks=file:/ks.cfg", line)
            pending = True
        elif re.match(r"\s*initrd\s", line) and pending:
            line = line.rstrip("\n") + f" ($ksdev){KS_IMG}\n"
            pending = False
            entries += 1
        out.append(line)
    if entries != 3:
        sys.exit(f"unexpected GRUB config: {entries} install entries, expected 3")
    return "".join(out)


def main():
    esp, ks_img = sys.argv[1:3]
    payload = open(ks_img, "rb").read()
    with fs.open_fs(f"fat://{esp}") as fat:
        fat.writebytes(KS_IMG, payload)
        for cfg in CONFIGS:
            fat.writetext(cfg, edit_config(fat.readtext(cfg)))
    with fs.open_fs(f"fat://{esp}") as fat:
        if fat.readbytes(KS_IMG) != payload:
            sys.exit("the kickstart initrd did not read back intact")
        for cfg in CONFIGS:
            if "inst.ks=file:/ks.cfg" not in fat.readtext(cfg):
                sys.exit(f"{cfg} did not read back with the kickstart entries")


if __name__ == "__main__":
    main()
