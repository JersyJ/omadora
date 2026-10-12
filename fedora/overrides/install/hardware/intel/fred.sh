# Enable Flexible Return and Event Delivery on Intel Panther Lake.
# Fedora fork: Fedora boots with GRUB and BLS entries instead of Limine, so the
# argument goes to every installed kernel's entry through grubby and into the
# files kernel-install and grub2-mkconfig read for future kernels.

if omarchy-hw-intel-ptl; then
  sudo grubby --update-kernel=ALL --args=fred=on

  if [[ -f /etc/kernel/cmdline ]] && ! grep -qw 'fred=on' /etc/kernel/cmdline; then
    sudo sed -i '1 s/$/ fred=on/' /etc/kernel/cmdline
  fi

  if [[ -f /etc/default/grub ]] && ! grep -q '^GRUB_CMDLINE_LINUX=.*fred=on' /etc/default/grub; then
    sudo sed -i 's/^GRUB_CMDLINE_LINUX="\(.*\)"/GRUB_CMDLINE_LINUX="\1 fred=on"/' /etc/default/grub
  fi
fi
