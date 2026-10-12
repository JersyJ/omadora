# COPR make_srpm entry point. Each COPR package is an SCM package with
# subdirectory fedora/rpm and spec <name>/<name>.spec; COPR passes the spec
# path and the output directory.

here := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: srpm
srpm:
	bash "$(here)../build-srpm" "$(spec)" "$(outdir)"
