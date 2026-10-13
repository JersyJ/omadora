#!/bin/bash

# Weekly health check of the third-party repositories Omadora installs from
# (.github/workflows/fedora-repos-check.yml; runs anywhere with curl, gpg and
# python3).
#
# Fails when a signing key in fedora/repos/keys no longer matches the key its
# repository publishes: the repository rotated its key, and laptops would stop
# trusting its updates until the new key is reviewed and committed.
# Reports, without failing: when each COPR last built successfully (a COPR
# that stopped building is the early sign of an abandoned one) and whether it
# already builds for the next Fedora release.
#
# Usage: fedora/tests/repos-check.sh
# Writes a Markdown report to $GITHUB_STEP_SUMMARY when set, else to stdout.

set -euo pipefail
source "$(dirname "$(realpath "$0")")/../lib/common.sh"

cd "$FEDORA_ROOT"
load_lock
next=$(( FEDORA_RELEASE + 1 ))
report=${GITHUB_STEP_SUMMARY:-/dev/stdout}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

fingerprints() {
  gpg --show-keys --with-colons "$1" 2>/dev/null | awk -F: '/^fpr/ { print $10 }' | sort -u
}

status=0
{
  echo "## Signing keys"
  echo
  echo "| Key | Result |"
  echo "| --- | --- |"
} >>"$report"
while IFS=$'\t' read -r file url; do
  [[ -z $file || $file == \#* ]] && continue
  if ! curl -sfL --max-time 60 "$url" -o "$tmp/published"; then
    echo "| \`$file\` | could not download $url |" >>"$report"
    status=1
  elif [[ $(fingerprints "fedora/repos/keys/$file") == "$(fingerprints "$tmp/published")" ]]; then
    echo "| \`$file\` | matches |" >>"$report"
  else
    echo "| \`$file\` | **changed**: review the new key at $url, then replace fedora/repos/keys/$file |" >>"$report"
    status=1
  fi
done <fedora/repos/keys/sources.tsv

{
  echo
  echo "## COPRs"
  echo
  echo "| COPR | Last successful build | Fedora $next |"
  echo "| --- | --- | --- |"
} >>"$report"
grep -ho '^\[copr:copr.fedorainfracloud.org:[^]]*\]' fedora/repos/*.repo fedora/repos/on-demand/*.repo |
  sed 's/^\[copr:copr.fedorainfracloud.org://; s/\]$//' | sort -u |
  while IFS=: read -r owner project; do
    python3 - "$owner" "$project" "$next" <<'PY' >>"$report"
import datetime, json, sys, urllib.request
owner, project, nxt = sys.argv[1:4]
api = "https://copr.fedorainfracloud.org/api_3"
def get(path):
    with urllib.request.urlopen(f"{api}/{path}", timeout=60) as response:
        return json.load(response)
try:
    chroots = get(f"project?ownername={owner}&projectname={project}").get("chroot_repos", {})
    builds = get(f"build/list?ownername={owner}&projectname={project}&status=succeeded&limit=1").get("items", [])
except Exception as error:
    print(f"| {owner}/{project} | could not query: {error} | |")
    sys.exit(0)
last = "none"
if builds and builds[0].get("ended_on"):
    ended = datetime.datetime.fromtimestamp(builds[0]["ended_on"], datetime.timezone.utc)
    days = (datetime.datetime.now(datetime.timezone.utc) - ended).days
    last = f"{ended:%Y-%m-%d} ({days} days ago)" + (" **stale?**" if days > 120 else "")
ready = "yes" if f"fedora-{nxt}-x86_64" in chroots else "not yet"
print(f"| {owner}/{project} | {last} | {ready} |")
PY
  done

exit "$status"
