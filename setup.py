# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""

try:
    from setuptools import setup
    _has_setuptools = True
except ImportError:
    from distutils.core import setup

import re

from coquery.defines import VERSION as version

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

DESCRIPTION = "Coquery: a free corpus query tool"

if __name__ == "__main__":

    setup(name="coquery",
        author="Gero Kunter",
        author_email="gero.kunter@coquery.org",
        maintainer="Gero Kunter",
        maintainer_email="gero.kunter@coquery.org",
        description="Coquery: A free corpus query tool",
        long_description=long_descr,
        license="GPL3",
        url="http://www.coquery.org",
        version=version,
        install_requires=["pandas", "sqlalchemy"],
        packages=['coquery', 'coquery/installer', 'coquery/gui', 'coquery/gui/ui/', 'coquery/visualizer'],
        entry_points={
            'console_scripts': ['coqcon = coquery.coquery:main_console', ],
            'gui_scripts': ['coquery = coquery.coquery:main', ]
            },
        keywords="corpus linguistics query corpora analysis visualization",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: MacOS',
            'Operating System :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Education',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Text Processing :: Linguistic']
          )
