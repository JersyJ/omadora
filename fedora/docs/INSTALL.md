# Installing Omadora on a ZBook

How to install Omadora on an HP ZBook 8 G2i 14" (`HARDWARE.md`). The install wipes the disk. It needs two USB sticks, network (Ethernet or Wi-Fi the installer can join) and about 30 minutes.

## 1. Firmware settings

In the BIOS setup (F10 at power-on):

1. Update the BIOS first if HP has a newer one: with HP's Windows tools while the preloaded Windows is still there, or from the BIOS setup's own network update. After the install, `omarchy-update-firmware` (fwupd) installs whatever firmware HP publishes to LVFS.
2. **Secure Boot: on**, in User Mode. The company requires it (`INTUNE.md`).
3. **"Enable MS UEFI CA key": on.** Fedora's bootloader (shim) is signed by Microsoft's third-party UEFI CA; with this setting off the USB stick and the installed system do not boot with Secure Boot on.
4. Intel AMT: off (recommended by the company guide, not checked by Intune).
5. Leave TPM on.

## 2. Installer stick

1. Download the Fedora Everything netinst ISO for the release in `upstream.lock` (`FEDORA_RELEASE`) from https://fedoraproject.org/misc#everything, with its `CHECKSUM` file. Verify it: `gpg --verify` the CHECKSUM against Fedora's key (https://fedoraproject.org/security), then `sha256sum -c`.
2. Write it to the first stick as-is: `sudo dd if=Fedora-Everything-netinst-x86_64-<release>.iso of=/dev/sdX bs=4M conv=fsync status=progress`, or with Fedora Media Writer.

Do not use Ventoy: its Secure Boot key could not be enrolled on the ZBook, and older Ventoy releases do not boot Fedora 45.

The packages come from the network, so the install is always current: the ISO only starts the installer.

## 3. Kickstart stick

The kickstart answers every installer question and runs Omarchy's setup. Generate it on any machine with this repository:

```bash
fedora/bin/kickstart --user <name> --password-hash "$(openssl passwd -6)" --disk nvme0n1 >ks.cfg
```

- `openssl passwd -6` asks for the user's password. Choose one that meets the company rule (at least 12 characters, a digit, a lowercase and an uppercase letter): the kickstart sets it from the hash, which skips the check `passwd` enforces later.
- Leave out `--luks-passphrase`: the installer then asks for the disk passphrase on the laptop, and it is never written to a file.
- `--timezone` (default Europe/Prague), `--keyboard` (default us) and `--lang` (default en_US.UTF-8) change the locale.

Format the second stick as FAT with the label `OEMDRV` (e.g. `sudo mkfs.fat -n OEMDRV /dev/sdY1`) and copy `ks.cfg` to its root. The installer loads a `ks.cfg` from a volume labeled `OEMDRV` without any boot option. The file holds the password hash: wipe the stick afterwards.

Rehearsed on 2026-10-13 in a VM with the kickstart on a USB stick labeled `OEMDRV`: the installer found it, asked for the passphrase twice, installed, and the result booted with Secure Boot to SDDM with no failed units or SELinux denials.

## 4. Install

1. Plug in both sticks, power on, press F9 for the boot menu and pick the installer stick (the UEFI entry).
2. Pick "Install Fedora" at the boot menu. The installer finds the kickstart, asks for the disk passphrase twice, then runs unattended: it partitions (EFI and `/boot` plain, everything else btrfs on LUKS2), installs Fedora and Omadora's packages from the network, runs Omarchy's system and user setup, and reboots.
3. Remove both sticks when it reboots.

If the installer stops with an error, the reason is on screen (switch consoles with Alt+Tab in the text installer); `/tmp/anaconda.log` and `/mnt/sysroot/var/log/omadora-kickstart.log` have the details.

## 5. First boot

1. Type the disk passphrase at the Omarchy boot screen.
2. SDDM shows the password field for the user the kickstart created: log in with the password. This also unlocks the login keyring that Intune uses.
3. Check the install:

```bash
systemctl --failed                 # nothing
sudo ausearch -m avc -ts boot      # no denials
mokutil --sb-state                 # SecureBoot enabled
omarchy version                    # the Omadora version
```

4. Run `omarchy update` once, then go through the hardware checks below, then enroll in Intune (`INTUNE.md`, "How enrollment works").

## 6. Hardware checks (first ZBook)

The virtual machine tests cover everything but the hardware. On the first ZBook, check each item and record the result in `HARDWARE.md` (what failed, with `journalctl -b -p warning` lines).

- [ ] Wi-Fi 7 (BE211): joins the office and home networks; `iw dev` shows the link, and a large download keeps a normal speed. Upstream disables Wi-Fi 7 on the BE200/BE211 PCI cards for a broken data path; this card's CNVi ID (`8086:e340`) is not in that list. If the rate collapses, add `options iwlwifi disable_11be=Y` to `/etc/modprobe.d/iwlwifi-disable-eht.conf`
- [ ] Bluetooth: pair a headset; audio plays through it
- [ ] Speakers, headphone jack and both microphones (`wpctl status`; record a few seconds and play back)
- [ ] Camera: the HP 5MP camera shows a picture (e.g. a video call in Edge)
- [ ] Fingerprint: Omarchy menu, Setup, Security, Fingerprint; enroll a finger, then check it unlocks the lock screen and answers `sudo`
- [ ] Keys: brightness, volume, mute and microphone mute show their on-screen indicators
- [ ] Suspend: close the lid, wait a minute, open it; the lock screen is back and takes the password. Same from the menu (System, Suspend)
- [ ] Lock: Super+Ctrl+L locks; leaving the laptop idle locks it after 5 minutes
- [ ] External display over USB-C or Thunderbolt, and a dock if the company uses one
- [ ] Power: `omarchy-powerprofiles-list` shows the profiles, `omarchy-powerprofiles-set battery power-saver` switches, and `cat /sys/firmware/acpi/platform_profile` follows; the battery shows in the bar
- [ ] FRED: `grep -o fred=on /proc/cmdline` prints `fred=on` (Panther Lake)
- [ ] Firmware: `omarchy-update-firmware` lists the ZBook's devices and updates what LVFS has
- [ ] Touchpad: tap to click, two-finger scroll

## Login screen size

The login screen picks its own scale (Hyprland's automatic choice: 1.5 on the ZBook's 14" 1920x1200 panel), separate from the desktop's (Omarchy menu, Setup, Monitor scaling, saved in `~/.config/hypr/monitors.lua`). To give the login screen the desktop's scale, write it to `/etc/omadora/greeter-scale`; it applies from the next time the login screen starts:

```bash
sudo mkdir -p /etc/omadora && echo 1.25 | sudo tee /etc/omadora/greeter-scale
```

Remove the file to go back to the automatic scale.

## Changing passwords later

- User password: Omarchy menu, Update, Password, User (runs `passwd`). The login keyring's password follows it, so Intune keeps its tokens.
- Disk passphrase: Omarchy menu, Update, Password, Drive Encryption.
