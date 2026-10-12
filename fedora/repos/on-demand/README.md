# On-demand repositories

Repositories that Omadora adds only when someone installs an app that needs one; `omarchy-pkg-add` reads the source from `fedora/packages/map.tsv` (Phase 2). Each is limited with `includepkgs` to that app.

| File | For | Why this source |
| --- | --- | --- |
| `1password.repo`, `brave-browser*.repo`, `google-chrome.repo`, `code.repo`, `sublime-text.repo`, `nordvpn.repo`, `dropbox.repo`, `symfony-cli.repo`, `cursor.repo` | Proprietary apps | The vendor's own signed RPM repository |
| `copr-sneexy-zen-browser.repo`, `copr-che-zed.repo` | Zen Browser, Zed | Dedicated COPRs that track upstream releases with Fedora 45 builds |
| `copr-lizardbyte-stable.repo` | Sunshine | Upstream's own COPR |
| `copr-neovi-xpadneo.repo` | Xbox controller driver | Dedicated COPR, current, akmod (signed with the machine's MOK under Secure Boot) |

Decided 2026-10-12: vendor repositories for apps whose vendor runs one; for apps without, a maintained COPR when one exists, otherwise Flathub.
