# Hardware: HP ZBook 8 G2i 14"

This is the only supported laptop.

- **Probe:** 2026-10-12, from an EndeavourOS live USB (kernel 6.19, Secure Boot off). Report: [`probes/C75Z7AV.txt`](probes/C75Z7AV.txt).
- **First Omadora install:** 2026-10-14, Fedora 45 with kernel 7.2.10, Secure Boot on.
- Other data comes from HP QuickSpecs and the Ubuntu certification.

## Unit

| Item | Found | On Fedora |
| --- | --- | --- |
| Model | SKU C75Z7AV, board 8ED9, BIOS Y70 01.01.07 (2026-07-07) | |
| CPU | Intel Core Ultra 7 366H (Panther Lake) | The `fred` CPU flag needs `fred=on`. Upstream's `intel/fred.sh` adds it with `grubby` |
| GPU | Intel Panther Lake (`8086:b0a0`, `xe`), eDP 1920x1200 | No NVIDIA. The company buys only SKUs without the RTX PRO 500, so the port has no NVIDIA support |
| Camera | HP 5MP Camera, USB UVC (Chicony `04f2:b882`), IR sensor | Plain UVC. No IPU7 stack is necessary. The IR sensor (face login) is not used |
| Fingerprint | Elan `04f3:0c9f`, match-on-chip | libfprint `elanmoc`; `fprintd` and `fprintd-pam` through authselect. The sensor keeps approximately 10 prints |
| Wi-Fi | Intel Wi-Fi 7 BE211 (CNVi `8086:e340`, `iwlwifi` with `iwlmld`) | Needs `iwlwifi-mld-firmware` and `NetworkManager-wifi` |
| Bluetooth | Intel, over PCIe (`btintel_pcie`, `8086:e376`) | Needs `iwlbluetooth-firmware` |
| Ethernet | Intel I219-LM (`e1000e`) | Works |
| Audio | Intel SOF (`sof-audio-pci-intel-ptl`), HDA codec, 2 digital microphones | Needs `alsa-sof-firmware` |
| NPU | Panther Lake NPU (`intel_vpu`) | Not used by the desktop |
| Input | Synaptics I2C touchpad (`SYNA3165`), HP WMI hotkeys, Intel HID | Works |
| Thunderbolt | 2 Thunderbolt 4 controllers, security level `user`, IOMMU protection on | `bolt` authorizes devices. To approve a dock: `boltctl enroll --policy auto <uuid>` |
| Power | 77 Wh battery; platform profiles low-power, balanced, performance | `power-profiles-daemon` with `intel_pstate` and `platform_profile` |
| Security | TPM 2.0, UEFI, Intel AMT (CSME) | Secure Boot on. Set AMT to off (`INSTALL.md`) |
| Storage | WD PC SN5000S 512 GB NVMe | The kickstart erases the disk. No dual boot |

## First install results (2026-10-14)

| Check | Result |
| --- | --- |
| Boot, Secure Boot, disk encryption | Works. 0 failed units, 0 SELinux denials |
| Wi-Fi | Works. 5 GHz, 160 MHz, Wi-Fi 6, 2.4 Gbit/s receive rate. Wi-Fi 7 not tested (no Wi-Fi 7 router) |
| Bluetooth | Works. Headset audio plays |
| Suspend (lid) and lock screen | Works. The lock screen shows after resume |
| Fingerprint | Works for the lock screen and `sudo` |
| Power profiles | Works. The firmware profile follows the selected profile |
| FRED | `fred=on` is set |
| Firmware (LVFS) | No updates on 2026-10-14 |
| Camera | Works. The HP 5MP camera shows a picture |
| External display | Works |

### Defects found on the real laptop

The VM tests did not find these defects. All are corrected in the packages.

| Defect | Cause | Correction |
| --- | --- | --- |
| Boot screen (Plymouth) crashes | Fedora puts Plymouth's text renderers in a separate package | `omarchy-settings` requires `plymouth-plugin-label` |
| No Wi-Fi and no Bluetooth | Fedora puts the Intel firmware in separate packages | `omarchy` requires `iwlwifi-mld-firmware` and `iwlbluetooth-firmware` |
| Suspend fails | The Bluetooth chip without firmware stops suspend | The Bluetooth firmware (row above) |
| Wi-Fi card not managed | Fedora puts NetworkManager's Wi-Fi plugin in a separate package | `omarchy` requires `NetworkManager-wifi` |
| `thermald` stops at some boots | It starts before the RAPL and coretemp drivers | A drop-in waits up to 15 seconds for the sensors |
| File preview (Space in Nautilus) fails | Fedora's `sushi` does not require `gjs` | `omarchy` requires `gjs` with `sushi` |
| FUSE mount of gvfs stays off after resume | systemd stops the sleep hook's background job | `omadora-gvfs-resume.service` restores the mount |

### Known messages

These messages are not defects. Do not correct them in Omadora.

- `spd5118 ... failed to resume`: the memory temperature sensor after resume (kernel and BIOS).
- `Bluetooth: hci0: Received gp1 mailbox interrupt`, `Malformed DDC record`: Intel Bluetooth firmware.
- `xe ... GSC proxy component not bound`: the driver binds 4 seconds later.
- `Couldn't write 'bbr'` and `'fq'`: the modules load later and the values apply.
- Hyprland `SIGSEGV` in `aquamarine` at exit: occurs when Hyprland stops (login screen exit, shutdown). Hyprland stack from nett00n's COPR.
- `hp_bioscfg`, `hp-wmi ... fan settings`, `virt/tdx`: BIOS and kernel information.

## USB boot

- Fedora's stick and the installed system boot with Secure Boot through shim. Set **Enable MS UEFI CA key** to on.
- Set **Fast Boot** to off, or the F9 menu shows no USB stick.
- Do not use Ventoy. Its Secure Boot key does not enroll on this laptop.

## Probe again

1. Boot a Linux live USB on the laptop.
2. Run `fedora/bin/probe-hardware --sudo <file>`. The probe is read-only. It records no serial numbers and masks MAC addresses.
3. Commit the result as `fedora/docs/probes/<sku>.txt`.

## Upstream hardware scripts

`install/hardware/all.sh` runs 38 scripts. For this laptop:

| Kept | Change on Fedora |
| --- | --- |
| `intel/video-acceleration.sh`, `intel/thermald.sh`, `intel/lpmd.sh`, `intel/sof-firmware.sh` | Package names through `packages/map.tsv` |
| `intel/fix-wifi7-eht.sh` | None (modprobe option) |
| `intel/fred.sh` | `grubby --update-kernel=ALL --args=fred=on` replaces the Limine drop-in |
| `vulkan.sh`, `bluetooth.sh`, `network.sh`, `set-wireless-regdom.sh` | Package names |

A Fedora override of `install/hardware/all.sh` removes all other scripts: NVIDIA, Apple, ASUS, Dell, Surface, Framework, Lenovo, Tuxedo, Broadcom, Elgato, yt6801 and speaker tuning for other models.
