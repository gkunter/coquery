# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -d ./doctrees .
SPHINXBUILD   = sphinx-build
BUILDDIR      = ..
BUILDFORMAT   = -b html

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from http://sphinx-doc.org/)
endif

.PHONY: help html inline

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make standalone HTML files"
	@echo "  inline	    to make inline help HTML files"

html:
	$(SPHINXBUILD) $(BUILDFORMAT) $(SPHINXOPTS) -c . ../html
	@echo
	@echo "Build finished. The HTML pages are in ../html."


inline: 
	$(SPHINXBUILD) $(BUILDFORMAT) $(SPHINXOPTS) -c ../coquery/help ../coquery/help
	@echo
	@echo "Build finished. The inline help HTML pages are in ../coquery/help."
