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
        logo="../images/logo.png",
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
        html_theme_options={
            "logo": {"text": "", "image": "../images/logo.png"},
        },
    )
)


sphinx_gallery_conf.update(
    {
        "within_subsection_order": FileNameSortKey,
    }
)



# -
