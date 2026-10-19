SPHINXBUILD ?= sphinx-build
SOURCEDIR = source
BUILDDIR = _build
PYTHONPATH ?= ../../MartinPdeS-docs

.PHONY: help clean html

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf "$(BUILDDIR)"

html:
	PYTHONPATH="$(PYTHONPATH)" $(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
