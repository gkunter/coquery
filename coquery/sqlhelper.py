# -*- coding: utf-8 -*-
"""
sqlhelper.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import __init__

import os
import logging
import warnings
import sqlalchemy

try:
    logger = logging.getLogger(__init__.NAME)
except AttributeError:
    pass

from errors import *
from defines import *
import options

def _conf_dict(configuration):
    """
    Either retrieves a dictionary containing a pre-defined connection 
    configuration from the options module if 'configuration' is the name of a 
    connection configuration, or return 'configuration' if it is a dictionary 
    containing the values for a valid connection configuration.
    
    ValueError is raised if 'configuration' is a string, but if there is no 
    connection that has that name.
    
    ValueError is also raised if 'configuration' is a dictionary, but if it 
    does not contain the required values for a configuration.
    
    An SQLite configuration has to contain the following values:
        type:       SQL_SQLITE
        
    A MySQL configuration has to contain the following values:
        type:       SQL_MYSQL
        host:       str specifying the host name
        port:       int specifying the port number
        user:       str specifying the user name
        password:   str specifying the password

    Parameters
    ----------
    configuration : str or dict
        Either the name of a configuration, or a dictionary containing 
        configuration values
    
    Returns
    -------
    conf : dict 
        A dictionary containing configuration values
    """
    print(configuration, type(configuration))
    if isinstance(configuration, str):
        try:
            return options.cfg.server_configuration[configuration]
        except KeyError:
            raise ValueError
    elif isinstance(configuration, tuple):
        if len(configuration) != 5:
            raise ValueError
        return dict(zip(["host", "port", "type", "user", "password"], configuration))
        
    elif isinstance(configuration, dict):
        t = configuration.get("type")
        if not t:
            raise ValueError
        if t == SQL_MYSQL:
            if "host" not in configuration:
                raise ValueError
            if "port" not in configuration:
                raise ValueError
            if "user" not in configuration:
                raise ValueError
            if "password" not in configuration:
                raise ValueError
        return configuration

def test_configuration(name):
    """
    Tests if the specified SQL configuration is available.
    
    This method retrieves the database information for the given configuration,
    and tries to make a configuration to the database system.
    
    For SQLite configurations, it will return True if the given database path 
    can be both read and written to, and otherwise False.
    
    For MySQL configurations, it will attempt to open a connection to the 
    MySQL server using the stored MySQL connection data, and run a version 
    query on the server. It will return True if the version is correctly 
    returned by the server, or False otherwise.
    
    Parameters
    ----------
    name : str or dict
        The name of the configuration that is to be tested, or a dictionary 
        containing the required values.

    Returns
    -------
    test : bool
        Returns True if the configuration is working, or False otherwise.
    """
    d = _conf_dict(name)
    if d["type"] == SQL_MYSQL:
        try:
            engine = sqlalchemy.create_engine(sql_url(name))
            with engine.connect() as connection:
                connection.execute("SELECT VERSION()")
        except sqlalchemy.exc.SQLAlchemyError as e:
            return False
        except Exception as e:
            raise e
        else:
            return True

    elif d["type"] == SQL_SQLITE:
        return os.access(sqlite_path(name), os.X_OK | os.R_OK)

def sql_url(configuration, db_name=""):
    """
    Return a SQLAlchemy engine url for the given configuration.
    
    Parameters
    ----------
    configuration : str or dict
        The name of the configuration that is to be used, or a dictionary 
        containing the required values.
    db_name : str 
        The name of a database. Can be empty if no specific database is 
        requested.
        
    Returns
    -------
    url : str
        A string containing a SQLAlchemy engine url that can be used to 
        create a database engine using create_engine().        
    """
    d = _conf_dict(configuration)

    if d["type"] == SQL_MYSQL:
        return "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4".format(
            host=d["host"], port=d["port"], user=d["user"], password=d["password"],
            db_name=db_name)
    elif d["type"] == SQL_SQLITE:
        return "sqlite+pysqlite:///{}".format(sqlite_path(configuration, db_name))

def sqlite_path(configuration, db_name=None):
    """
    Return the path to the specified SQLite database, or the directory that 
    contains the SQLite databases if no database name is specified.
    
    Parameters
    ----------
    configuration : str 
        The name of the configuration to use
    db_name : str 
        The name of a database. Can be empty if no specific database is 
        requested.
        
    Returns
    -------
    path : str
        The path pointing either directly to the database, or to the
        directory in which databases are stored.
    """
    if db_name:
        return os.path.join(options.get_home_dir(), "databases", configuration, "{}.db".format(db_name))
    else:
        return os.path.join(options.get_home_dir(), "databases", configuration)

def drop_database(configuration, db_name):
    """
    Drops the database 'db_name' from the given configuration.
    
    Parameters
    ----------
    configuration : str 
        The name of the configuration to use.
    db_name : str 
        The name of a database.
    """
    engine = sqlalchemy.create_engine(sql_url(configuration, db_name))
    
    if engine.dialect.name == SQL_MYSQL:
        with engine.connect() as connection:
            text = 'DROP DATABASE {}'.format(db_name)
            connection.execute(text)
    elif engine.dialect.name == SQL_SQLITE:
        os.remove(sqlite_path(configuration, db_name))

def has_database(configuration, db_name):
    """
    Test if the database 'db_name' exists in the given configuration.
    
    Parameters
    ----------
    configuration : str 
        The name of the configuration to use.
    db_name : str 
        The name of a database.
        
    Returns
    -------
    b : bool 
        True if the database exists, or False otherwise.
    """
    engine = sqlalchemy.create_engine(sql_url(configuration, db_name))
    if engine.dialect.name == SQL_MYSQL:
        results = engine.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'".format(db_name))
        return len(results) > 0
    elif engine.dialect.name == SQL_MYSQL:
        return os.path.exists(sqlite_path(configuration, db_name))
    