# Fedora fork: firewalld instead of ufw (fedora/docs/DECISIONS.md), with
# upstream's policy: nothing in, everything out, LocalSend allowed.
#
# The default zone keeps only DHCPv6 replies and mDNS (ufw's stock rules allow
# mDNS too, for printer discovery); SSH is closed until
# omarchy-setup-security-sshd opens it. Docker needs no rule: it puts its
# bridges in firewalld's docker zone, which accepts their DNS traffic to the
# host, the job of upstream's allow-docker-dns rules.
#
# Installs are followed by reboot, so the configuration is written offline and
# the live installer's firewall is left alone.
zone=public

# Ask firewalld itself: in Anaconda's chroot `systemctl is-active` reports
# success for anything, while firewall-cmd sees no daemon.
if firewall-cmd --state >/dev/null 2>&1; then
  running=1
  firewall=(firewall-cmd --permanent)
else
  running=0
  firewall=(firewall-offline-cmd)
fi

# firewalld treats a change that is already in place as an error
# (ZONE_ALREADY_SET, ALREADY_ENABLED), so every change is made only when needed.
if [[ $("${firewall[@]}" --get-default-zone) != "$zone" ]]; then
  if (( running )); then
    # The default zone is persistent by itself; it refuses --permanent.
    firewall-cmd --set-default-zone="$zone" >/dev/null
  else
    firewall-offline-cmd --set-default-zone="$zone" >/dev/null
  fi
fi

for service in $("${firewall[@]}" --zone="$zone" --list-services); do
  case $service in
    dhcpv6-client | mdns) ;;
    *) "${firewall[@]}" --zone="$zone" --remove-service="$service" >/dev/null ;;
  esac
done
for service in dhcpv6-client mdns; do
  if ! "${firewall[@]}" --zone="$zone" --query-service="$service" >/dev/null 2>&1; then
    "${firewall[@]}" --zone="$zone" --add-service="$service" >/dev/null
  fi
done

# LocalSend.
for port in 53317/tcp 53317/udp; do
  if ! "${firewall[@]}" --zone="$zone" --query-port="$port" >/dev/null 2>&1; then
    "${firewall[@]}" --zone="$zone" --add-port="$port" >/dev/null
  fi
done

if (( running )); then
  firewall-cmd --reload >/dev/null
fi
systemctl enable firewalld
