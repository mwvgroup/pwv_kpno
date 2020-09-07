# This makefile is configured to generate Sphinx documentation for the pwv_kpno
# python package.

SPHINXBUILD   = python -msphinx
SPHINXPROJ    = pwv_kpno
SOURCEDIR     = ./
BUILDDIR      = ./build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

PACKAGE_VERSION=$(shell pip show pwv_kpno | grep Version | cut -f 2 -d ' ')

gh-pages:
	make html BUILDDIR=../../$(PACKAGE_VERSION)/documentation
