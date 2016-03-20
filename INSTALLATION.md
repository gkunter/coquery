# Installation

See the [Download section](http://www.coquery.org/download/) of the Coquery
website for detailed instructions and requirements. A Windows installer 
executable is provided there as well.

Coquery can be installed as a Python module using the Python Index Packager 
`pip`. Supported Python versions are 2.7 and versions 3.4 or later.
To install Coquery as a python module, run:
```
    pip install coquery
```

## Required Python modules
In order to run Coquery, the following Python packages have to be present on 
your system:

* Pandas 0.15.0 or later
* SQLAlchemy 1.0 or later
* either PySide 1.2.0 or PyQt4 4.11.0 or later

If you use `pip` to install Coquery, these modules are also installed
automatically.

## Optional Python modules
The following modules are optional. You can run Coquery without them, but 
installing them provides additional functionality to the program:
    
* Seaborn 0.6.0 or later
* PyMySQL 0.6.4 or later
* NLTK 3.0 or later
* PDFMiner/pdfminer3k 

If you wish to install them with `pip`, run
```
pip install seaborn pymysql nltk pdfminer
```
if you are using Python 2.7, or 
```
pip install seaborn pymysql nltk pdfminer3k
```
if you are using Python 3.4 or later.