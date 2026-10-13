#!/bin/bash

# Run upstream's graphical acceptance suite (test/acceptance) inside the
# desktop session of a test VM, the way upstream runs it in its own throwaway
# VMs: apps, panels, menus, input methods, shell surfaces, security and system
# checks. The suite opens apps and changes settings, so only ever run it in a
# VM, never on a workstation.
#
# Needs a VM installed with OMADORA_VM_PASSWORD_LOGIN=1 (fedora/tests/vm-install.sh):
# it logs in at SDDM, copies test/ from HEAD into the VM over the VM's host
# network, runs the suite, and brings the log and screenshots back to
# <workdir>/acceptance/. Fails when a test file fails that
# fedora/tests/acceptance-expected-failures.txt does not list, or a listed one
# passes.
#
# Usage: fedora/tests/vm-acceptance.sh [workdir]
#   OMADORA_VM_PASSWORD=<text>  the test user's password (default omadora-test)
#   OMADORA_VM_SB_VARS=<file>   boot with Secure Boot on (see vm-console.py)

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

work=$(realpath "${1:-$FEDORA_DIR/.build/vm}")
password=${OMADORA_VM_PASSWORD:-omadora-test}
out=$work/acceptance
export OMADORA_VM_DIR=$work OMADORA_VM_LUKS=omadora-disk OMADORA_VM_PASSWORD=$password

cd "$FEDORA_ROOT"
rm -rf "$out"
mkdir -p "$out/serve"
git archive --prefix=omarchy-tests/ HEAD test | gzip >"$out/serve/tests.tar.gz"

# A small server on the host's loopback, which the VM reaches as 10.0.2.2:
# it serves the tests and takes the artifacts back with PUT.
port=$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 - "$out/serve" "$port" >"$out/http.log" 2>&1 <<'PY' &
import http.server, os, sys
root, port = sys.argv[1], int(sys.argv[2])
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=root, **kwargs)
    def do_PUT(self):
        length = int(self.headers.get("Content-Length", 0))
        with open(os.path.join(root, "upload-" + os.path.basename(self.path)), "wb") as upload:
            upload.write(self.rfile.read(length))
        self.send_response(201)
        self.end_headers()
http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
PY
server=$!
trap 'kill "$server" 2>/dev/null || true' EXIT

# The suite runs from the serial console, outside the session, so take the
# session's desktop name: Omadora's MIME defaults are Hyprland's own list.
info "Logging in and running upstream's acceptance suite in the VM"
OMADORA_VM_COMMAND_TIMEOUT=4000 "$FEDORA_DIR/tests/vm-console.py" --sddm-login \
  "rm -rf ~/omarchy-tests ~/acceptance; mkdir -p ~/acceptance; curl -sf http://10.0.2.2:$port/tests.tar.gz | tar -xz -C ~" \
  "cd ~/omarchy-tests && XDG_CURRENT_DESKTOP=Hyprland OMARCHY_ACCEPTANCE_SUDO_PASSWORD='$password' OMARCHY_ACCEPTANCE_DIR=\$HOME/acceptance timeout 3900 test/acceptance >\$HOME/acceptance/suite.log 2>&1; cd ~" \
  "tar -czf /tmp/acceptance.tgz -C ~/acceptance . && curl -sf -T /tmp/acceptance.tgz http://10.0.2.2:$port/acceptance.tgz" >"$out/console.log"

[[ -f $out/serve/upload-acceptance.tgz ]] || die "no results came back from the VM; see $out/console.log"
tar -xzf "$out/serve/upload-acceptance.tgz" -C "$out"
rm -rf "$out/serve"

grep -E '^(ok|not ok|==>)' "$out/suite.log"

# Failed test files: a "not ok" line under a file's "==>" header.
mapfile -t failed < <(awk '/^==> / { file = $2 } /^not ok/ && file != "" { print file }' "$out/suite.log" | sort -u)
expected_file=$FEDORA_DIR/tests/acceptance-expected-failures.txt
mapfile -t expected < <(grep -vE '^\s*(#|$)' "$expected_file" | awk '{ print $1 }' | sort -u)

unexpected=$(comm -23 <(printf '%s\n' "${failed[@]}" | sed '/^$/d') <(printf '%s\n' "${expected[@]}" | sed '/^$/d'))
# A listed file that passes again fails the run, unless its reason starts with "flaky:".
fixed=$(comm -13 <(printf '%s\n' "${failed[@]}" | sed '/^$/d') <(printf '%s\n' "${expected[@]}" | sed '/^$/d') |
  grep -vxF -f <(grep -E '^[^#][^[:space:]]*[[:space:]]+flaky:' "$expected_file" | awk '{ print $1 }') || true)

status=0
if [[ -n $unexpected ]]; then
  echo "Failing and not listed in $expected_file:"
  printf '  %s\n' $unexpected
  status=1
fi
if [[ -n $fixed ]]; then
  echo "Listed in $expected_file but passing now (remove them):"
  printf '  %s\n' $fixed
  status=1
fi
(( status == 0 )) && info "Acceptance suite: no unexpected results (log and screenshots in $out)"
exit "$status"
