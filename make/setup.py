# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""

import re
from setuptools import setup

with open('coquery/__init__.py', "rt") as f:
    version = re.search(
        '^__version__\s*=\s*"(.*)"',
        f.read(), re.M).group(1)

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "coquery",
    version = version,
    author = "Gero Kunter",
    author_email = "gero.kunter@uni-duesseldorf.de",
    url = "(to be added)"
    packages = ["coquery"],
    description = "Coquery is a corpus query tool.",
    long_description = long_descr,
    download_url = "(to be added)"
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",        
        "Topic :: Text Processing :: Linguistic"]
        entry_points = {
            "console_scripts": ['coquery = coquery.coquery:main']
         },
     )
