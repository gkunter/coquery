.. title:: Coquery Documentation: Connections

.. _connections:

Database connections
====================

When you start Coquery, the 'Default' database connection is already be set
up for you. Using this 'Default' connection enables you to install new
corpora, and to run queries afterwards.

For most users, the 'Default' connection may already sufficient. However, you
may want to use a different location on your computer to store the corpus
database tables, for instance because they consume too much disk space or
because you want to use a faster disk drive than the default drive in order to
speed up the corpus queries. In addition, Coquery is able to take connect to
MySQL database servers which, among other benefits, can grant shared access to
the corpus data so that users don't have to install large corpora on their
own computers.

For these purposes, you can create a new database connection in the 'Database
connections' dialog from the 'Options' menu. If you have more than one
database connection, you can switch between them by using the Connection combo
box in the lower right corner of the main screen.

Note that with regard to the set of installed corpora, each database
connection is independent of each other. This means that if you want to use
the same corpus with different database connections, you have to install that
corpus separately using each database connection. Consequently, a corpus that
is installed on one database connection is not available if you switch to a
different database connection, unless you installed that corpus for that
database connection also.

The 'Default' connection
++++++++++++++++++++++++

The 'Default' connection uses a database system that requires no additional
configuration or installation, and which can therefore be used on every
computer regardless of the overall setup. The directory where the corpus
databases are stored depends on your operating system. The following paths are
all relative to your user's main directory:

* On Windows: APPDATA/Coquery/connections/Default/databases
* On MacOS: Library/Application support/Coquery/connections/Default/databases
* On Linux: either .config/Coquery/connections/Default/databases or
  $XDG_CONFIG_HOME/Coquery/connections/Default/databases

You can view the database directory that is used by the 'Default' connection
by selecting 'Default' in the list of available connections to the left of the
'Database connections dialog. The database directory is now shown to the
right.

The 'Default' connection cannot be modified or deleted, which means that it
will always be available to Coquery as a fallback option. In other words, the
'Default' connection will ensure that there is always at least one working
database connection available that Coquery can use to store and query corpora.

Using a different storage location
++++++++++++++++++++++++++++++++++

If you want to use a different location where Coquery stores the corpus databases, you can create a new database connection in the Database connection dialog. In order to do so, first select 'New connection...' in the list of
available connections to the left of the dialog.

Now, enter a valid connection name in the first field to the right. Valid
connection names may contain only upper or lower case latin letters, numbers,
and the underscore character '_'. Make sure that 'Use MySQL server' is set to
'No'.

If you want to use a different database directory for the new connection,
click on the 'Browse' button and select the directory that you want the
connection to use. If you have correctly selected the database directory, you
can click the 'Add' button to add the database connection to the list of
available connections to the left of the dialog.

As it is not possible to move corpora from one connection to another, you will
first have to install the corpora that you wish to store in the new directory
by using the Corpus manager.

MySQL connections
+++++++++++++++++

MySQL connections connect to a MySQL server. Using a MySQL connection can have
performance advantages over using a serverless connection: MySQL servers may
be hosted on very powerful computers, and may therefore respond much faster to
corpus queries. However, setting up a MySQL connection is more technical than
a serverless connection. This section describes the steps required to set up a
MySQL connection.

There are two ways of using MySQL connections: either by connecting to a local
MySQL server (i.e. a server that is installed on the user's computer), or by
connecting to a remote MySQL server (i.e. a server that can be accessed via
the internet).

Setting up a local MySQL server
-------------------------------

Coquery can connect to a local MySQL server (or compatible). MySQL is
considered to be fast and reliable, and it is also available as Open Source
software. An alternative server is MariaDB.

The MySQL homepage provides download instructions and installation guides for Windows, Mac OS X, and Linux computers. Follow the steps described on the page
`Get Started with MySQL <https://dev.mysql.com/usingmysql/get_started.html>`_
from the MySQL website to install a MySQL server.

During the installation, you will have to create a MySQL root user. Keep a
note of the root user name and password that you select for the root user. If
you have modified the port number of the MySQL server during the installation,
also keep note of the new port number.

Using a remote MySQL server
---------------------------

If you wish to use a remote MySQL server, i.e. to connect to a MySQL server
via a network (usually the internet), you require to obtain the following information:

* URL or IP address of the database server
* Port number of the database server
* Name of a database user account that can be used by Coquery
* Password of that database user account

If you do not know how to obtain this information, or if you are unsure
whether a suitable database user account exists on the remote MySQL server
that can be used by Coquery, please consult the administrator in charge of the
MySQL server. They may want to discuss with you which MySQL privileges have to
be granted to the database user. The set of privileges determines which corpus
operations can be performed by Coquery. The following overview will help you
to determine which privileges will be required:

* To query existing corpora: SELECT, INSERT
* To install new corpora: ALTER, CREATE, INDEX, INSERT, SELECT
* To remove or reinstall existing corpora: DROP

Creating a new MySQL connection
-------------------------------

Once you have a MySQL server installed on your computer, or have collected
the required information for a remote MySQL server, open the 'Database
connections' dialog from the 'Options' menu, and select 'New connection...'
from the list to the left.

Now, enter a valid connection name in the first field to the right. Valid
connection names may contain only upper or lower case latin letters, numbers,
and the underscore character '_'.

Next, set 'Use MySQL server' to 'Yes', and select an appropriate server location:

* Select 'Local server on this computer' if your MySQL server is installed on
  your own PC.
* If you want to use a remote MySQL server, select 'URL or IP address'.

The default port number of MySQL servers is 3306. If you have modified the
port number during the installation of your local MySQL server, or if the
remote server uses a different port number, change the number accordingly.

Finally, enter the user credentials for the database user account:

* If you use a remote MySQL server, enter the database user name and password
  that you have received from the server administrator.
* If you use a local server, enter the MySQL root user name and the password
  that you have selected during the installation.

If the information that you have entered was correct, the connection status
will indicate a successful connection to the MySQL server. You can now click
on the 'Add' button to add the database connection to the list of available
connections to the left of the dialog.

Checking the connection status
------------------------------

If you have entered the correct user credentials, and if your local or remote
MySQL server is responding correctly, the connection status indicator should
be lit in green, and a text should be displayed in the 'Connection status'
view that confirms that you have successfully established a connection to the
server.

A red connection status indicator is shown if there is an error in the current
MySQL server configuration. Please check whether you have entered a valid URL
or IP address. The error message in the 'Connection status' view may help you
to narrow down the cause of the error.

If the connection status indicator is lit in yellow, this means that Coquery
could find a MySQL server, but that the attempt to connect to the server was
unsuccessful. Please verify that the user name and the password that you have
entered are valid. Also ensure that the port number is correct.

Selecting, modifying, and removing database connections
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

To the left of the Database connections dialog, there is a list of all
available database connections. If you want to create a new database
connection, select the entry 'New connection...' on the bottom of the list.

Note that all changes to the list of available database connections will be
ignored if you close the Database connections dialog by clicking the 'Cancel'
button. The changes you have made will only become active if you close the
dialog by clicking the 'Ok' button.

If you want to change the settings of an existing database connection, select
the name of the connection, and the current settings for that connection will
be shown on the right of the dialog. You can now modify these settings. The
selected connection will immediately be updated with the changes you make.

If you wish to remove a database connection from the list of available
connections, select the name of the connection. Discard this connection by
clicking the 'Remove' button.

If you want to switch from one database connection to another, simply select
the name of the connection that you want to use. Alternatively, you can close
the Database connections dialog and select a database connection from the
Connections combo box in the lower right corner of the main screen.
