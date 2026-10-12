# Fedora fork: only the steps that can apply to the HP ZBook 8 G2i 14" (Intel
# Panther Lake, no NVIDIA), the one laptop Omadora supports
# (fedora/docs/HARDWARE.md). Left out: Apple, ASUS, Dell, Surface, Framework,
# Lenovo, Tuxedo, Broadcom, Elgato and yt6801 fixes, NVIDIA, the IPU7 camera
# stack (the ZBook's camera is USB), and Arch's pacman.sh.
run_logged "$OMARCHY_INSTALL/hardware/network.sh"
run_logged "$OMARCHY_INSTALL/hardware/set-wireless-regdom.sh"
run_logged "$OMARCHY_INSTALL/hardware/fix-fkeys.sh"
run_logged "$OMARCHY_INSTALL/hardware/fix-synaptic-touchpad.sh"
run_logged "$OMARCHY_INSTALL/hardware/bluetooth.sh"
run_logged "$OMARCHY_INSTALL/hardware/vulkan.sh"

run_logged "$OMARCHY_INSTALL/hardware/intel/video-acceleration.sh"
run_logged "$OMARCHY_INSTALL/hardware/intel/lpmd.sh"
run_logged "$OMARCHY_INSTALL/hardware/intel/thermald.sh"
run_logged "$OMARCHY_INSTALL/hardware/intel/fred.sh"
run_logged "$OMARCHY_INSTALL/hardware/intel/fix-wifi7-eht.sh"
run_logged "$OMARCHY_INSTALL/hardware/intel/sof-firmware.sh"

run_logged "$OMARCHY_INSTALL/hardware/speaker-tuning.sh"

run_logged "$OMARCHY_INSTALL/hardware/platform-setup.sh"
