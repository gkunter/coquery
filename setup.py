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
    install_requires = check_dependencies()

    setup(name="coquery",
        author="Gero Kunter",
        author_email="gero.kunter@coquery.org",
        maintainer="Gero Kunter",
        maintainer_email="gero.kunter@coquery.org",
        description="Coquery: A free corpus query tool",
        long_description=long_descr,
        license=GPL3,
        url="http://www.coquery.org",
        version=version,
        install_requires=get_required_modules(),
        packages=['coquery'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications',
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
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
