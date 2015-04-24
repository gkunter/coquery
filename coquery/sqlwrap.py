# -*- coding: utf-8 -*-
"""
FILENAME: sqlwrap.py -- part of Coquery corpus query tool

This module defines a wrapper to access a MySQL database.

LICENSE:
Copyright (c) 2015 Gero Kunter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import __init__

import logging

logger = logging.getLogger(__init__.NAME)


from errors import *
from options import *

try:
    import MySQLdb as mysql
    import MySQLdb.cursors as mysql_cursors
except ImportError:
    import pymysql as mysql
    import pymysql.cursors as mysql_cursors

ExecutedLastCommand = False

ModifyingCommands = ["ALTER", "CREATE", "DELETE", "DROP", "INSERT", 
                     "LOAD", "UPDATE"]
NonModifyingCommands = ["SELECT", "SHOW", "DESCRIBE", "SET", "RESET"]

class myDictCursor(mysql_cursors.Cursor):
    """ a DictCursor that is fully iterable. For some reason, this didn't
    work with the mysql.DictCursor class."""
    def __init__(self, *args):
        super(myDictCursor, self).__init__(*args)
        self.column_names = None
        
    def fetchone(self, *args):
        next_row = super(myDictCursor, self).fetchone(*args)
        if not self.column_names:
            self.column_names = [current_column[0] for i, current_column in enumerate(self.description)]
        if next_row == None:
            return None
        else:
            return dict(zip(self.column_names, next_row))
        
    def __next__(self):
        return self.next()
        
    def next(self):
        next_row = self.fetchone()
        if next_row == None:
            raise StopIteration
        else:
            return next_row
        
    def __iter__(self):
        self.column_names = [current_column[0] for i, current_column in enumerate(self.description)]
        return self

class mySSDictCursor(mysql_cursors.SSCursor):
    """ a DictCursor that is fully iterable. For some reason, this didn't
    work with the mysql.DictCursor class."""
    def __init__(self, *args):
        super(mySSDictCursor, self).__init__(*args)
        self.column_names = None
        
    def fetchone(self, *args):
        next_row = super(mySSDictCursor, self).fetchone(*args)
        if not self.column_names:
            self.column_names = [current_column[0] for i, current_column in enumerate(self.description)]
        if next_row == None:
            return None
        else:
            return dict(zip(self.column_names, next_row))
        
    def __next__(self):
        return self.next()
        
    def next(self):
        next_row = self.fetchone()
        if next_row == None:
            raise StopIteration
        else:
            return next_row
        
    def __iter__(self):
        self.column_names = [current_column[0] for i, current_column in enumerate(self.description)]
        return self
    
class SqlDB (object):
    def __init__(self, Host, Port, User, Password, Database):
        self.Con = None
        self.Cur = None
        self.Host = Host
        self.Port = Port
        self.User = User
        self.Password = Password
        self.Database = Database
        self.LastQuery = None
        
        try:
            if mysql.__name__ == "mysql.connector":
                self.Con = mysql.connect (
                    host=Host, 
                    port=Port, 
                    user=User, 
                    password=Password, 
                    database=Database)
            else:
                self.Con = mysql.connect (
                    host=Host, 
                    port=Port, 
                    user=User, 
                    passwd=Password, 
                    db=Database)
        except Exception as e:
             raise SQLInitializationError(e)
        
        self.Cur = self.Con.cursor()

    def explain(self, S):
        """
Call        explain(self, S)
Summary     Execute an SQL EXPLAIN command for the command S. The resulting
            table will be printed to the log file as INFO.             
Value       no return value
        """
        command = S.partition(" ")[0].upper()
        if command in ["SHOW", "DESCRIBE", "SET", "RESET"]:
            return
        try:
            self.Cur.execute("EXPLAIN %s" % S)
        except mysql.ProgrammingError as e:
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

    def execute_cursor(self, S, cursor_type=myDictCursor):
        if cursor_type is "SSCursor":
            cursor_type = mysql_cursors.SSCursor
        elif cursor_type is "Cursor":
            cursor_type = mysql_cursors.Cursor
        S = S.strip()

        Command = S.partition(" ")[0].upper()

        if Command in ModifyingCommands:
            Modify = True
        elif Command in NonModifyingCommands:
            Modify = False
        else:
            logger.warning("Command '%s' not categorized, assuming modifying commannd" % Command)
            Modify = True

        if Command == "SELECT" and cfg.no_cache: 
            S = S.replace ("SELECT", "SELECT SQL_NO_CACHE")

        self.last_command = S
        if cfg.explain_queries:
            self.explain(S)
        if cfg.verbose:
            logger.debug(S)

        if cfg.dry_run:
            ExecutedLastCommand = not Modify
            cursor = []
        else:
            ExecutedLastCommand = True
            self.last_command = S
            cursor = self.Con.cursor(cursor_type)
            try:
                cursor.execute(S)
            except mysql.OperationalError:
                raise SQLOperationalError(S)
            except mysql.ProgrammingError:
                raise SQLProgrammingError(S)
        return cursor
    
    def execute(self, S, ForceExecution = False):
        """
Call        execute(self, S, ForceExecution=False)
Summary     Executes the SQL command string provided in S, or pretend to do 
            so if cfg.dry_run is True and the SQL command is a modifying 
            command. The parameter ForceExecution can be used to override 
            cfg.dry_run.
            if cfg.ExplainQueries is True, an SQL EXPLAIN command will be
            executed as well, and the output will be displayed.
Value       no return value
        """
        S = S.strip()

        Command = S.partition(" ")[0].upper()

        if Command in ModifyingCommands:
            Modify = True
        elif Command in NonModifyingCommands:
            Modify = False
        else:
            Modify = True

        if Command == "SELECT" and cfg.no_cache: 
            S = S.replace ("SELECT", "SELECT SQL_NO_CACHE")

        self.last_command = S
        if cfg.explain_queries:
            self.explain(S)
        logger.debug(S)

        if cfg.dry_run and not ForceExecution:
            ExecutedLastCommand = not Modify
        else:
            ExecutedLastCommand = True
            self.last_command = S
            try:
                self.Cur.execute(S)
            except mysql.OperationalError:
                raise SQLOperationalError(S)
            except mysql.ProgrammingError:
                raise SQLProgrammingError(S)

    def commit (self):
        if not cfg.dry_run:
            self.Con.commit ()
        
    def rollback (self):
        if not cfg.dry_run:
            self.Con.rollback ()

    def fetch_all (self):
        return self.Cur.fetchall()

    def next(self):
        return self.Cur.fetchone()
    
    def start_read_only(self):
        self.execute("START TRANSACTION READ ONLY")
        self.commit()