# Fedora fork: no passwordless default keyring.
#
# Upstream creates an unencrypted "Default_keyring" so autologin sessions never
# prompt for a keyring password. This fork logs in through SDDM with a
# password, and pam_gnome_keyring (kept in /etc/pam.d/sddm, see
# install/login/sddm.sh) creates and unlocks the encrypted "login" keyring with
# that password. Microsoft Intune's identity broker stores its tokens in that
# keyring through libsecret, so it must exist, be the default, and be
# encrypted. gnome-keyring makes "login" the default when no other keyring
# claims it, so there is nothing to create here.
:
