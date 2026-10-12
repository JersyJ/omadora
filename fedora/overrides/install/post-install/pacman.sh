# Fedora fork: upstream restores pacman.conf, the mirrorlist and the keyrings
# here. On Fedora the omadora-repos package owns the repository files, limits
# and version locks, and RPM verifies signatures with the keys each repository
# names, so there is nothing to restore. The CUPS override upstream applies
# here is not used on Fedora (fedora/docs/DECISIONS.md).
:
