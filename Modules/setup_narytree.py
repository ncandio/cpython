#!/usr/bin/env python3

import os
import sys
from distutils.core import setup, Extension

# Add current directory to sys.path to import the module after building
sys.path.insert(0, '.')

narytree_module = Extension(
    'narytree',
    sources=['narytreemodule.cpp'],
    language='c++',
    extra_compile_args=['-std=c++17', '-O2', '-Wall', '-Wextra'],
    extra_link_args=['-std=c++17']
)

setup(
    name='narytree',
    version='1.0',
    description='N-ary tree data structure for Python',
    author='CPython Extension',
    ext_modules=[narytree_module],
    zip_safe=False,
)