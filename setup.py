#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.core import Extension

module = Extension('cpp_position', sources=['TradeTide/cpp/position.cpp'], language='c++')

setup(
    ext_modules=[module]
)

# -
