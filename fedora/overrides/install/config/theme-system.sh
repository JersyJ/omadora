# Set links for Nautilus action icons
mkdir -p /usr/share/icons/Yaru/scalable/actions
ln -snf /usr/share/icons/Adwaita/symbolic/actions/go-previous-symbolic.svg \
          /usr/share/icons/Yaru/scalable/actions/go-previous-symbolic.svg
ln -snf /usr/share/icons/Adwaita/symbolic/actions/go-next-symbolic.svg \
          /usr/share/icons/Yaru/scalable/actions/go-next-symbolic.svg
gtk-update-icon-cache /usr/share/icons/Yaru &>/dev/null || true

# Seed Chromium's first run: follow system appearance ("device") instead of dark,
# and skip the terms-of-service dialog Chromium 151 turned on by default.
# Fedora fork: Fedora's Chromium reads its initial preferences from
# /etc/chromium/master_preferences (Arch: /usr/lib/chromium/initial_preferences).
mkdir -p /etc/chromium
echo '{"distribution":{"require_eula":false},"browser":{"theme":{"color_scheme":0,"color_scheme2":0}}}' > \
  /etc/chromium/master_preferences
