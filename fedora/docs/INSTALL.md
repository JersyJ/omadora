# Installing Omadora on a ZBook

This procedure installs Omadora on an HP ZBook 8 G2i 14" (`HARDWARE.md`).

> **WARNING:** The install erases the full disk, Windows included.

You need:

- 1 USB stick, 2 GB or larger
- A wired network connection. The installer uses Ethernet with DHCP only. The ZBook has no Ethernet port: use a USB-C adapter or a dock.
- Approximately 30 minutes

## 1. Firmware settings

Press F10 at power-on to open the BIOS setup.

1. If HP has a newer BIOS, install it first. Use HP's Windows tools before the install erases Windows, or the BIOS network update.
2. Set **Secure Boot** to on, in User Mode. The company requires it (`INTUNE.md`).
3. Set **Enable MS UEFI CA key** to on. Microsoft's third-party CA signs Fedora's boot loader (shim). If this setting is off, the stick and the installed system do not boot with Secure Boot.
4. Set **Fast Boot** to off (Advanced, Boot Options). If Fast Boot is on, the F9 menu shows no USB stick.
5. Set **Intel AMT** to off (Advanced, Remote Management Options). The company guide recommends this. Intune does not check it.
6. Keep TPM and HP Sure Start on.

After the install, `omarchy-update-firmware` (fwupd) installs the firmware that HP publishes to LVFS. You can set Fast Boot to on again.

## 2. USB stick

The stick holds the installer and the kickstart. The kickstart answers all installer questions and runs Omarchy's setup. Prepare the stick on a Linux computer with this repository.

1. Download the Fedora Everything netinst ISO and its `CHECKSUM` file from https://fedoraproject.org/misc#everything. Use the release in `upstream.lock` (`FEDORA_RELEASE`).
2. Verify the ISO. Run `gpg --verify` on the CHECKSUM file with Fedora's key (https://fedoraproject.org/security), then `sha256sum -c`.
3. Make the kickstart:

   ```bash
   fedora/bin/kickstart --user <name> --password-hash "$(openssl passwd -6)" --disk nvme0n1 >fedora/.build/ks.cfg
   ```

   - `openssl passwd -6` asks for the user password. Use the company rule: 12 characters or more, with a digit, a lowercase and an uppercase letter. The kickstart does not check the password.
   - Do not use `--luks-passphrase`. The installer then asks for the disk passphrase on the laptop, and no file contains it.
   - To change the locale, use `--timezone` (default Europe/Prague), `--keyboard` (default us) and `--lang` (default en_US.UTF-8).

4. Build the stick image. This step needs `sfdisk`, `cpio` and `uv`.

   ```bash
   fedora/bin/usb-image Fedora-Everything-netinst-x86_64-<release>.iso fedora/.build/ks.cfg fedora/.build/omadora-usb.img
   ```

5. Find the stick device with `lsblk`. If usbguard blocks the stick, run `sudo usbguard allow-device <id>`.
6. Write the image to the stick:

   ```bash
   sudo dd if=fedora/.build/omadora-usb.img of=/dev/sdX bs=4M conv=fsync status=progress
   ```

> **CAUTION:** The image and the stick contain the password hash. After the install, delete the image and erase the stick.

> **NOTE:**
> - `usb-image` puts the kickstart in the ISO's EFI partition as an extra initrd, as Fedora's `mkksiso` does. Shim and GRUB keep Fedora's signatures.
> - The packages come from the network. The ISO only starts the installer, so each install is current.
> - Do not use Ventoy. Its Secure Boot key does not enroll on the ZBook, and old releases do not boot Fedora 45.
> - A kickstart on a second stick with the label `OEMDRV` also works. A kickstart on a partition of the installer stick does not work: the installer locks that stick.
> - The first ZBook was installed with this procedure on 2026-10-14, with Secure Boot on.

## 3. Install

1. Connect the stick and the network cable.
2. Power on and press F9. Select the USB stick (UEFI entry).
3. Select **Install Fedora 45**, or wait 60 seconds. Do not select **Test this media**: that check fails because the stick contains the kickstart.
4. Type the disk passphrase two times.
5. Wait. The installer partitions the disk, installs the packages and runs Omarchy's setup.
   - EFI and `/boot` are not encrypted. All other data is btrfs on LUKS2.
6. At "Installation complete. Press ENTER to quit", press Enter. The laptop reboots.
7. Remove the stick.

If the installer stops, read the error on the screen. Press Alt+Tab to change consoles. For details, see `/tmp/anaconda.log` and `/mnt/sysroot/var/log/omadora-kickstart.log`.

## 4. First boot

1. At the Omarchy boot screen, type the disk passphrase.
2. At the login screen, type the user password. This also unlocks the login keyring that Intune uses.
3. Check the install:

   ```bash
   systemctl --failed                 # 0 units
   sudo ausearch -m avc -ts boot      # <no matches>
   mokutil --sb-state                 # SecureBoot enabled
   omarchy version                    # the Omadora version
   ```

4. Run `omarchy update`.
5. Do the hardware checks (section 5).
6. Enroll in Intune (`INTUNE.md`, "How enrollment works").

## 5. Hardware checks

The VM tests do not test hardware. On each new laptop model, do these checks. Record the results in `HARDWARE.md`. For each failure, record the `journalctl -b -p warning` lines.

- [ ] **Wi-Fi:** connect to a network. `iw dev wlp0s20f3 link` shows the link. A large download keeps its speed.
  - If the speed drops a lot, put `options iwlwifi disable_11be=Y` in `/etc/modprobe.d/iwlwifi-disable-eht.conf`. Upstream does this for BE200/BE211 PCI cards. The ZBook's CNVi card (`8086:e340`) is not on that list.
- [ ] **Bluetooth:** pair a headset. Audio plays through it.
- [ ] **Audio:** speakers, headphone jack and both microphones work (`wpctl status`; record and play back).
- [ ] **Camera:** the HP 5MP camera shows a picture, for example in an Edge video call.
- [ ] **Fingerprint:** Omarchy menu, Setup, Security, Fingerprint. Enroll a finger. The finger unlocks the lock screen and `sudo`.
- [ ] **Keys:** brightness, volume, mute and microphone mute show their indicators.
- [ ] **Suspend:** close the lid for 1 minute, then open it. The lock screen shows and accepts the password. Do the same from the menu (System, Suspend).
- [ ] **Lock:** Super+Ctrl+L locks. After 5 minutes idle, the laptop locks.
- [ ] **External display:** USB-C or Thunderbolt, and the company dock if there is one.
- [ ] **Power:** `powerprofilesctl set power-saver` changes `/sys/firmware/acpi/platform_profile` to `low-power`. The bar shows the battery.
- [ ] **FRED:** `grep -o fred=on /proc/cmdline` prints `fred=on` (Panther Lake).
- [ ] **Firmware:** `omarchy-update-firmware` lists the laptop's devices.
- [ ] **Touchpad:** tap to click and two-finger scroll work.

## Login screen size

The login screen and the desktop have separate scales:

- **Login screen:** Hyprland's automatic scale, 1.5 on the ZBook's 1920x1200 panel.
- **Desktop:** Omarchy menu, Setup, Monitor scaling. Saved in `~/.config/hypr/monitors.lua`.

To give the login screen the desktop scale, write the scale to `/etc/omadora/greeter-scale`:

```bash
sudo mkdir -p /etc/omadora && echo 1.25 | sudo tee /etc/omadora/greeter-scale
```

The new scale shows the next time the login screen starts. To use the automatic scale again, delete the file. If you change the desktop scale, write the file again.

## Passwords

- **User password:** Omarchy menu, Update, Password, User (runs `passwd`). The login keyring password changes with it, so Intune keeps its tokens.
- **Disk passphrase:** Omarchy menu, Update, Password, Drive Encryption.
