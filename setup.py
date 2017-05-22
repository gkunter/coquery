# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""

try:
    from setuptools import setup
    _has_setuptools = True
except ImportError:
    from distutils.core import setup

import re
import os

from imp import find_module

from coquery import __version__ as version

with open(os.path.join(os.path.split(
        os.path.realpath(__file__))[0], "README.rst"), "rb") as f:
    long_descr = f.read().decode("utf-8")

DESCRIPTION = "Coquery: a free corpus query tool"

if __name__ == "__main__":
    required_modules = ["pandas", "sqlalchemy"]
    use_pyqt = False

    if find_module("PyQt5"):
        use_pyqt = True

    setup(name="coquery",
        author="Gero Kunter",
        author_email="gero.kunter@coquery.org",
        maintainer="Gero Kunter",
        maintainer_email="gero.kunter@coquery.org",
        description="Coquery: A free corpus query tool",
        long_description=long_descr,
        license="GPL3",
        url="http://www.coquery.org",
        version=version.split(" ")[0],
        install_requires=required_modules,
        packages=['coquery',
                  os.path.join('coquery', 'installer'),
                  os.path.join('coquery', 'gui'),
                  os.path.join('coquery', 'gui', 'ui'),
                  os.path.join('coquery', 'visualizer')],
        package_data={'': [
                  os.path.join('coquery', 'icons/*'),
                  os.path.join('coquery', 'help/*'),
                  os.path.join('coquery', 'texts/*')]},
        include_package_data=True,
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
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Education',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Text Processing :: Linguistic']
          )
