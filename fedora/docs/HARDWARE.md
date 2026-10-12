# Hardware: HP ZBook 8 G2i 14"

The only supported laptop. A real unit was probed on 2026-10-12 (report: [`probes/C75Z7AV.txt`](probes/C75Z7AV.txt), from an EndeavourOS live USB with kernel 6.19, Secure Boot temporarily off). Facts not covered by the probe come from public listings (HP QuickSpecs, Ubuntu certification).

## Probed unit

| Item | Found | Fedora impact |
| --- | --- | --- |
| Model | HP ZBook 8 G2i 14", SKU C75Z7AV, board 8ED9, BIOS Y70 01.01.07 (2026-07-07) | |
| CPU | Intel Core Ultra 7 366H (Panther Lake) | Kernel 6.19 already drives everything; F45's 7.2 is newer. No `fred` CPU flag without `fred=on`, so upstream's `intel/fred.sh` applies (as a `grubby` argument) |
| GPU | Intel Panther Lake graphics only (`8086:b0a0`, `xe` driver, GuC/HuC firmware loaded); eDP 1920×1200 | **No NVIDIA on this SKU.** The NVIDIA path stays mapped for SKUs with the RTX PRO 500 but isn't tested on this unit |
| Camera | HP 5MP Camera, USB UVC (Chicony `04f2:b882`), plus an IR sensor (`/dev/video2`, `video3`); no IPU PCI device, no MIPI sensor in ACPI | **Plain UVC, works out of the box.** The IPU7 stack (`intel-ipu7-camera`, `v4l2-relayd`) is not needed and is dropped. The IR camera is only for Windows Hello-style face login; not used |
| Fingerprint | Elan `04f3:0c9f` (match-on-chip) | Supported by libfprint's `elanmoc` driver: `fprintd` + `fprintd-pam` through authselect |
| Wi-Fi, Bluetooth | Intel Wi-Fi 7 BE211 320 MHz (CNVi `8086:e340`, `iwlwifi` with the `iwlmld` op mode), Intel Bluetooth over PCIe (`btintel_pcie`) | Both load firmware and work. Upstream's `intel/fix-wifi7-eht.sh` needs a check against this card in Phase 2 |
| Ethernet | Intel I219-LM (`e1000e`) | Works |
| Audio | Intel SOF (`sof-audio-pci-intel-ptl`, firmware 2.14.1.1), HDA codec, 2 digital mics | Works with `alsa-sof-firmware` |
| NPU | Panther Lake NPU (`intel_vpu`, firmware loaded) | Nothing needed for the desktop |
| Input | Synaptics I2C touchpad (`SYNA3165`), HP WMI hotkeys, Intel HID | Works |
| Thunderbolt | Two Thunderbolt 4 controllers | `bolt` for device authorization |
| Power | 77 Wh battery; ACPI platform profiles low-power, balanced, performance | `power-profiles-daemon` / Omarchy's power menu work through `platform_profile` |
| Security chips | TPM 2.0; UEFI | TPM2 LUKS unlock is possible. Secure Boot must be on in the tested configuration |
| Storage | WD PC SN5000S 512 GB NVMe, preloaded with Windows (BitLocker partition present) | The kickstart wipes the disk; no dual boot |

## Booting from USB

- **Secure Boot:** Ventoy's own Secure Boot key could not be enrolled on this unit, so the probe ran with Secure Boot off. Fedora's media are signed by Microsoft and should boot with it on; Phase 2 confirms that and whether the BIOS option "Enable MS UEFI CA key" must be on. If it must, that becomes a requirement for IT.
- **Ventoy:** Fedora 45 live ISOs do not boot from Ventoy 1.1.17; 1.1.18 (2026-10-09) lists the fix.

## Re-probing

Boot any Linux live USB on the laptop and run `fedora/bin/probe-hardware --sudo <file>`. It is read-only, records no serial numbers and masks MAC addresses. Commit the result as `fedora/docs/probes/<sku>.txt`.

## Upstream hardware scripts

`install/hardware/all.sh` runs 38 scripts. For this laptop:

| Kept | Change on Fedora |
| --- | --- |
| `intel/video-acceleration.sh`, `intel/thermald.sh`, `intel/lpmd.sh`, `intel/sof-firmware.sh` | Package names through `packages/map.tsv` only |
| `intel/fix-wifi7-eht.sh` | None (modprobe option) |
| `intel/fred.sh` | Rewrite: `grubby --update-kernel=ALL --args=fred=on` instead of a Limine drop-in |
| `nvidia.sh` | Rewrite: RPM Fusion akmod, dracut instead of mkinitcpio, MOK enrollment. Only for SKUs with the RTX PRO 500; not on the probed unit |
| `vulkan.sh`, `bluetooth.sh`, `network.sh`, `set-wireless-regdom.sh` | Package names only |

Everything else (Apple, ASUS, Dell, Surface, Framework, Lenovo, Tuxedo, Broadcom, Elgato, yt6801, speaker tuning for other models) is left out by a Fedora override of `install/hardware/all.sh`.
