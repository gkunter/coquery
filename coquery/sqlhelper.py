# -*- coding: utf-8 -*-
"""
sqlhelper.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os
import logging
import sqlalchemy

from .defines import SQL_MYSQL, SQL_SQLITE, DEFAULT_CONFIGURATION
from . import options


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
    test : tuple
        A tuple, with a boolean value as first element and an Exception as
        the second element.

        If the configuration is valid, the boolean value is True, and the
        second element is the value of the query ``SELECT VERSION()``.

        If the configuration is not valid, the boolean value is False, and
        the second element is the exception that was raised when testing
        the connection.
    """
    connection = options.cfg.connections[name]
    return connection.test()


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
    connection = options.cfg.connections[configuration]
    return connection.url(db_name)


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
    connection = options.cfg.connections[name]

    if db_name:
        return os.path.join(connection.path, "{}.db".format(db_name))
    else:
        return connection.path


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
    s = sql_url(configuration, db_name)
    engine = sqlalchemy.create_engine(s)

    if engine.dialect.name == SQL_MYSQL:
        with engine.connect() as connection:
            text = 'DROP DATABASE {}'.format(db_name)
            connection.execute(text)
    elif engine.dialect.name == SQL_SQLITE:
        os.remove(sqlite_path(configuration, db_name))
    engine.dispose()


def create_database(configuration, db_name):
    s = sql_url(configuration)
    engine = sqlalchemy.create_engine(s)
    if engine.dialect.name == SQL_MYSQL:
        with engine.connect() as connection:
            S = """
                CREATE DATABASE {}
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
                """.format(db_name.split()[0])
            connection.execute(S)
    engine.dispose()


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
        S = """
            SELECT SCHEMA_NAME
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME = '{}'
            """.format(db_name)
        try:
            engine.execute(S)
        except sqlalchemy.exc.InternalError as e:
            return False
        except Exception as e:
            raise e
        else:
            return True
    elif engine.dialect.name == SQL_SQLITE:
        return os.path.exists(sqlite_path(configuration, db_name))


def create_index(engine, table, index, variables, length=None):
    """
    Create an index for the specified column table.

    Parameters
    ----------
    engine : an SQLAlchemy engine

    table : str
        The name of the table

    index : str
        The name of the new index

    variables : list
        A list of strings representing the column names that are to be
        indexed.

    length : int or None
        The length of the index (applies to TEXT or BLOB fields)
    """

    with engine.connect() as connection:
        # Do not create an index if the table is empty:
        S = "SELECT * FROM {} LIMIT 1".format(table)
        if not connection.execute(S).fetchone():
            return

        if length:
            variables = ["%s(%s)" % (variables[0], length)]
        S = 'CREATE INDEX {} ON {}({})'.format(
            index, table, ",".join(variables))
        connection.execute(S)


def get_index_length(engine, table, column, coverage=0.95):
    """
    Return the index length that is required for the given coverage.

    If the current SQL engine is SQL_SQLITE, this method always returns
    None.

    Parameters
    ----------
    table, column : str
        The name of the table and the column, respectively

    coverage : float
        The coverage percentage that the index should cover. Default: 0.95

    Returns
    -------
    number : int
        The first character length that reaches the given coverage, or
        None if the coverage cannot be reached.
    """

    if engine.name == SQL_SQLITE:
        return None

    S = """
    SELECT len,
        COUNT(DISTINCT SUBSTR({column}, 1, len)) AS number,
        total,
        ROUND(COUNT(DISTINCT SUBSTR({column}, 1, len)) / total, 2) AS coverage
    FROM   {table}
    INNER JOIN (
        SELECT COUNT(DISTINCT {column}) total
        FROM   {table}
        WHERE  {column} != "") count_total
    INNER JOIN (
        SELECT @x := @x + 1 AS len
        FROM   {table}, (SELECT @x := 0) count_init
        LIMIT  32) count_inc
    GROUP BY len""".format(
        table=table, column=column)

    with engine.connect() as connection:
        results = connection.execute(S)

    max_c = None
    for x in results:
        if not max_c or x[3] > max_c[3]:
            max_c = x
        if x[3] >= coverage:
            print("{}.{}: index length {}".format(table, column, x[0]))
            logging.info("{}.{}: index length {}".format(table, column, x[0]))
            return int(x[0])
    if max_c:
        print("{}.{}: index length {}".format(table, column, max_c[0]))
        logging.info("{}.{}: index length {}".format(table, column, max_c[0]))
        return int(max_c[0])
    return None
