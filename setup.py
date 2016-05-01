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

from coquery.defines import VERSION as version
with open(os.path.join(os.path.split(os.path.realpath(__file__))[0], "README.rst"), "rb") as f:
    long_descr = f.read().decode("utf-8")

DESCRIPTION = "Coquery: a free corpus query tool"

if __name__ == "__main__":
    required_modules = ["pandas", "sqlalchemy"]
    use_pyqt = False
    use_pyside = False

    try:
        if find_module("PyQt4"):
            use_pyqt = True
    except ImportError:
        pass
    try:
        if find_module("PySide"):
            use_pyside = True
    except ImportError:
        pass

    if not use_pyqt and not use_pyside:
        required_modules.append("PySide")

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
            'Topic :: Education',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Text Processing :: Linguistic']
          )
