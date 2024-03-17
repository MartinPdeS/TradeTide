#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.core import Extension

module = Extension(
    name='TradeTide.binaries.interface',
    sources=['TradeTide/cpp/interface.cpp'],
    language='c++',
    extra_compile_argss=['-std=c++11']
)

setup(
    ext_modules=[module]
)

# -
