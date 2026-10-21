#!/usr/bin/env python
# -*- coding: utf-8 -*-

from martinpdes_docs import configure


autodoc_mock_imports = [
    "numpy",
    "matplotlib",
    "numpydoc",
]

globals().update(
    configure(
        project="TradeTide",
        package="TradeTide",
        author="Martin Poinsinet de Sivry-Houle",
        repository="MartinPdeS/TradeTide",
        logo="../images/logo.png",
        favicon="_static/favicon.svg",
        prefer_installed_package=True,
        gallery_default_thumb="../images/logo.png",
        html_theme_options={
            "logo": {"text": "", "image": "../images/logo.png"},
        },
    )
)


# -
