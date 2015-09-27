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