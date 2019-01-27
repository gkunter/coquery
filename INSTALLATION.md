# Installation

See the [Download section](http://www.coquery.org/download/) of the Coquery
website for detailed instructions and requirements. A Windows installer
executable is provided there as well.

Coquery can be installed as a Python module using the Python Index Packager
`pip`. It requires Python version 3.4 or later. To install Coquery as a
Python module, run:
```
    pip install coquery
```

## Required Python modules
In order to run Coquery, the following Python packages have to be present on
your system:

* Pandas 0.23.0 or later
* SQLAlchemy 1.0 or later
* PyQt5 5.6.0 or later

If you use `pip` to install Coquery, these modules are also installed
automatically.

## Optional Python modules
The following modules are optional. You can run Coquery without them, but
installing them provides additional functionality to the program:

* Seaborn 0.9.0 or later
* PyMySQL 0.6.4 or later
* NLTK 3.0 or later
* pdfminer3k

If you wish to install them with `pip`, run:
```
pip install seaborn pymysql nltk pdfminer3k
```
