# On-demand repositories

Omadora adds these repositories only when you install an app that needs one. `omarchy-pkg-add` reads the source from `fedora/packages/map.tsv`. Each repository has an `includepkgs` limit for its app.

| File | For | Source |
| --- | --- | --- |
| `1password.repo`, `brave-browser*.repo`, `google-chrome.repo`, `code.repo`, `sublime-text.repo`, `nordvpn.repo`, `dropbox.repo`, `symfony-cli.repo`, `cursor.repo`, `grok-bot.repo` | Proprietary apps | The vendor's signed RPM repository |
| `copr-sneexy-zen-browser.repo`, `copr-che-zed.repo`, `copr-mineiro-ghostty.repo` | Zen Browser, Zed, Ghostty | COPRs that follow upstream releases, with Fedora 45 builds |
| `copr-lizardbyte-stable.repo` | Sunshine | Upstream's COPR |
| `copr-neovi-xpadneo.repo` | Xbox controller driver | A current COPR. akmod, signed with the machine's MOK when Secure Boot is on |

Rule (2026-10-12): use the vendor repository if the vendor has one. Otherwise use a maintained COPR, or else Flathub.
