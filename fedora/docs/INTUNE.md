# Intune and company compliance

This file lists the company requirements for a Linux laptop and how Omadora meets them.

- **Source:** the company's internal "Linux Corporate Device Setup and Support Guide" (read 2026-10-12).
- **Scope:** only what the port needs. Internal hosts, certificates, access-package names and support channels stay in the internal guide. Do not put them in this public repository.
- **Status (2026-10-14):** the first ZBook has all packages and settings. Enrollment is not done (Phase 4, `DECISIONS.md`).

## Compliance checks

Intune checks these items continuously. If one check fails, the device is non-compliant and Edge blocks company services.

| Requirement | Omadora | Open |
| --- | --- | --- |
| Fedora newer than 42, x86_64 Intel or AMD. One user per device | Fedora 45, Intel ZBook | None |
| Secure Boot on, in User Mode. Third-party UEFI certificates allowed | Fedora's shim boots with Secure Boot on. On the ZBook: "Enable MS UEFI CA key" on, `mokutil` shows "SecureBoot enabled" (2026-10-14) | None |
| OS disk encryption: the full disk, or the OS and `/home` (`/boot` and `/boot/efi` do not count) | The kickstart encrypts the btrfs with LUKS2. ZBook: encrypted (2026-10-14) | None |
| Microsoft Edge installed | Base install (`packages/extra.txt`, `repos/microsoft-edge.repo`) | None |
| Defender for Endpoint (`mdatp`): installed, healthy, current definitions, registered, real-time protection on | `mdatp` in the base install. ZBook: "No license found" before enrollment (expected) | Intune registers it. Check health after enrollment |
| Screen lock | Quickshell lock screen: Super+Ctrl+L and 5 minutes idle (`idle.lock = 300`), password through `/etc/pam.d/omarchy-lock-password`. Works in the VM (2026-10-13) and on the ZBook, also after resume (2026-10-14) | How Intune reads this setting is not known. Check after enrollment |
| Local password: 12 characters or more, a digit, a lowercase and an uppercase letter | `/etc/security/pwquality.conf.d/50-omadora.conf` (`minlen = 12`, `dcredit = -1`, `lcredit = -1`, `ucredit = -1`). `passwd` applies it through `pam_pwquality` | The kickstart does not check the first password. Choose a compliant password at install |
| Daily critical security updates | `dnf5-automatic.timer`: security updates each day (`upgrade_type = security`), no automatic reboot, snapper snapshots before and after | Packages without advisories (our COPR, the Hyprland COPR) wait for `omarchy update`. How Intune detects updates is not documented. Check after enrollment |
| Full OS update every 2 weeks. Intune reminds each Thursday 14:30, allows 2 postponements, then forces it | `omarchy update`: full `dnf upgrade --refresh`, Flatpak updates, migrations, restart checks | None. The 2-week sync agrees with this |
| Hostname `L<serial>` | Installer default | None: Intune sets it |
| Pulse Secure (Ivanti) | No VPN client | Optional per user (internal guide) |

## Packages

| Package | Repository | Notes |
| --- | --- | --- |
| `intune-portal` (Company Portal; installs `microsoft-identity-broker`) | Microsoft RHEL 10 prod (`repos/microsoft.repo`) | Uses Fedora's WebKitGTK 6.0 and libsoup 3, which Fedora keeps patched. The RHEL 9 build needs WebKitGTK 4.0, which gets no security fixes after 2.50.6 |
| `mdatp` (Defender for Endpoint) | Microsoft RHEL 10 prod | Intune configures it |
| `microsoft-edge-stable` | Microsoft Edge (`repos/microsoft-edge.repo`) | |
| `xorg-x11-server-Xwayland` | Fedora | The RHEL 10 Intune Portal runs on Wayland. `omarchy` requires Xwayland for other X11 apps |
| `libsecret` (`secret-tool`) | Fedora | For troubleshooting only |

- **Java:** not necessary. The identity broker 3.x is native code. Only `microsoft-identity-diagnostics` needs a JRE, and Fedora's `java-25-openjdk` is sufficient. The guide's Temurin 11 steps are for the old Java broker.
- **Signatures:** Microsoft signs the RHEL 10 packages with a newer key (`repos/keys/microsoft-rhel10.asc`). dnf checks package signatures. dnf does not check metadata signatures, as for Fedora's repositories, because the daily unattended update cannot read a metadata key.
- **Limits:** each Microsoft repository has an `includepkgs` limit (`repos/README.md`). The guide's commands add repositories without limits. Omadora does not.
- **Release upgrade:** the guide removes `intune*` before `dnf system-upgrade` and installs it again after. Omadora's release upgrade procedure must do the same.

### Tests

| Date | Where | Result |
| --- | --- | --- |
| 2026-10-12 | VM | `intune-portal`, `mdatp` and `microsoft-edge-stable` resolve together. Intune Portal opens in the Hyprland session |
| 2026-10-13 | VM | The RHEL 10 packages install with no missing libraries, use `webkitgtk6.0` 2.54.1, and show the sign-in window |
| 2026-10-14 | ZBook | All packages installed. `mdatp` waits for its license |

> **NOTE:** Before enrollment, `pam_intune` writes messages at console and SSH logins: "Failed to process authtok" and "No authtok available; password policies will fail". SDDM logins and `passwd` work. After enrollment, check that these messages stop.

## Enrollment

1. Install with disk encryption and Secure Boot on. Use a local password that meets the rules above.
2. Update the UEFI firmware first: `fwupdmgr refresh --force && fwupdmgr update`. The guide recommends Intel AMT off.
3. Request the company's Linux onboarding access package (self-approved). Finish enrollment in 24 hours.
4. Make sure the packages above are installed, then reboot. Do not use a VPN during enrollment.
5. Open Edge. Skip its sign-in and keep Edge open.
6. Start `intune-portal` and sign in.
   - If the Intune window is blank, start it with `WEBKIT_DISABLE_COMPOSITING_MODE=1 intune-portal`.
7. Intune asks one time for the local password (polkit), then runs its checks. Compliance can take 10 to 60 minutes while Defender gets its definitions.

After enrollment:

- Use Office, Outlook and Teams as Edge web apps. Native OneDrive sync and desktop mail clients are not compliant.
- Intune installs the company Wi-Fi certificates and profiles through NetworkManager.

## Effects on Omadora's design

| Topic | Requirement | Omadora |
| --- | --- | --- |
| Secret storage | Intune keeps its tokens in the default secret service. The keyring password must agree with the account password. Another secret service later breaks enrollment | GNOME Keyring. The SDDM password unlocks the login keyring, and `passwd` changes both (tested 2026-10-13) |
| Polkit prompt | Intune asks for the password through polkit. The guide says the prompt does not show on i3 or Sway | Omarchy's Quickshell polkit agent shows the prompt (tested 2026-10-12) |
| Login shell | Root policies are not applied if the shell is zsh | Omarchy uses bash |
| Passwordless sudo | The guide discourages it for daily use | Omarchy's NOPASSWD rules stay (2026-10-12) |
| Slack | The guide describes the Slack RPM | Not used: the company stopped using Slack |
| Java | OpenJDK only, no Oracle Java | No Java in the base install |
