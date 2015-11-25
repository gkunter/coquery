# -*- coding: utf-8 -*-
"""
sqlwrap.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import __init__

import logging

try:
    logger = logging.getLogger(__init__.NAME)
except AttributeError:
    pass

from errors import *
import options

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    raise DependencyError("pymysql")

class SqlDB (object):
    """ A wrapper for MySQL. """
    def __init__(self, Host, Port, User, Password, db_name=None, encoding="utf8", connect_timeout=60):
        self.Con = None
        self.Cur = None
        try:
            if db_name:
                self.Con = pymysql.connect(
                    host=Host, 
                    port=Port, 
                    user=User, 
                    passwd=Password, 
                    db=db_name,
                    connect_timeout=connect_timeout,
                    charset=encoding)
            else:
                self.Con = pymysql.connect(
                    host=Host, 
                    port=Port, 
                    user=User, 
                    passwd=Password,
                    connect_timeout=connect_timeout,
                    charset=encoding)

        except (pymysql.OperationalError, pymysql.InternalError) as e:
             raise SQLInitializationError(e)
        self.Cur = self.Con.cursor()
        self.set_variable("NAMES", encoding)

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
            self.Cur.close()
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
            self.Cur.execute("EXPLAIN %s" % S)
        except pymysql.ProgrammingError as e:
            raise SQLProgrammingError(S + "\n"+ "%s" % e)
        else:
            explain_table = self.Cur
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
        S = S.strip()
        if options.cfg.explain_queries:
            self.explain(S)
        logger.debug(S)

        if server_side:
            cursor = self.Con.cursor(pymysql.cursors.SSDictCursor)
        else:
            cursor = self.Con.cursor(pymysql.cursors.DictCursor)
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

        self.Cur.execute(S)

    def commit (self):
        self.Con.commit ()
        
    def rollback (self):
        self.Con.rollback ()

    def fetch_all (self):
        return self.Cur.fetchall()

    def next(self):
        return self.Cur.fetchone()
    
    def start_read_only(self):
        self.Cur.execute("START TRANSACTION READ ONLY;")
        
    def get_database_size(self, database):
        """ Returns the size of the database in bytes."""
        self.Cur.execute("SELECT data_length+index_length FROM information_schema.tables WHERE table_schema = '{}'".format(database))
        return self.Cur.fetchone()[0]
