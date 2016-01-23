# -*- coding: utf-8 -*-
"""
sqlwrap.py is part of Coquery.

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

try:
    logger = logging.getLogger(__init__.NAME)
except AttributeError:
    pass

from errors import *
from defines import *
import options

import sqlite3
if options._use_mysql:
    import pymysql
    import pymysql.cursors

class SqlDB (object):
    """ A wrapper for MySQL. """
    def __init__(self, Host, Port, Type, User, Password, db_name=None, db_path="", encoding="utf8", connect_timeout=60):
        
        if Type == SQL_MYSQL and not options._use_mysql:
            raise DependencyError("pymysql", "https://github.com/PyMySQL/PyMySQL")
        
        self.Con = None
        self.db_type = Type
        self.db_name = db_name
        self.db_host = Host
        self.db_port = Port
        self.db_user = User
        self.db_pass = Password
        self.db_path = db_path
        self.timeout = connect_timeout
        self.encoding = encoding

        self.Con = self.get_connection()

        if self.db_type == SQL_MYSQL:
            self.set_variable("NAMES", self.encoding)

    def get_connection(self):
        if self.db_type not in SQL_ENGINES:
            raise RuntimeError("Database type '{}' not supported.".format(self.db_type))
        elif self.db_type == SQL_MYSQL:
            try:
                if self.db_name:
                    connection = pymysql.connect(
                        host=self.db_host, 
                        port=self.db_port, 
                        user=self.db_user, 
                        passwd=self.db_pass, 
                        db=self.db_name,
                        connect_timeout=self.timeout,
                        charset=self.encoding)
                else:
                    connection = pymysql.connect(
                        host=self.db_host, 
                        port=self.db_port, 
                        user=self.db_user, 
                        passwd=self.db_pass, 
                        connect_timeout=self.timeout,
                        charset=self.encoding)
            except (pymysql.Error) as e:
                raise SQLInitializationError(e)
        elif self.db_type == SQL_SQLITE:
            if self.db_name:
                if not self.db_path:
                    self.db_path = os.path.join(options.get_home_dir(), "databases", "{}.db".format(self.db_name))
                connection = sqlite3.connect(self.db_path)
            else:
                raise SQLInitializationError("SQLite requires a database name")
        else:
            raise RuntimeError("Database type '{}' not supported.".format(self.db_type))
        return connection

    @staticmethod
    def sqlite_path(db_name):
        return os.path.join(options.get_home_dir(), "databases", "{}.db".format(db_name))

    @staticmethod
    def test_connection(host, port, user, password, connect_timeout=60):
        """
        Tests if the specified MySQL connection is available.
        
        This method attempts to create a connection to the MySQL server using
        the host, port, user name, and password as provided as arguments.
        
        Parameters
        ----------
        host : string
            The host name or IP address of the host
        port : int 
            The MySQL port on the host server
        user : string 
            The name of the MySQL user 
        password : string 
            The password of the MySQL user
            
        Returns
        -------
        test : bool
            Returns True if a connection could be created, or False otherwise.
        """
        try:
            con = pymysql.connect(
                host=host, 
                port=port, 
                user=user, 
                passwd=password,
                connect_timeout=connect_timeout)
        except pymysql.Error as e:
            return False
        else:
            con.close()
        return True

    def kill_connection(self):
        try:
            self.Con.kill(self.Con.thread_id())
        except (pymysql.OperationalError, pymysql.InternalError):
            pass

    def set_variable(self, variable, value):
        cur = self.Con.cursor()
        try:
            string_classes = (str, unicode)
        except NameError:
            string_classes = (str)
        if isinstance(value, string_classes):
            self.execute("SET {} '{}'".format(variable, value))
        else:
            self.execute("SET {}={}".format(variable, value))

    def close(self):
        try:
            self.Con.close()
        except (pymysql.ProgrammingError, pymysql.Error):
            pass
        
    def explain(self, S):
        """
        Explain a MySQL query.
        
        The output of the EXPLAIN command is formatted as a table, and then
        logged to the logger as an INFO.
        
        Parameters
        ----------
        S : string
            The MySQL string to be explained.
        """
        command = S.partition(" ")[0].upper()
        if command in ["SHOW", "DESCRIBE", "SET", "RESET"]:
            return
        try:
            cur = self.Con.cursor()
            cur.execute("EXPLAIN %s" % S)
        except pymysql.ProgrammingError as e:
            raise SQLProgrammingError(S + "\n"+ "%s" % e)
        else:
            explain_table = cur
            explain_table_rows = [[x[0] for x in explain_table.description]]
            for x in explain_table:
                explain_table_rows.append([str(y) for y in x])
                
            explain_column_width = [len(x[0]) for x in explain_table.description]
            for current_row in explain_table_rows:
                for i in range(len(current_row)):
                    explain_column_width[i] = max(explain_column_width[i], len(current_row[i]))
                    
            format_string = " | ".join (["%%-%is" % x for x in explain_column_width])
            line_string = "-" * (sum (explain_column_width) - 3 + 3 * len(explain_column_width))
            
            log_rows = ["EXPLAIN %s" % S]
            log_rows.append(line_string)
            log_rows.append(format_string % tuple(explain_table_rows [0]))
            log_rows.append(line_string)
            for x in explain_table_rows[1:]:
                log_rows.append(format_string % tuple(x))
            log_rows.append(line_string)
            logger.debug("\n".join(log_rows))

    def execute_cursor(self, S, server_side=False):
        def dict_factory(cursor, row):
            d = {}
            for i, column in enumerate(cursor.description):
                d[column[0]] = row[i]
            return d

        S = S.strip()
        if options.cfg.explain_queries:
            self.explain(S)
        logger.debug(S)

        if self.db_type == SQL_MYSQL:
            if server_side:
                cursor = self.Con.cursor(pymysql.cursors.SSDictCursor)
            else:
                cursor = self.Con.cursor(pymysql.cursors.DictCursor)
        elif self.db_type == SQL_SQLITE:
            con = self.get_connection()
            con.row_factory = sqlite3.Row
            cursor = con.cursor()
        cursor.execute(S)
        return cursor
    
    def executemany(self, S, data):
        cur = self.Con.cursor()
        cur.executemany(S, data)
    
    def execute(self, S):
        """
