#!/bin/bash

# Install each of Omarchy's optional extras in a test VM through Omarchy's own
# package command (omarchy-pkg-add, what the Install menu runs), then check it:
# a command answers, or a desktop app opens a window in the Hyprland session.
# Run it after the extras' recipes or their map entries change.
#
# Needs a VM installed with OMADORA_VM_PASSWORD_LOGIN=1 (fedora/tests/vm-install.sh)
# whose packages include the map being tested. Prints one line per extra and
# fails when any did not install or did not start.
#
# Usage: fedora/tests/vm-extras.sh [workdir] [extra...]
#   OMADORA_VM_PASSWORD=<text>  the test user's password (default omadora-test)
#   OMADORA_VM_SB_VARS=<file>   boot with Secure Boot on (see vm-console.py)

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

work=$(realpath "${1:-$FEDORA_DIR/.build/vm}")
shift || true
password=${OMADORA_VM_PASSWORD:-omadora-test}
export OMADORA_VM_DIR=$work OMADORA_VM_LUKS=omadora-disk OMADORA_VM_PASSWORD=$password

# Arch name | check: "cmd:<command line>" or "window:<command>:<window class regex>"
extras=(
  "omarchy-emacs|cmd:command -v omarchy-install-emacs emacs"
  "omazed|cmd:command -v omazed"
  "once-bin|cmd:once --version"
  "voxtype-bin|cmd:voxtype --version"
  "umu-launcher|cmd:umu-run --help"
  "ghostty|window:ghostty:ghostty"
  "claude-desktop|window:claude-desktop:(?i)claude"
  "openai-codex-desktop|window:chatgpt:(?i)chatgpt"
  "grok-bot|window:grok-bot:(?i)grok"
  # Not offered (todo in the map): hermes-desktop, perplexity, t3code-bin, lmstudio-bin.
)
if (( $# > 0 )); then
  selected=()
  for extra in "${extras[@]}"; do
    for name in "$@"; do
      [[ ${extra%%|*} == "$name" ]] && selected+=("$extra")
    done
  done
  extras=("${selected[@]}")
fi

session='export XDG_RUNTIME_DIR=/run/user/$(id -u) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus; eval "$(systemctl --user show-environment | grep -E "^(WAYLAND_DISPLAY|DISPLAY|XDG_CURRENT_DESKTOP|HYPRLAND_INSTANCE_SIGNATURE|PATH)=" | sed "s/^/export /")"'
commands=()
for extra in "${extras[@]}"; do
  name=${extra%%|*}
  check=${extra#*|}
  case $check in
    cmd:*)
      test_line="${check#cmd:} >/dev/null 2>&1"
      ;;
    window:*)
      spec=${check#window:}
      launch=${spec%%:*}
      class=${spec#*:}
      test_line="(setsid $launch >/tmp/extra-$name.log 2>&1 &); for i in \$(seq 60); do hyprctl -j clients | jq -e --arg c '$class' 'any(.[]; .class | test(\$c))' >/dev/null && break; sleep 2; done; hyprctl -j clients | jq -e --arg c '$class' 'any(.[]; .class | test(\$c))' >/dev/null"
      ;;
  esac
  # sudo's cached credential lasts minutes; refresh it before each install.
  commands+=("$session; printf '%s\\n' '$password' | sudo -S -v -p ''; if timeout 1200 omarchy-pkg-add $name >/tmp/extra-$name-install.log 2>&1; then if $test_line; then echo \"EXTRA $name ok\"; else echo \"EXTRA $name installed, check failed\"; tail -n 5 /tmp/extra-$name.log 2>/dev/null; fi; else echo \"EXTRA $name did not install\"; tail -n 8 /tmp/extra-$name-install.log; fi")
done

OMADORA_VM_COMMAND_TIMEOUT=1800 "$FEDORA_DIR/tests/vm-console.py" --sddm-login "${commands[@]}" "@shot extras-last" | tee "$work/extras.log" | grep -av '^[$#] ' | grep -aoE 'EXTRA .*|^  .*' || true

# Terminal replies can precede a marker on its line, so markers match anywhere;
# vm-console's echo of each command ("$ ...") holds the marker text too.
results=$(grep -av '^[$#] ' "$work/extras.log" || true)
failed=$(grep -ac 'EXTRA .* \(did not install\|check failed\)' <<<"$results" || true)
passed=$(grep -ac 'EXTRA .* ok$' <<<"$results" || true)
info "Extras: $passed ok, $failed failed (log: $work/extras.log)"
(( failed == 0 && passed == ${#extras[@]} ))
