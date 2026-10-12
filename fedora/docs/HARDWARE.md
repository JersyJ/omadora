# Hardware: HP ZBook 8 G2i 14"

The only supported laptop. Facts below come from public listings (HP QuickSpecs, retailers, Ubuntu certification); the probe of a real unit replaces them. The probe is postponed to Phase 2 (decided 2026-10-12): it is needed before the first install on a real ZBook, not before.

## Known so far

| Item | What is known | Fedora impact |
| --- | --- | --- |
| CPU | Intel Core Ultra 3 "Panther Lake" (Ultra 5 335, Ultra 7 356H / 366H); launched March 2026 | Fedora 45 kernel 7.2 supports it; upstream enables FRED (`fred=on`) on Panther Lake, which becomes a `grubby` kernel argument |
| GPU | Intel Xe3 integrated; optional NVIDIA RTX PRO 500 Blackwell (6 GB) | NVIDIA SKU needs RPM Fusion `akmod-nvidia` with the open kernel modules and a MOK enrolled once for Secure Boot |
| Camera | Webcam with shutter and LED; IR face login listed as an option | Unknown whether MIPI (Intel IPU7) or USB. MIPI needs an akmod plus closed-source userspace with no Fedora package |
| Fingerprint | Listed as an option | `fprintd` + `fprintd-pam` through authselect; the sensor vendor decides libfprint support |
| Wi-Fi | Not confirmed | Upstream disables 802.11be on some Intel Wi-Fi 7 cards (`intel/fix-wifi7-eht.sh`) |
| Ports | 2× Thunderbolt 4, HDMI 2.1, USB-C 10 Gbps, USB-A, RJ45 | Thunderbolt authorization via `bolt` |
| Linux | Ubuntu 24.04 certified only on an OEM 6.17 kernel; Ubuntu preinstall offered for the 14" model | Expect fixes to land in recent kernels; F45's 7.2 is newer than the OEM kernel |

## Probe a real unit

Boot a Fedora 45 live USB (or any Linux) on the laptop and run:

```bash
git clone <this repo> && cd omarchy-fedora
fedora/bin/probe-hardware --sudo zbook-8-g2i-14.txt
```

It is read-only and records no serial numbers. Commit the result as `fedora/docs/probes/<sku>.txt`. Check in particular:

- **Camera:** an Intel IPU PCI device plus the ACPI sensor `OVTI08F4` means the MIPI/IPU7 path. ACPI tables often list sensors that are not fitted, so a sensor ID alone proves nothing. A UVC device in `lsusb` means a USB camera.
- **NVIDIA:** whether this SKU has the RTX PRO 500.
- **Wi-Fi:** the exact Intel card (`lspci -nn`), for the Wi-Fi 7 fix.
- **Fingerprint:** the USB vendor and product ID, to check libfprint support.
- **Secure Boot:** confirm it is enabled, which is the configuration we test.

## Upstream hardware scripts

`install/hardware/all.sh` runs 38 scripts. For this laptop:

| Kept | Change on Fedora |
| --- | --- |
| `intel/video-acceleration.sh`, `intel/thermald.sh`, `intel/lpmd.sh`, `intel/sof-firmware.sh` | Package names through `packages/map.tsv` only |
| `intel/fix-wifi7-eht.sh` | None (modprobe option) |
| `intel/fred.sh` | Rewrite: `grubby --update-kernel=ALL --args=fred=on` instead of a Limine drop-in |
| `nvidia.sh` | Rewrite: RPM Fusion akmod, dracut instead of mkinitcpio, MOK enrollment |
| `vulkan.sh`, `bluetooth.sh`, `network.sh`, `set-wireless-regdom.sh` | Package names only |
| `intel/ipu7-camera.sh` | Only if the probe finds the MIPI camera |

Everything else (Apple, ASUS, Dell, Surface, Framework, Lenovo, Tuxedo, Broadcom, Elgato, yt6801, speaker tuning for other models) is left out by a Fedora override of `install/hardware/all.sh`.