Call        execute(self, S, ForceExecution=False)
Summary     Executes the SQL command string provided in S, or pretend to do 
            so if options.cfg.dry_run is True and the SQL command is a modifying 
            command. The parameter ForceExecution can be used to override 
            options.cfg.dry_run.
            if options.cfg.ExplainQueries is True, an SQL EXPLAIN command will be
            executed as well, and the output will be displayed.
Value       no return value
        """
        S = S.strip()
        if options.cfg.explain_queries:
            self.explain(S)
        logger.debug(S)
        try:
            cur = self.Con.cursor()
            cur.execute(S)
        except pymysql.Error as e:
            warnings.warn(str(e))
            raise e

    def commit(self):
        self.Con.commit()
        
    def rollback(self):
        self.Con.rollback()

    def start_read_only(self):
        cur = self.Con.cursor()
        cur.execute("START TRANSACTION READ ONLY")
        
    def get_database_size(self, database_name):
        """ Returns the size of the database in bytes."""
        if self.db_type == SQL_MYSQL:
            cur = self.Con.cursor()
            cur.execute("SELECT data_length+index_length FROM information_schema.tables WHERE table_schema = '{}'".format(database_name))
            return cur.fetchone()[0]
        elif self.db_type == SQL_SQLITE:
            return os.path.getsize(self.sqlite_path(database_name))

    def drop_database(self, database_name):
        if self.db_type == SQL_MYSQL:
            cur = self.Con.cursor()
            cur.execute("DROP DATABASE {}".format(database_name.split()[0]))
        elif self.db_type == SQL_SQLITE:
            os.remove(self.sqlite_path(database_name))
