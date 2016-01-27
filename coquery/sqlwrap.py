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
    def __init__(self, Host, Port, Type, User, Password, db_name=None, db_path="", encoding="utf8", connect_timeout=60, local_infile=0):
        
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
        self.local_infile = local_infile

        self.Con = self.get_connection()

        if self.db_type == SQL_MYSQL:
            self.set_variable("NAMES", self.encoding)

    def create_database(self, db_name):
        if self.db_type == SQL_MYSQL:
            cur = self.Con.cursor()
            cur.execute("CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(db_name.split()[0]))
        elif self.db_type == SQL_SQLITE:
            # SQLite databases are created when making a connection to them
            pass

    def use_database(self, db_name):
        if self.db_type == SQL_MYSQL:
            cur = self.Con.cursor()
            cur.execute("USE {}".format(db_name.split()[0]))
        elif self.db_type == SQL_SQLITE:
            self.db_path = SqlDB.sqlite_path(db_name)
        self.Con = self.get_connection()

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
                        local_infile=self.local_infile,
                        charset=self.encoding)
                else:
                    connection = pymysql.connect(
                        host=self.db_host, 
                        port=self.db_port, 
                        user=self.db_user, 
                        passwd=self.db_pass, 
                        connect_timeout=self.timeout,
                        local_infile=self.local_infile,
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

    def has_database(self, db_name):
        """
        Check if the database 'db_name' exists on the current connection.
        
        Parameters
        ----------
        db_name : str 
            The name of the database 
            
        Returns
        -------
        b : bool 
            True if the database exists, or False otherwise.
        """
        if self.db_type == SQL_MYSQL:
            cur = self.Con.cursor()
            cur.execute("SHOW DATABASES")
            try:
                for x in cur:
                    if x[0] == db_name.split()[0]:
                        return db_name
            except pymysql.ProgrammingError as ex:
                warning.warn(ex)
                if cur:
                    warning.warn(cur.messages)
                else:
                    warning.warn(self.Con.messages)
            return False
        elif self.db_type == SQL_SQLITE:
            return os.path.exists(SqlDB.sqlite_path(db_name))

    def has_table(self, table_name):
        """
        Check if the table 'table_name' exists in the current database.
        
        Parameters
        ----------
        table_name : str 
            The name of the table
            
        Returns
        -------
        b : bool 
            True if the table exists, or False otherwise.
        """
        cur = self.Con.cursor()
        if self.db_type == SQL_MYSQL:
            return bool(con.execute("SELECT * FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}'".format(self.db_name, table_name)))
        elif self.db_type == SQL_SQLITE:
            S = "SELECT * from sqlite_master WHERE type = 'table' and name = '{}'".format(table_name)
            return bool(cur.execute(S).fetchall())

    def create_table(self, table_name, description):
        """
        Create a new table 'table_name' using the specification from
        'description'.
        
        Parameters
        ----------
        table_name : str 
            The name of the new table 
        description : str 
            The SQL string used to create the new table
        """
        cur = self.Con.cursor()
        return cur.execute('CREATE TABLE {} ({})'.format(table_name, description))

    def find(self, table_name, values, additional_variables=[], case=False):
        """ 
        Obtain all records from table_name that match the column-value
        pairs given in the dict values.
        
        Parameters
        ----------
        table_name : str 
            The name of the table 
        values : dict 
            A dictionary with column names as keys and cell contents as values
        additional_variables : list
            Not supported anymore
        case : bool
            Set to True if the find should be case-sensitive, or False 
            otherwise.
            
        Returns
        -------
        l : list of tuples 
            A list of tuples, each representing a row from the data table 
            that match the provided values
        """
        assert additional_variables == [], "Parameter 'additional_variables' is no longer supported by DB.find()"
        
        if self.db_type == SQL_MYSQL:
            cur = self.Con.cursor(pymysql.cursors.DictCursor)
        elif self.db_type == SQL_SQLITE:
            con = self.Con
            con.row_factory = sqlite3.Row
            cur = con.cursor()
        variables = list(values.keys()) + additional_variables
        where = []
        for column, value in values.items():
            where.append('{} = "{}"'.format(column, str(value).replace('"', '""')))
        if case:
            S = "SELECT {} FROM {} WHERE BINARY {}".format(", ".join(variables), table_name, " AND BINARY ".join(where))
        else:
            S = "SELECT {} FROM {} WHERE {}".format(", ".join(variables), table_name, " AND ".join(where))
        S = S.replace("\\", "\\\\")
        try:
            cur.execute(S)
        except Exception as e:
            print(e)
            raise e
        return cur.fetchall()
        
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
            cur.execute("SET {} '{}'".format(variable, value))
        else:
            cur.execute("SET {}={}".format(variable, value))

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
            con.row_factory = dict_factory
            cursor = con.cursor()
        cursor.execute(S)
        return cursor

    def get_field_type(self, table_name, column_name):
        """
        Obtain the current SQL field type for the specified column.
        
        Parameters
        ----------
        table_name, column_name : str 
            The name of the table and the column, respectively
            
        Returns
        -------
        s : str 
            A string containing the current SQL field type for the specified 
            column.
        """
        cur = self.Con.cursor()
        if self.db_type == SQL_MYSQL:
            S = "SHOW FIELDS FROM %s WHERE Field = '%s'" % (table_name, column_name)
            cur.execute(S)
            Results = cur.fetchone()
            try:
                if isinstance(Results, bytes):
                    Results = Results.decode("utf-8")
            except NameError:
                Results = str(Results)
            if Results:
                field_type = Results[1]
                if Results[2] == "NO":
                    field_type += " NOT NULL"
                return str(field_type)
            else:
                return None
            
        elif self.db_type == SQL_SQLITE:
            S = "PRAGMA table_info({})".format(table_name)
            cur.execute(S)
            for row in cur:
                result = dict(zip("cid", "name", "type", "notnull", "dflt_value", "pk"),
                              row)
                column = result["name"]
                data_type = result["type"]
                not_null = result["notnull"]
                if column == column_name:
                    if not_null:
                        return "{} NOT NULL".format(data_type)
                    else:
                        return str(data_type)

    def get_optimal_field_type(self, table_name, column_name):
        """
        Obtain the optimal field type for the specified column.
        
        This method is not supported for SQLite databases. Here, the return 
        value is always the current field type of the column.
        
        Parameters
        ----------
        table_name, column_name : str 
            The name of the table and the column, respectively
            
        Returns
        -------
        s : str 
            A string containing the optimal SQL field type for the specified 
            column.
        """
        if self.db_type == SQL_SQLITE:
            return self.get_field_type(table_name, column_name)
        cur = self.Con.cursor()
        cur.execute("SELECT %s FROM %s PROCEDURE ANALYSE()" % (column_name, table_name), override=True)
        x = cur.fetchone()[-1]
        try:
            if isinstance(x, bytes):
                x = x.decode("utf-8")
        except NameError:
            x = str(x)
        return x
        
    def modify_field_type(self, table_name, column_name, new_type):
        """
        Change the field type of the specified column to the new type.
        
        Parameters
        ----------
        table_name, column_name : str 
            The name of the table and the column, respectively
        new_type : str 
            A string containing the new SQL field type for the specified 
            column.
        """
        old_field = self.get_field_type(table_name, column_name)
        cur = self.Con.cursor()
        cur.execute("ALTER TABLE %s MODIFY %s %s" % (table_name, column_name, new_type))
        if options.cfg.verbose:
            logger.info("ALTER TABLE %s MODIFY %s %s" % (table_name, column_name, new_type))

    def has_index(self, table_name, index_name):
        """
        Check if the specified column has an index.
        
        Parameters
        ----------
        table_name, column_name : str 
            The name of the table and the column, respectively
            
        Returns
        -------
        b : bool 
            True if the column has an index, or False otherwise.
        """
        cur = self.Con.cursor()
        if self.db_type == SQL_MYSQL:
            return bool(cur.execute('SHOW INDEX FROM %s WHERE Key_name = "%s"' % (table_name, index_name)))
        elif self.db_type == SQL_SQLITE:
            cur.execute("SELECT name FROM sqlite_master WHERE type = 'index' AND name = '{}' AND tbl_name = '{}'".format(index_name, table_name))
            return bool(len(cur.fetchall()))
    
    def get_index_length(self, table_name, column_name, coverage=0.95):
        """
        Return the index length that is required for the given coverage.
        
        If the current SQL engine is SQL_SQLITE, this method always returns
        None.
        
        Parameters
        ----------
        table_name, column_name : str 
            The name of the table and the column, respectively
            
        coverage : float
            The coverage percentage that the index should cover. Default: 0.95
        
        Returns
        -------
        number : int 
            The first character length that reaches the given coverage, or 
            None if the coverage cannot be reached.
        """
        
        if self.db_type == SQL_SQLITE:
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
            table=table_name, column=column_name)
        cur = self.Con.cursor()
        cur.execute(S)
        max_c = None
        for x in cur:
            if not max_c or x[3] > max_c[3]:
                max_c = x
            if x[3] >= coverage:
                print("{}.{}: index length {}".format(table_name, column_name, x[0]))
                logger.info("{}.{}: index length {}".format(table_name, column_name, x[0]))
                return int(x[0])
        if max_c:
            print("{}.{}: index length {}".format(table_name, column_name, max_c[0]))
            logger.info("{}.{}: index length {}".format(table_name, column_name, max_c[0]))
            return int(max_c[0])
        return None
    
    def create_index(self, table_name, index_name, variables, index_length=None):
        """
        Create an index for the specified column table.
        
        Parameters
        ----------
        table_name : str 
            The name of the table
            
        index_name : str 
            The name of the new index
            
        variables : list 
            A list of strings representing the column names that are to be 
            indexed.
            
        index_length : int or None
            The length of the index (applies to TEXT or BLOB fields)
        """
        cur = self.Con.cursor()

        # Do not create an index if the table is empty:
        cur.execute("SELECT * FROM {} LIMIT 1".format(table_name))
        if not cur.fetchone():
            return
        
        if index_length:
            variables = ["%s(%s)" % (variables[0], index_length)]
        S = 'CREATE INDEX {} ON {}({})'.format(
            index_name, table_name, ",".join(variables))
        cur.execute(S)

    def start_transaction(self):
        if self.db_type == SQL_MYSQL:
            cur = self.Con.cursor()
            cur.execute("START TRANSACTION")

    def executemany(self, s, d):
        cur = self.Con.cursor()
        if self.db_type == SQL_SQLITE:
            s = s.replace("%s", "?")
        cur.executemany(s, d)

    def execute(self, S):
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
