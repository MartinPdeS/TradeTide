#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from sphinx_gallery.sorting import FileNameSortKey
from pathlib import Path
import TradeTide
from TradeTide.directories import doc_css_path
from martinpdes_docs import configure


package_name = "TradeTide"
version = TradeTide.__version__

current_dir = Path(".")

sys.path.append(str(current_dir.resolve()))


def setup(app):
    app.add_css_file(str(doc_css_path))


autodoc_mock_imports = [
    "numpy",
    "matplotlib",
    "numpydoc",
]


project = package_name
author = "Martin Poinsinet de Sivry-Houle"

globals().update(
    configure(
        project=project,
        package=package_name,
        author=author,
        repository="MartinPdeS/TradeTide",
        logo="_static/logo.svg",
        favicon="_static/favicon.svg",
        version=os.getenv("tag", "latest"),
        extensions=[
            "sphinx.ext.mathjax",
            "sphinx_gallery.gen_gallery",
            "sphinx.ext.autodoc",
            "sphinx.ext.napoleon",
            "sphinx.ext.viewcode",
            "sphinx.ext.autosectionlabel",
            "sphinx.ext.intersphinx",
        ],
    )
)


def reset_mpl(gallery_conf, fname):
    import matplotlib.pyplot as plt

    plt.style.use("default")


sphinx_gallery_conf = {
    "examples_dirs": "../examples/",
    "gallery_dirs": "gallery/",
    "image_scrapers": ("matplotlib"),
    "ignore_pattern": "/__",
    "filename_pattern": r".*\.py",
    "plot_gallery": True,
    "thumbnail_size": [600, 600],
    "download_all_examples": False,
    "reset_modules": reset_mpl,
    "line_numbers": False,
    "remove_config_comments": True,
    "capture_repr": ("_repr_html_", "__repr__"),
    "nested_sections": True,
    "within_subsection_order": FileNameSortKey,
}


html_static_path = ["_static"]
templates_path = ["_templates"]
html_css_files = ["default.css", "layout.css"]
epub_exclude_files = ["search.html"]

# -
