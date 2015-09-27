# Requirements

## Required Python modules:
In order to run Coquery, the following Python packages have to be present on your system:

- NumPy       (version 1.7.0 or later)
- pandas      (version 0.15.0 or later)
- Matplotlib  (version 1.4.0 or later)
- Seaborn     (version 0.6.0 or later)
- PyMySQL     (version 0.6.4 or later)
- EITHER PySide      (recommended, version 1.2.0 or later)
  OR
  PyQt4       (alternative, version 4.11.0 or later)

It is recommended to use the Python installer ``pip`` to obtain the latest versions of these packages. In order to install these Python modules using `pip`, open a command shel, and enter:
```
pip install numpy pandas matplotlib seaborn pymysql pyside
```

## Database server
In order to install corpora and run queries using Coquery, a database server needs to be installed. MySQL and MariaDB are both database servers which provide the infrastructure required to install corpora and run queries using Coquery. Both are freely available. For Linux, MariaDB is usually the default choice. Only MySQL is available under Windows.

On most Linux distributions, either database server can easily be installed using the system package manager. Windows and Mac OS X users may want to follow the [MySQL Installation guide](http://dev.mysql.com/doc/refman/5.7/en/installing.html). 
Note that during installation, you will probably be asked to enter a root password for the database server. Choose a suitable password, and remember it. You will need this password to set up the MySQL connection in Coquery.


## Optional: Installing the Natural Language Toolkit (NLTK)
The Python package NLTK Natural Language Toolkit) is only used if you wish to compile your own corpus from a collection of texts, and wish to use an automatic part-of-speech tagger for these texts. You can compile your own corpora without NLTK, but in that case, you cannot include part-of-speech information in your queries.

