# -*- coding: utf-8 -*-
"""setup.py: setuptools control."""

try:
    from setuptools import setup
    _has_setuptools = True
except ImportError:
    from distutils.core import setup

import re

def has_module(name):
    """
    Check if the Python module 'name' is available.
    
    Parameters
    ----------
    name : str 
        The name of the Python module, as used in an import instruction.
        
    This function uses ideas from this Stack Overflow question:
    http://stackoverflow.com/questions/14050281/
        
    Returns
    -------
    b : bool
        True if the module exists, or False otherwise.
    """

    if sys.version_info > (3, 3):
        import importlib.util
        return importlib.util.find_spec(name) is not None
    elif sys.version_info > (2, 7, 99):
        import importlib
        return importlib.find_loader(name) is not None
    else:
        import pkgutil
        return pkgutil.find_loader(name) is not None


with open('coquery/defines.py', "rt") as f:
    version = re.search('^VERSION\s*=\s*"(.*)"', f.read(), re.M).group(1)

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

DESCRIPTION = "Coquery: a free corpus query tool"
LONG_DESCRIPTION = """\
Coquery is a free corpus query tool for linguistis, lexicographers, 
translators, and anybody who wishes to search and analyse text corpora.
It is available for Windows, Linux, and Mac OS X computers.

You can either build your own corpus from a collection of text files
or PDF documents in a directory on your computer, or install a corpus 
module for one of the supported corpora (the corpus data files are not
provided by Coquery).

A corpus can then be queried using a simple, yet expressive query syntax.
The query produces a list of matching tokens that can be flexibly arranged
in the form of token tables, frequency tables, contingency tables, and
collocation tables. Coquery can also calculate different statistics such as 
normalized frequencies, Shannon entropy, or mutual information scores.

Several diagram modules are available to create visualizations of frequency
distributions, categorical differences, or diachronic changes.
"""



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
