# Intune and company compliance

What the company requires of a Linux laptop, and how Omadora meets it. Source: the company's internal "Linux Corporate Device Setup and Support Guide" (read 2026-10-12). This file keeps only what the port needs; internal hosts, certificates, access-package names and support channels stay in that guide, which is not in this public repository.

Intune enrollment is Phase 4 (pilot) work (`DECISIONS.md`). Everything below that Omadora can prepare ships before then.

## Compliance checks

Intune checks these continuously; a failing one makes the device non-compliant and blocks company services in Edge.

| Requirement | Omadora today | Work left |
| --- | --- | --- |
| Supported OS: Fedora newer than 42, x86_64 Intel or AMD | Fedora 45 on the ZBook (Intel) | None. Intune is not for shared machines: one user per device |
| Secure Boot enabled, no exceptions; Secure Boot in User Mode; third-party UEFI certificates allowed | Boots with Secure Boot on through Fedora's shim (tested in a VM with Microsoft's keys) | On the ZBook: confirm HP's "Enable MS UEFI CA key" setting is on (`HARDWARE.md`) |
| Disk encryption at OS level: the whole disk, or the OS and `/home`; `/boot` and `/boot/efi` are ignored | The kickstart encrypts the btrfs with LUKS2 | None (test VMs alone run unencrypted) |
| Microsoft Edge installed | In the base install (`packages/extra.txt`, `repos/microsoft-edge.repo`) | None |
| Microsoft Defender for Endpoint (`mdatp`): installed, healthy, definitions up to date, registered to the organisation, real-time protection on | `mdatp` in the base install | Intune configures and registers it; verify health on the first enrolled pilot device |
| Screen lock settings | Omarchy locks with its Quickshell lock screen (`omarchy-apply-lock`) | Unknown how Intune reads this setting; verify on the first enrolled pilot device |
| Local password: at least 12 characters, one digit, one lowercase and one uppercase letter (no MFA on local accounts) | Not enforced | Ship a `pwquality.conf.d` drop-in: `minlen = 12`, `dcredit = -1`, `lcredit = -1`, `ucredit = -1` |
| Automatic security updates; critical security updates applied daily | No automatic updates | Phase 3 update pipeline: automatic security updates that respect the version locks |
| Full OS update at least every two weeks; Intune reminds every Thursday (14:30 local), allows two postponements, then forces it | `omarchy update` is still Arch's | Phase 3: `omarchy update` runs a full `dnf upgrade --refresh`; the two-week upstream sync rhythm fits this policy |
| Hostname `L<serial>` | Anaconda's default | None: Intune sets it |
| Pulse Secure (Ivanti) policies | No VPN client | Optional per user; see the internal guide |

## Packages Intune needs on Fedora

| Package | Repository | Notes |
| --- | --- | --- |
| `intune-portal` (Company Portal, pulls `microsoft-identity-broker`) | Microsoft RHEL 9 prod (`repos/microsoft.repo`) | Needs `libwebkit2gtk-4.0.so.37`, `libjavascriptcoregtk-4.0.so.18` and libsoup 2, which Fedora 43 and later lack WebKit for. Fedora 45 still ships `libsoup` 2.74 |
| `mdatp` (Defender for Endpoint) | Microsoft RHEL 9 prod | Configured by Intune |
| `microsoft-edge-stable` | Microsoft Edge (`repos/microsoft-edge.repo`) | |
| `webkit2gtk4.0`, `javascriptcoregtk4.0` | COPR `dwrobel/webkit2gtk4.0` (`repos/copr-dwrobel-webkit2gtk4.0.repo`), built for Fedora 43, 44, 45 and Rawhide | Replaces the guide's workaround of taking `webkit2gtk4.0` and `libicu76` from end-of-life Fedora 42 |
| `xorg-x11-server-Xwayland` | Fedora | Intune Portal is an X11 (GTK 3) app; without Xwayland it panics with "Unable to initialize GTK+". The omarchy package requires it |
| `libsecret` (`secret-tool`) | Fedora | Troubleshooting only |

No Java 11 is needed. The current identity broker (3.x) is native code; only `microsoft-identity-diagnostics` asks for a JRE, and accepts Fedora's `java-25-openjdk` (`jre >= 17`). The guide's Temurin 11 steps date from the Java broker.

Verified 2026-10-12 in the test VM (Fedora 45): `intune-portal`, `mdatp` and `microsoft-edge-stable` resolve together from these repositories, and Intune Portal starts and shows its window in the Hyprland session. Enrollment itself is untested until the pilot.

Risk: the COPR's WebKitGTK 4.0 (2.50.0) lags upstream WebKitGTK (2.54.1), so it misses security fixes, and its maintainer may stop. Intune Portal only renders Microsoft's sign-in pages in it. If the COPR goes stale, rebuild it in Omadora's COPR.

All of these repositories get `includepkgs` limits like every other third-party source (`repos/README.md`). The guide's own commands also add whole repositories without limits; Omadora will not.

Fedora release upgrades: the guide removes `intune*` before `dnf system-upgrade` and reinstalls it afterwards. Omadora's release upgrade procedure must do the same.

## How enrollment works

1. Install with full-disk encryption and Secure Boot on, with a local account whose password meets the rules above. Update the UEFI firmware first (`fwupdmgr refresh --force && fwupdmgr update`); disabling Intel AMT in the firmware is recommended, not checked.
2. Request the company's Linux onboarding access package (self-approved), then finish enrollment within 24 hours.
3. Install the packages above, reboot. No VPN during enrollment.
4. Open Edge once and skip its sign-in, keep it open, then start `intune-portal` and sign in. A blank Intune window is worked around with `WEBKIT_DISABLE_COMPOSITING_MODE=1 intune-portal`, which may matter under Hyprland.
5. Intune asks once for the local password, to install a polkit rule, then runs its checks. Compliance can take 10–60 minutes while Defender fetches definitions.

Office, Outlook and Teams are used as Edge web apps (PWAs). Native OneDrive sync and desktop mail clients are not compliant. Company Wi-Fi certificates and profiles arrive through Intune and need NetworkManager.

## What this means for Omadora's design

| Topic | Finding | Status |
| --- | --- | --- |
| Secret storage | Intune keeps its tokens in the desktop's default secret service. Omadora uses GNOME Keyring with an encrypted login keyring unlocked at login. The keyring password must match the account password, so password changes must update it too. Switching to another secret service later breaks enrollment | Decided (GNOME Keyring); the `passwd` sync check stays open in Phase 2 |
| Polkit prompt | Intune asks for the password through polkit once. The guide notes the prompt never appears on i3/Sway | Verified 2026-10-12: Omarchy's Quickshell polkit agent shows the dialog in the Hyprland session |
| Login shell | Root policies are not deployed when the user's shell is zsh | Omarchy uses bash |
| Passwordless sudo | The guide discourages passwordless sudo for daily use | Omarchy's narrow NOPASSWD rules and temporary grants stay (decided 2026-10-12) |
| Slack | The guide describes the Slack RPM | Not used: the company discontinued Slack |
| Java | Company guidelines require OpenJDK, not Oracle Java | No Java in the base install; Fedora's OpenJDK if `microsoft-identity-diagnostics` is ever needed |
