# COPR make_srpm entry point for jersyj/omadora. COPR runs it from the
# repository root's .copr/ with the spec path of the package being built; each
# COPR package is an SCM package with spec fedora/rpm/<name>/<name>.spec.
# Owned by the fork, like fedora/.

root := $(abspath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))..)

.PHONY: srpm
srpm:
	bash "$(root)/fedora/rpm/build-srpm" "$(spec)" "$(outdir)"
