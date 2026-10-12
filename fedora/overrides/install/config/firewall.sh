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

if systemctl is-active --quiet firewalld; then
  firewall=(firewall-cmd --permanent)
else
  firewall=(firewall-offline-cmd)
fi

"${firewall[@]}" --set-default-zone="$zone" >/dev/null
for service in $("${firewall[@]}" --zone="$zone" --list-services); do
  case $service in
    dhcpv6-client | mdns) ;;
    *) "${firewall[@]}" --zone="$zone" --remove-service="$service" ;;
  esac
done
for service in dhcpv6-client mdns; do
  "${firewall[@]}" --zone="$zone" --add-service="$service" >/dev/null
done

# LocalSend.
"${firewall[@]}" --zone="$zone" --add-port=53317/tcp >/dev/null
"${firewall[@]}" --zone="$zone" --add-port=53317/udp >/dev/null

if systemctl is-active --quiet firewalld; then
  firewall-cmd --reload >/dev/null
fi
systemctl enable firewalld
