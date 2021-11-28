# -*- coding: utf-8 -*-
"""
sqlwrap.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import logging
import codecs
import sys
import pandas as pd

try:
    from cStringIO import StringIO as IO_Stream
except ImportError:
    from io import BytesIO as IO_Stream

from .errors import DependencyError, SQLProgrammingError
from .defines import SQL_MYSQL, SQL_SQLITE
from .general import get_chunk
from . import options
from . import capturer

if options.use_mysql:
    import pymysql
    import pymysql.cursors


class SqlDB(object):
    """ A wrapper for MySQL. """
    def __init__(self, Host, Port, Type, User, Password, db_name="",
                 db_path="", encoding="utf8", connect_timeout=60,
                 local_infile=0):

        if Type == SQL_MYSQL and not options.use_mysql:
            raise DependencyError("pymysql",
                                  "https://github.com/PyMySQL/PyMySQL")

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

        self.sql_url = options.cfg.current_connection.url(db_name)
        self.engine = options.cfg.current_connection.get_engine(db_name)

        test, version = options.cfg.current_connection.test()
        if test:
            self.version = version
        else:
            self.version = ""
        self.connection = None

    def use_database(self, db_name):
        self.db_name = db_name
        self.sql_url = options.cfg.current_connection.url(db_name)
        self.engine = options.cfg.current_connection.get_engine(db_name)

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
        with self.engine.connect() as connection:
            if self.db_type == SQL_MYSQL:
                S = """
                    SELECT *
                    FROM information_schema.tables
                    WHERE table_schema = '{}' AND table_name = '{}'
                    """.format(self.db_name, table_name)
                return bool(connection.execute(S))
            elif self.db_type == SQL_SQLITE:
                S = """
                    SELECT *
                    FROM sqlite_master
                    WHERE type = 'table' and name = '{}'
                    """.format(table_name)
                return bool(connection.execute(S).fetchall())

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
        S = 'CREATE TABLE {} ({})'.format(table_name, description)
        with self.engine.connect() as connection:
            return connection.execute(S)

    def find(self, table, values, case=False):
        """
        Obtain all records from table_name that match the column-value
        pairs given in the dict values.

        Parameters
        ----------
        table : str
            The name of the table
        values : dict
            A dictionary with column names as keys and cell contents as
            values
        case : bool
            Set to True if the find should be case-sensitive, or False
            otherwise.

        Returns
        -------
        results : list
            A list of tuples representing the results from the find.
        """

        variables = list(values.keys())
        where = []
        for column, value in values.items():
            s = "{} = '{}'".format(column, str(value).replace("'", "''"))
            where.append(s)

        S = "SELECT {} FROM {}".format(", ".join(variables), table)

        # case sensitivity works differently for SQLite and MySQL:
        if self.db_type == SQL_MYSQL:
            if case:
                S = "{} WHERE BINARY {}".format(S,
                                                " AND BINARY ".join(where))
            else:
                S = "{} WHERE {}".format(S, " AND ".join(where))

        elif self.db_type == SQL_SQLITE:
            S = "{} WHERE {}".format(S, " AND ".join(where))
            if case:
                S = "{} COLLATE NOCASE".format(S)

        S = S.replace("\\", "\\\\")
        results = self.connection.execute(S).fetchall()
        return results

    def kill_connection(self):
        try:
            self.Con.kill(self.Con.thread_id())
        except (pymysql.OperationalError, pymysql.InternalError):
            pass

    def set_variable(self, variable, value):
        try:
            string_classes = (str, unicode)
        except NameError:
            string_classes = (str)
        if isinstance(value, string_classes):
            self.connection.execute("SET {} '{}'".format(variable, value))
        else:
            self.connection.execute("SET {}={}".format(variable, value))

    def close(self):
        return

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
            explain_table = self.connection.execute("EXPLAIN %s" % S)
        except pymysql.ProgrammingError as e:
            raise SQLProgrammingError(S + "\n" + "%s" % e)
        else:
            explain_table_rows = [[x[0] for x
                                   in explain_table.description]]
            for x in explain_table:
                explain_table_rows.append([str(y) for y in x])

            explain_column_width = [len(x[0]) for x
                                    in explain_table.description]
            for current_row in explain_table_rows:
                for i, x in enumerate(current_row):
                    explain_column_width[i] = max(explain_column_width[i],
                                                  len(x))

            format_string = " | ".join(["%%-%is" % x for x
                                        in explain_column_width])
            line_string = "-" * (sum(explain_column_width) - 3 +
                                 3 * len(explain_column_width))
            log_rows = ["EXPLAIN {}".format(S), line_string,
                        format_string % tuple(explain_table_rows[0]),
                        line_string]
            for x in explain_table_rows[1:]:
                log_rows.append(format_string % tuple(x))
            log_rows.append(line_string)
            logging.debug("\n".join(log_rows))

    def execute_cursor(self, S, server_side=False):
        def dict_factory(cursor, row):
            d = {}
            for i, column in enumerate(cursor.description):
                d[column[0]] = row[i]
            return d

        S = S.strip()
        if options.cfg.explain_queries:
            self.explain(S)
        logging.debug(S)

        cursor = None
        if self.db_type == SQL_MYSQL:
            if not self.Con.open:
                self.Con = self.get_connection()
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

    def load_dataframe(self, df, table_name, index_label,
                       if_exists="append"):
        """
        Load the table with content from the dataframe.

        Parameters
        ----------
        df : Pandas DataFrame
            The dataframe that is to be loaded into the database table
        table_name : string
            The name of the table
        index_label : string
            The name of the index column. If empty, no additional index
            column is created.
        if_exists : string, either "fail", "replace", or "append"
            If "append" (the default), the rows from the dataframe are
            appended to the table; the table is created if it does not
            exist. If "replace", any existing table is replaced by the
            rows from the dataframe. If "fail", the dataframe is NOT
            loaded into the table.

        Returns
        -------
        lines : int
            The number of lines that have been loaded into the table.
        """
        df.index = pd.RangeIndex(start=1, stop=len(df)+1, step=1)
        df.to_sql(table_name,
                  self.engine,
                  if_exists=if_exists,
                  index=bool(index_label),
                  index_label=index_label)
        return len(df)

    def load_file(self, file_name, encoding, table, index,
                  if_exists="append", skip=None, chunksize=250000, **kwargs):
        """
        Load the file content into the SQL table.

        Parameters
        ----------
        table_name : string
            The name of the table
        index : string
            The name of the index column. If empty, no additional index
            column is created.
        if_exists : string, either "fail", "replace", or "append"
            If "append" (the default), the rows from the dataframe are
            appended to the table; the table is created if it does not
            exist. If "replace", any existing table is replaced by the
            rows from the dataframe. If "fail", the dataframe is NOT
            loaded into the table.

        Returns
        -------
        lines : int
            The number of lines that have been loaded into the table.
        """
        count = 0
        chunk_signal = kwargs.pop("chunksignal", None)
        with codecs.open(file_name, "r", encoding=encoding) as big_file:

            # Iterate the chunks:
            for i, lines in enumerate(get_chunk(big_file, chunksize)):
                if chunk_signal:
                    chunk_signal.emit(i, None)
                content = list(lines)
                count += len(content)

                # create IO stream for chunk:
                if sys.version_info < (3, 0):
                    buffer = (u"\n".join([x.strip() for x in content])
                                   .replace("\x00", "")
                                   .encode("utf-8"))
                    stream = IO_Stream(buffer)
                else:
                    buffer = ("\n".join([x.strip() for x in content])
                                  .replace("\x00", ""))
                    stream = IO_Stream(bytes(buffer, encoding="utf-8"))

                # load the IO stream containing a chunk from the big
                # file into the matching table name:
                columns = self.load_infile(stream,
                                           table_name=table,
                                           if_exists=if_exists,
                                           index=index,
                                           keep_default_na=False,
                                           **kwargs).columns
                if i == 0:
                    kwargs["names"] = columns
                    kwargs["header"] = None
                kwargs["skiprows"] = None

        return count

    def load_infile(self, file_name, table_name, if_exists="append",
                    index=None, fillna=None, drop_duplicate=None, engine="c",
                    **kwargs):
        """
        Bulk-load a text file into a table.

        Parameters
        ----------
            fillna : used to fill missing values
            kwargs : dictionary of pandas.read_csv arguments

        """
        capt = capturer.Capturer(stderr=True)
        with capt:
            df = pd.read_csv(file_name, engine="c", **kwargs)
        for x in capt:
            logging.warning("File {} – {}".format(file_name, x))
            print("File {} – {}".format(file_name, x))

        if fillna is not None:
            df = df.fillna(fillna)
        if drop_duplicate:
            df = df[~df.duplicated(drop_duplicate)]
        self.load_dataframe(df,
                            table_name,
                            index_label=index,
                            if_exists=if_exists)
        return df

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
        if self.db_type == SQL_MYSQL:
            S = "SHOW FIELDS FROM {} WHERE Field = '{}'".format(
                table_name, column_name)
            results = self.connection.execute(S).fetchone()
            try:
                if isinstance(results, bytes):
                    results = results.decode("utf-8")
            except NameError:
                results = str(results)
            if results:
                field_type = results[1]
                if results[2] == "NO":
                    field_type += " NOT NULL"
                return str(field_type)
            else:
                return None

        elif self.db_type == SQL_SQLITE:
            S = "PRAGMA table_info({})".format(table_name)
            results = self.connection.execute(S)
            for row in results:
                result = dict(zip(
                    ("cid", "name", "type", "notnull", "dflt_value", "pk"),
                    row))
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
        S = "SELECT {} FROM {} PROCEDURE ANALYSE()".format(column_name,
                                                           table_name)
        x = list(self.connection.execute(S).fetchone())
        x = x[-1]
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
        S = "ALTER TABLE {} MODIFY {} {}".format(
            table_name, column_name, new_type)
        self.connection.execute(S)
        if options.cfg.verbose:
            logging.info(S)

    def has_index(self, table, index):
        """
        Check if the specified column has an index.

        Parameters
        ----------
        table, column: str
            The name of the table and the column, respectively

        Returns
        -------
        b : bool
            True if the column has an index, or False otherwise.
        """
        if self.db_type == SQL_MYSQL:
            S = "SHOW INDEX FROM {} WHERE Key_name = '{}'".format(table,
                                                                  index)
            return bool(self.connection.execute(S))
        elif self.db_type == SQL_SQLITE:
            S = """
                SELECT name FROM sqlite_master
                WHERE type = 'index' AND name = '{}' AND tbl_name = '{}'
                """.format(index, table)
            return bool(len(self.connection.execute(S).fetchall()))

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
            ROUND(COUNT(DISTINCT SUBSTR({column}, 1, len)) / total, 2)
            AS coverage
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

        results = self.connection.execute(S)
        max_c = None
        for x in results:
            if not max_c or x[3] > max_c[3]:
                max_c = x
            if x[3] >= coverage:
                s = "{}.{}: index length {}".format(table_name,
                                                    column_name,
                                                    x[0])
                logging.info(s)
                print(s)
                return int(x[0])
        if max_c:
            s = "{}.{}: index length {}".format(table_name,
                                                column_name,
                                                max_c[0])
            logging.info(s)
            print(s)
            return int(max_c[0])
        return None

    def create_index(self, table_name, index_name, variables,
                     index_length=None):
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
        if index_length:
            variables = ["%s(%s)" % (variables[0], index_length)]
        S = 'CREATE INDEX {} ON {}({})'.format(
            index_name, table_name, ",".join(variables))
        self.connection.execute(S)

    def executemany(self, s, d):
        s = s.replace("%s", "?")
        self.connection.execute(s, d)

    def execute(self, S):
        S = S.strip()
        if options.cfg.explain_queries:
            self.explain(S)
        logging.debug(S)
        self.connection.execute(S)
