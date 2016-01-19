"""
dbconnection.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License. A 
Coquery exception applies under GNU GPL version 3 section 7.

For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>. For the Coquery 
exception, see <http://www.coquery.org/license/>.
"""

from __future__ import unicode_literals 
from __future__ import print_function

try:
    str = unicode
except NameError:
    pass

import warnings
import copy
from collections import defaultdict
import sqlite3

import pymysql as mysql
import pymysql.cursors as mysql_cursors

from defines import *
import options
import logging

verbose = False
name = ""
logger = None

insert_cache = defaultdict(list)

class DBConnection(object):
    def __init__(self, db_user="mysql", db_host="localhost", db_type="mysql", db_port=3306, db_pass="mysql", local_infile=0, encoding="utf8", db_path=""):
        self.db_type = db_type
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_passwd = db_pass
        self.db_path = None
        self.db_name = None
        self._encoding = encoding

        if db_type == SQL_MYSQL:
            self._con = mysql.connect(
                host=db_host, 
                user=db_user, 
                passwd=db_pass,
                port=db_port,
                local_infile=local_infile, 
                charset=encoding)

            self.set_variable("NAMES", encoding)
            self.set_variable("CHARACTER SET", encoding)
            self.set_variable("autocommit", 0)
            self.set_variable("unique_checks", 0)
            self.set_variable("foreign_key_checks", 0)
        elif db_type == SQL_SQLITE:
            self._con = None
        else:
            raise RuntimeError("Database type '{}' not supported.".format(db_type))

    def Con(self):
        if self.db_type == SQL_MYSQL:
            return self._con
        elif self.db_type == SQL_SQLITE:
            if not self._con:
                self._con = sqlite3.connect(self.db_path)
            return self._con

    @staticmethod
    def sqlite_path(db_name):
        return os.path.join(options.get_home_dir(), "databases", "{}.db".format(db_name))

    def start_transaction(self):
        if self.db_type == SQL_MYSQL:
            cur = self.Con().cursor()
            self.execute(cur, "START TRANSACTION")

    def has_database(self, database_name):
        if self.db_type == SQL_MYSQL:
            cur = self.Con().cursor()
            self.execute(cur, "SHOW DATABASES")
            try:
                for x in cur:
                    if x[0] == database_name.split()[0]:
                        return database_name
            except mysql.ProgrammingError as ex:
                warning.warn(ex)
                if cur:
                    warning.warn(cur.messages)
                else:
                    warning.warn(self.Con().messages)
            return False
        elif self.db_type == SQL_SQLITE:
            return os.path.exists(DBConnection.sqlite_path(database_name))
        else:
            raise Exception

    def create_database(self, database_name):
        if self.db_type == SQL_MYSQL:
            cur = self.Con().cursor()
            self.execute(cur, "CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(database_name.split()[0]))
        elif self.db_type == SQL_SQLITE:
            # SQLite databases are created when making a connection to them
            pass

    def use_database(self, database_name):
        if self.db_type == SQL_MYSQL:
            cur = self.Con().cursor()
            self.execute(cur, "USE {}".format(database_name.split()[0]))
        elif self.db_type == SQL_SQLITE:
            self.db_path = DBConnection.sqlite_path(database_name)
        
    def drop_database(self, database_name):
        if self.db_type == SQL_MYSQL:
            cur = self.Con().cursor()
            self.execute(cur, "DROP DATABASE {}".format(database_name.split()[0]))
        elif self.db_type == SQL_SQLITE:
            os.remove(DBConnection.sqlite_path(database_name))
                      
    def load_infile(self, file_name, table_name, arguments):
        cur = self.Con().cursor()
        self.execute(cur, "LOAD DATA LOCAL INFILE '{}' INTO TABLE {} {}".format(file_name, table_name, arguments))

    def executemany(self, s, d):
        cur = self.Con().cursor()
        if self.db_type == SQL_SQLITE:
            s = s.replace("%s", "?")
        cur.executemany(s, d)

    def execute(self, cursor, command, override=False):
        if verbose:
            logger.info(command)
        try:
            return cursor.execute(command)
        except Exception as e:
            print(e)
            warnings.warn("An error occurred when executing MySQL command '{}'.".format(command))
            raise e

    def has_table(self, table_name):
        cur = self.Con().cursor()
        if self.db_type == SQL_MYSQL:
            return self.execute(cur, "SELECT * FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}'".format(self.db_name, table_name), override=True)
        elif self.db_type == SQL_SQLITE:
            S = "SELECT * from sqlite_master WHERE type = 'table' and name = '{}'".format(table_name)
            return self.execute(cur, S).fetchall()

    def load_data(self, table_name, path, arguments=""):
        cur = self.Con().cursor()
        return self.execute(cur, "LOAD DATA LOCAL INFILE '{}' INTO TABLE {} {}".format(path, table_name, arguments))

    def create_table(self, table_name, description, override=False):
        cur = self.Con().cursor()
        return self.execute(cur, 'CREATE TABLE {} ({})'.format(table_name, description), override=override)
    
    def drop_table(self, table_name):
        cur = self.Con().cursor()
        return self.execute(cur, 'DROP TABLE {}'.format(table_name))

    def has_index(self, table_name, index_name):
        cur = self.Con().cursor()
        if self.db_type == SQL_MYSQL:
            return self.execute(cur, 'SHOW INDEX FROM %s WHERE Key_name = "%s"' % (table_name, index_name), override=True)
        elif self.db_type == SQL_SQLITE:
            results = self.execute(cur, "SELECT name FROM sqlite_master WHERE type = 'index' AND name = '{}' AND tbl_name = '{}'".format(index_name, table_name))
            return len(results.fetchall())
    
    def get_index_length(self, table_name, column_name, coverage=0.95):
        """
        Return the index length that is required for the given coverage.
        
        If the current SQL engine is SQL_SQLITE, this method always returns
        None.
        
        Parameters
        ----------
        table_name : string
            The name of the table
        
        column_name : string
            The name of the column for which an index is to be created 
            
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
        cur = self.Con().cursor()
        self.execute(cur, S)
        max_c = None
        for x in cur.fetchall():
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
    
    def create_index(self, table_name, index_name, variables, index_type=None, index_length=None):
        cur = self.Con().cursor()

        # Do not create an index if the table is empty:
        self.execute(cur, "SELECT * FROM {} LIMIT 1".format(table_name))
        if not cur.fetchone():
            return
        
        if index_length:
            variables = ["%s(%s)" % (variables[0], index_length)]
        if index_type:
            S = 'CREATE INDEX {} ON {}({}) USING {}'.format(
                index_name, table_name, ",".join(variables), index_type)
        else:
            S = 'CREATE INDEX {} ON {}({})'.format(
                index_name, table_name, ",".join(variables))
        self.execute(cur, S)
            
    def get_field_type(self, table_name, column_name):
        cur = self.Con().cursor()
        if self.db_type == SQL_MYSQL:
            self.execute(cur, "SHOW FIELDS FROM %s WHERE Field = '%s'" % (table_name, column_name), override=True)
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
            self.execute(cur, S)
            for result in cur.fetchall():
                column = result["name"]
                data_type = result["type"]
                not_null = result["notnull"]
                if column == column_name:
                    if not_null:
                        return "{} NOT NULL".format(data_type)
                    else:
                        return str(data_type)
                    
    def get_optimal_field_type(self, table_name, column_name):
        if self.db_type == SQL_SQLITE:
            return self.get_field_type(table_name, column_name)
        cur = self.Con().cursor()
        self.execute(cur, "SELECT %s FROM %s PROCEDURE ANALYSE()" % (column_name, table_name), override=True)
        x = cur.fetchone()[-1]
        try:
            if isinstance(x, bytes):
                x = x.decode("utf-8")
        except NameError:
            x = str(x)
        return x
        
    def modify_field_type(self, table_name, column_name, new_type):
        cur = self.Con().cursor()
        old_field = self.get_field_type(table_name, column_name)
        self.execute(cur, "ALTER TABLE %s MODIFY %s %s" % (table_name, column_name, new_type))

    def read_table(self, table_name, FUN):
        cur = self.Con().cursor(MySQLdb.cursors.SSCursor)
        self.execute(cur, "SELECT * FROM %s" % table_name, override=True)
        D = {}
        for current_entry in cur.fetchall():
            try:
                x = FUN(current_entry)
            except UnicodeDecodeError as e:
                x = FUN([str(x).decode("utf-8") for x in current_entry])
            D[x] = current_entry
        return D

    def get_max(self, table_name, column_name):
        cur = self.Con().cursor()
        self.execute(cur, 'SELECT MAX(%s) FROM %s' % (column_name, table_name), override=True)
        try:
            return int(max(0, cur.fetchall() [0] [0]))
        except (TypeError, ValueError):
            return None

    def get_number_of_rows(self, table_name):
        cur = self.Con().cursor()
        self.execute(cur, 'SELECT COUNT(*) FROM %s' % (table_name), override=True)
        try:
            return int(max(0, cur.fetchall() [0] [0]))
        except TypeError:
            return None        

    def find(self, table_name, values, additional_variables=[], case=False):
        """ Obtain all records from table_name that match the column-value
        pairs given in the dict values."""
        if self.db_type == SQL_MYSQL:
            cur = self.Con().cursor(mysql_cursors.DictCursor)
        elif self.db_type == SQL_SQLITE:
            con = self.Con()
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
            self.execute(cur, S, override=True)
        except Exception as e:
            print(e)
            raise e
        return cur.fetchall()

    def insert(self, table_name, data):
        cur = self.Con().cursor()
        # take care of quote characters and backslashes:
        new_data = copy.copy(data)
        for x in new_data:
            new_data[x] = "%s" % str(new_data[x]).replace('"', '""')
            new_data[x] = new_data[x].replace("\\", "\\\\")

        S = "INSERT INTO {}({}) VALUES({})".format(
            table_name, 
            ",".join(new_data.keys()), 
            ",".join('"%s"' % x for x in new_data.values()))
        self.execute(cur, S)
        return self.Con().insert_id()

    def insert_id(self):
        return self.Con().insert_id()

    def set_variable(self, variable, value):
        if self.db_type == SQL_MYSQL:
            cur = self.Con().cursor()
            if isinstance(value, str):
                self.execute(cur, "SET {} '{}'".format(variable, value), override=True)
            else:
                self.execute(cur, "SET {}={}".format(variable, value), override=True)

    def commit(self):
        self.Con().commit()

    def close(self):
        self.Con().commit()
        self.Con().close()