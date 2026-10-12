# Fedora fork: keep pam_gnome_keyring in SDDM's PAM stack.
#
# Upstream removes it so a password login can't create an encrypted keyring
# next to its passwordless default one. This fork wants the opposite: the
# password typed at SDDM unlocks the encrypted "login" keyring that Intune and
# other libsecret clients use (see install/user/default-keyring.sh). Fedora's
# sddm package ships the auth and session lines, so only check them.
if [[ -f /etc/pam.d/sddm ]]; then
  for stack in auth session; do
    if ! grep -Eq "^-?${stack}[[:space:]].*pam_gnome_keyring\.so" /etc/pam.d/sddm; then
      echo "error: /etc/pam.d/sddm has no $stack line for pam_gnome_keyring.so; the login keyring would not unlock" >&2
      exit 1
    fi
  done
fi
