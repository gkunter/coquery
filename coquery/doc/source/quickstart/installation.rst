.. _installation:

Installation 
############

There are two principal ways of installing Coquery on your computer: a 
binary installation, and a source installation.

Binary installation (Windows only)
==================================

Binary installations are only available on Windows systems. Here, you 
download an installer from `<http://www.coquery.org/downloads/>`_. The 
binary installater is a relatively large file (about 128Mb). After 
executing the installer and following the on-screen instructions, Coquery 
will be available to the user.

Source installation (Windows, Linux, Mac OS X)
==============================================

Coquery is written in the Python programming language. Python is standardly
available on Linux and Mac OS X computers, and can be freely installed on 
Windows computers. On computers with the Python interpreter installed, the 
source installation is recommended, as the download size is much smaller 
(less than 5Mb). Also, starting Coquery is slightly faster. The runtime 
performance of software and binary installations do not differ notably.

Installation using pip
----------------------

In addition to the Python interpreter, the following set of additional 
python modules is required in order to run Coquery:

* pandas 0.15.0 or later
* SQLAlchemy 1.0 or later
* PySide 1.2.0 or later OR PyQT4 4.11.0 or later

Python comes with an easy-to-use module installation system called ``pip``. 
In order to install Coquery and all required Python modules in a single step, 
open a command line and execute the following command::

    pip install numpy pandas sqlalchemy pyside coquery

Optional Python modules
=======================

If you use the software installation, you may want to install the following
optional Python packages to enable all features in Coquery. They are already
included in the binary installation.

* Matplotlib 1.4.0 or later (for visualizations)
* Seaborn 0.6.0 or later (for visualizations)
* PyMySQL 0.6.4 or later (for MySQL database connections)
* Natural Language Toolkit 3.0 or later (for automatic tagging and 
  lemmatization)

The following command installs these modules using ``pip``::

    pip install matplotlib seaborn pymysql nltk

MySQL server
============

There are two types of database connections: serverless connections and 
connections that communicate with a MySQL server. 

The default connection is a serverless one. No further software or additional 
configuration is required for this type of connections. With smaller corpora 
with about 1,000,000 to 10,000,000 word tokens, most queries will be completed
almost instantly if you are using a fairly recent computer. 

For larger corpora such as the BNC or COCA, the performance of serverless 
database connections may not be sufficient. If queries frequently take several 
seconds or even longer, a database connection using a MySQL server may be 
recommended.

A MySQL server is a computer program that reserves a proportion of the 
available system resources for running database queries in a highly 
performant way. Such a server can either reside on your own computer, or may 
be located externally on a different computer that is accessible over the 
network. With MySQL servers, very often the available system memory is the 
factor that delimits query performance most significantly, so installing a 
larger corpus such as COCA on an external computer with large memory 
capacities is strongly recommended. 

Using an external MySQL server has the additional advantage that the same 
corpus database on the server can be queried by separate installations of 
Coquery on different computers via the network. In this way, users do not 
have to allocate harddisk space and system resources to the corpus 
databases.

The configuration of MySQL connections and a guide to setting up a MySQL 
server is described in detail in :ref:`connections`.