Details on the very useful NLTK package are given on the [Natural Language Toolkit homepage](http://www.nltk.org/). 
The site contains also [Installation instructions](http://www.nltk.org/install.html). In order to use NLTK for the compilation of your own corpus, a tagger and a tokenizer need to be 
Instructions on how to install these language-specific NLTK data packages are given [here](http://www.nltk.org/data.html). 

# THE REMAINDER OF THIS FILE CONTAINS OBSOLETE INFORMATION 
# Installation #

## Quick Guide: Installing Coquery on Windows ##

## Quick Guide: Installing Coquery on Linux ##

If you want to install Coquery on a computer running Debian, Ubuntu or Linux Mint, run the following commands:
```
#!bash
$ sudo apt-get install python python-pip python-mysqldb python-pyside python-nltk mariadb-server 
$ pip install coquery 
```
## Quick Guide: Installing Coquery on Mac OS X ##

## Detailled description ##

Installing Coquery consists of three parts:

* installing the components that are needed to run Coquery
* installing and setting up a database system that will store the corpora
* installing the corpora that you want to use

Each of these parts is described in detail below.

### Python (required) ###
Coquery is written in the Python programming language. This language is pre-installed on most Linux and Mac OS X computers; Windows users may need to install Python manually.

Installation packages for Python are freely available at [Python Downloads](https://www.python.org/downloads/). The script runs supports version 2.7 as well as version 3.3 or higher. Python 2.7 is the recommended version.

### Python Package Installer pip (required) ###

The [Python package installer](https://pypi.python.org/pypi/pip) is used to install Coquery. pip is automatically 
installed with Python versions 2.7.9 and higher, and Python versions 3.4 and higher. If you are using a Python version
that does not ship with pip, please follow the pip 
[installation instructions](https://pip.pypa.io/en/stable/installing.html). On most Linux distributions, pip is also 
available in the system package manager (e.g. Synaptic, aptitude, YaST2).

### MySQLdb or PyMySQL (required) ###
MySQLdb and PyMySQL are Python package that are used by Coquery to interact with the database system. Only one of the two packages is required in order to run Coquery. MySQLdb is the recommended package, as corpus queries using it are notably faster if compared to the same queries using PyMySQL. However, MySQLdb only supports Python versions up to 2.7. If you use Python 3.3 or higher, you need to install PyMySQL.

Installing MySQLdb using pip:
```
#!bash
pip install mysql-python
```

Installing PyMySQL using pip:
```
#!bash
pip install pymysql
```

### PyQt or PySide (optional) ###
Either the Pyhton packages PyQt or PySide are used if you want to use the graphical interface for Coquery.

PySide can be installed using pip:
```
#!bash
pip install pyside 
```

PyQt can be obtained from the [PyQt homepage](http://www.riverbankcomputing.co.uk/software/pyqt/intro). Coquery supports PyQt4, but not PyQt5.

### MySQL/MariaDB database server ###
MySQL and MariaDB are both database servers which provide the infrastructure required to install corpora and run queries using Coquery. Both are freely available. For Linux, MariaDB is usually the default choice. Only MySQL is available under Windows.

On most Linux distributions, either database server can easily be installed using the system package manager. Windows and Mac OS X users may want to follow the [MySQL Installation guide](http://dev.mysql.com/doc/refman/5.7/en/installing.html). 
Note that during installation, you will probably be asked to enter a root password for the database server. Choose a suitable password, and remember it. You will need this password during the Coquery installation process.

Installing mariadb on Debian, Ubunutu or Linux Mint:
```
#!bash
sudo apt-get install mariadb-server
```

## Install Coquery ##
Once the required and recommended packages are installed, you can proceed to install Coquery. This can easily be done using pip:

```
#!bash
pip install coquery
```

During the installation, you will be asked for the root password for the MySQL/MariaDB database server (see last step of previous section). You will also be asked for a database user name, the database passwort, the database host and a port number. Unless you are running the
database on a remote server uning the network, you can use the default values:

```
User name: coquery
Password: coquery
Hostname: localhost
Port number: 3306
```

The installation routine will set up a database user with this name and this password. 
It will also write these values to a configuration file so that these credentials are used in the future whenever Coquery is run.

## Install corpora ##
Coquery provides corpus modules for some popular linguistic corpora, 
most notably the British National Corpus, the Corpus of Contemporary American English, 
and the Corpus of Historical American English. 

The Coquery corpus modules *do not* provide the corpus data themselves. These files must be obtained from the corpus maintainers.
A Coquery corpus module installer reads the corpus files into a MySQL/MariaDB database and installs a corpus module so that
Coquery can use for queries on the respective corpus. Coquery does not need the original corpus files anymore cnce the respective
corpus module has been sucessfully installed.  

A list of available corpus module installers can be obtained using pip:
```
#!bash
$ pip search coq_
coq_bnc
coq_coca
coq_coha
...
```

Install any of these installer to install that corpus module:
```
$ pip install coq_coca
```

### Example: Installing the BNC ###
An XML-encoded edition of the British National Corpus can be freely obtained. If you want to query the British National Corpus using Coquery,
follow the instructions on the [BNC website](http://www.natcorp.ox.ac.uk/XMLedition/). Once you have downloaded and extracted the XML files,
you can install the BNC corpus module:
```
$ pip install coq_bnc
Enter the location of the BNC files: /home/kunter/downloads/BNC/XML/
```

The installer will take a considerable amount of time, and it will require also several gigabytes of hard disk space. Once it has completed, you can
delete the XML source files (or move them to a removable device) to free up your hard disk. 

After that, you can run your first query on the BNC using Coquery:
```
coquery --corpus BNC -q "a multitude of possibilities" -c 15 -t
```

If you want to remove the BNC database and the corpus module, use the uninstall command:
```
$ pip uninstall coq_bnc
```

### Example: Compiling your own corpus ###
You can build your own corpus using any collection of texts that are stored on your computer. This example illustrates the required steps.

```
#!bash
coq_generic de_quincey
Enter the location of the text files: /opt/coquery/test/de_quincey
```

The script will process all text files stored in the given directory, and store the information into a new corpus named 'de_quincey'. 
This corpus can then be used with Coquery:
```
coquery --corpus DE_QUINCEY -q "a|an|the *{0,3} game" -O
```

### Automatic part-of-speech tagging using NLTK ###
The Python package NLTK Natural Language Toolkit) is only used if you wish to compile your own corpus from a collection of texts, and wish to use an automatic part-of-speech tagger for these texts. You can compile your own corpora without NLTK, but in that case, you cannot include part-of-speech information in your queries.

Details on the very useful NLTK package are given on the [Natural Language Toolkit homepage](http://www.nltk.org/). 
The site contains also [Installation instructions](http://www.nltk.org/install.html). In order to use NLTK for the compilation of your own corpus, a tagger and a tokenizer need to be 
Instructions on how to install these language-specific NLTK data packages are given [here](http://www.nltk.org/data.html). 

Instaling NLTK using pip (you still need to install the NLTK data packages):
```
#!bash
pip install ntlk 
```

Note that NLTK may depend on other Python packages, such as the numpy package. If you receive an error during corpus compilation that seems to refer to 'numpy', try this:
```
#!bash
pip install numpy
```
~~