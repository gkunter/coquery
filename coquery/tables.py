# -*- coding: utf-8 -*-
"""
tables.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import collections
import pandas as pd
import re
import sys

from .defines import SQL_MYSQL, SQL_SQLITE
from .unicode import utf8


class Column(object):
    """ Define an object that stores the description of a column in one
    MySQL table."""
    is_identifier = False
    key = False

    def __init__(self, name, data_type, index_length=None):
        """
        Initialize the column

        Parameters
        ----------
        name : str
            The name of the column
        data_type : str
            A MySQL data type description
        index_length : int or None
            The length of the index for this column. If None, the index length
            will be determined automatically, which can take quite some time
            for larger corpora.
        """

        self._name = name
        self._data_type = data_type
        self.index_length = index_length
        self.unique = False

    def __repr__(self):
        return "Column({}, {}, {})".format(self._name,
                                           self._data_type,
                                           self.index_length)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def data_type(self):
        """
        Return the data type of the column.

        Returns
        -------
        data_type : string
            The data type of the column in the same form as used by the
            MySQL CREATE TABLE command.

        """
        return self._data_type

    @property
    def base_type(self):
        """
        Return the base type of the column.

        This function does not return the field length, but only the base
        data type, i.e. VARCHAR, MEDIUMINT, etc.

        Use data_type for the full column specification.

        Returns
        -------
        base_type : string
            A MySQL base data type.

        """
        return self._data_type.split()[0].partition("(")[0].upper()

    @data_type.setter
    def data_type(self, new_type):
        self._data_type = new_type


class Identifier(Column):
    """ Define a Column class that acts as the primary key in a table."""
    is_identifier = True

    def __init__(self, name, data_type, unique=True, index_length=None):
        super(Identifier, self).__init__(name, data_type, index_length)
        self.unique = unique

    def __repr__(self):
        return ("Identifier(name='{}', data_type='{}', unique={},"
                "index_length={})").format(self._name, self._data_type,
                                           self.unique, self.index_length)

    @property
    def name(self):
        return self._name
        if self.unique:
            return self._name
        else:
            return "{}_primary".format(self._name)


class Link(Column):
    """ Define a Column class that links a table to another table. In MySQL
    terms, this acts like a foreign key."""
    key = True

    def __init__(self, name, table_name):
        super(Link, self).__init__(name, "", True)
        self._link = table_name

    def __repr__(self):
        return "Link(name='{}', '{}', data_type='{}')".format(
            self._name, self._link, self._data_type)


class Table(object):
    """ Define a class that is used to store table definitions."""
    def __init__(self, name):
        self._name = name
        self.columns = list()
        self.primary = None
        self._current_id = 0
        self._row_order = []
        self._add_cache = dict()
        self._add_cache2 = list()
        # The defaultdict _add_lookup will store the index of rows in this
        # table. It uses the trick described at http://ikigomu.com/?p=186
        # to achieve an O(1) lookup. When looking up a row as in
        #
        # x = self._add_lookup[tuple([row[x] for x in self._row_order])]
        #
        # the returned value is the length of the lookup table at the time
        # the entry was created. In other words, this is the row id of that
        # row.
        self._add_lookup = collections.defaultdict(
            lambda: len(self._add_lookup) + 1)
        self._commited = {}
        self._col_names = None
        self._engine = None
        self._max_cache = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, s):
        self._name = s

    def setDB(self, db):
        self._DB = db

    def commit(self):
        """
        Commit the table content to the data base.

        This table commits the unsaved content of the table to the data base.

        As this method is usually called after a file has been processed,
        this ensures that all new table rows are commited, while at the same
        time preserving some memory space.
        """

        if self._add_cache2:
            df = pd.DataFrame(self._add_cache2)

            try:
                df.columns = self._get_field_order()
            except ValueError as e:
                raise e

            # make sure that all strings are unicode, even under
            # Python 2.7:
            if sys.version_info < (3, 0):
                for column in df.columns[df.dtypes == object]:
                    try:
                        df[column] = df[column].apply(utf8)
                    except TypeError:
                        pass

            # apply unicode normalization:
            for column in df.columns[df.dtypes == object]:
                try:
                    df[column] = df[column].str.normalize("NFKC")
                except TypeError:
                    pass

            df.to_sql(self.name, self._DB.engine, if_exists="append",
                      index=False)
            self._add_cache2 = list()

    def add(self, values):
        """
        Store the 'values' dictionary in the add cache of the table. If
        necessary, a valid primary key is added to the values.

        """
        l = [values[x] for x in self._row_order]

        if self.primary.name not in self._row_order:
            self._current_id += 1
            self._add_cache2.append(tuple([self._current_id] + l))
        else:
            self._current_id = values[self.primary.name]
            self._add_cache2.append(tuple(l))

        self._add_lookup[tuple(l)] = self._current_id

        if self._max_cache and len(self._add_cache2) > self._max_cache:
            self.commit()

        return self._current_id

    def get_or_insert(self, values, case=False):
        """
        Returns the id of the first entry matching the values from the table.

        If there is no entry matching the values in the table, a new entry is
        added to the table based on the values.
        description.

        Parameters
        ----------
        values : dict
            A dictionary with column names as keys, and the entry content
            as values.

        Returns
        -------
        id : int
            The id of the entry, as it is stored in the SQL table.
        """
        key = tuple([values[x] for x in self._row_order])
        if key in self._add_lookup:
            return self._add_lookup[key]
        else:
            return self.add(values)

    def _get_field_order(self):
        if self.primary.name not in self._row_order:
            return [self.primary.name] + self._row_order
        else:
            return self._row_order

    def find(self, values):
        """
        Return the first row that matches the values, or None
        otherwise.
        """
        x = self._DB.find(self.name, values, [self.primary.name])
        if x:
            return x[0]
        else:
            return None

    def add_column(self, column):
        self.columns.append(column)
        if column.name in self._row_order:
            if not column.key:
                raise ValueError("Duplicate column: {}, {}".format(
                    self._row_order, column.name))
            else:
                return
        if column.is_identifier:
            self.primary = column
            if not column.unique:
                self._row_order.append(column.name)
        else:
            self._row_order.append(column.name)

    def get_column(self, name):
        """
        Return the specified column.

        Parameters
        ----------
        name : string
            The name of the column

        Returns
        -------
        col : object or NoneType
            The Column object matching the name, or None.
        """
        for x in self.columns:
            if x.name == name:
                return x
        return None

    def suggest_data_type(self, name):
        """
        Return an SQL data type that may be optimal in terms of storage space.

        For INT types, the optimal data type is the smallest integer type that
        is large enough to store the integer.

        For CHAR and TEXT types, the optimal data type is VARCHAR(max), where
        max is the maximum number of characters for the column.

        FOR DECIMAL and NUMERIC types, the optimal type is changed to FLOAT
        on MySQL and to REAL on SQLite3.

        For FLOAT, DOUBLE, and REAL types, the optimal type is not changed on
        MySQL, but changed to REAL on SQLite3.

        Parameters
        ----------
        name : string
            The name of the column

        Returns
        -------
        S : string
            A string containing the suggested data type
        """

        sql_int = [
            (0, 255, "TINYINT UNSIGNED"),
            (-128, 127, "TINYINT"),
            (0, 65535, "SMALLINT UNSIGNED"),
            (-32768, 32767, "SMALLINT"),
            (0, 16777215, "MEDIUMINT UNSIGNED"),
            (-8388608, 8388607, "MEDIUMINT"),
            (0, 4294967295, "INT UNSIGNED"),
            (-2147483648, 2147483647, "INT")]

        if self._DB.db_type == SQL_SQLITE:
            func_length = "length"
        elif self._DB.db_type == SQL_MYSQL:
            func_length = "CHAR_LENGTH"

        col = self.get_column(name)

        # test if column contains NULL
        S = "SELECT MAX({0} IS NULL) FROM {1}".format(col.name, self.name)
        with self._DB.engine.connect() as connection:
            has_null = connection.execute(S).fetchone()[0]

        # In an empty table, the previous check returns NULL. In this case,
        # the original data type will be returned.
        if has_null is None:
            dt_type = col.data_type

        # integer data types:
        elif col.base_type.endswith("INT"):
            S = ("SELECT MIN({0}), MAX({0}) FROM {1} WHERE {0} IS NOT NULL"
                 .format(col.name, self.name))
            with self._DB.engine.connect() as connection:
                v_min, v_max = connection.execute(S).fetchone()

            for dt_min, dt_max, dt_label in sql_int:
                if v_min >= dt_min and v_max <= dt_max:
                    dt_type = dt_label
                    break
            else:
                if v_min >= 0:
                    dt_type = "BIGINT UNSIGNED"
                else:
                    dt_type = "BIGINT"

        # character data types:
        elif col.base_type.endswith(("CHAR", "TEXT")):
            S = "SELECT MAX({2}(RTRIM({0}))) FROM {1}".format(
                col.name, self.name, func_length)
            with self._DB.engine.connect() as connection:
                max_len = connection.execute(S).fetchone()[0]
            dt_type = "VARCHAR({})".format(max_len)

        # fixed-point types:
        elif col.base_type in ["DECIMAL", "NUMERIC"]:
            if self._DB.db_type == SQL_SQLITE:
                dt_type = "REAL"
            else:
                dt_type = col.data_type.replace(col.base_type, "FLOAT")

        # float and decimal data types:
        elif col.base_type in ["FLOAT", "DOUBLE", "REAL"]:
            if self._DB.db_type == SQL_SQLITE:
                dt_type = "REAL"
            else:
                dt_type = col.data_type

            S = ("SELECT MIN({0}), MAX({0}) FROM {1} WHERE {0} IS NOT NULL"
                 .format(col.name, self.name))
            with self._DB.engine.connect() as connection:
                v_min, _ = connection.execute(S).fetchone()

            if v_min >= 0:
                dt_type = "{} UNSIGNED".format(dt_type)

        # all other data types:
        else:
            dt_type = col.data_type

        if has_null == 0:
            dt_type = "{} NOT NULL".format(dt_type)

        return dt_type

    def get_create_string(self, db_type, index_gen=False):
        """
        Generates the SQL command required to create the table.

        Parameters
        ----------
        db_type : str
            A string representing the SQL engine, either "mysql" or "sqlite"

        index_gen : bool
            A boolean variable that indicates whether a generated indexed
            column should be created for this table.

            If `index_gen` is False, no generated index column will be
            generated. If it is True, an generated column named `Next{}` will
            will be generated with the primary index name inserted into the
            string. This column will contain the value of the
            primary key + 1.

            At the moment, this is only available in MySQL databases.

        Returns
        -------
        S : str
            A string that can be sent to the SQL engine in order to create
            the table according to the specifications.
        """
        command_list = []
        str_list = []
        columns_added = set([])
        for column in self.columns:
            if db_type == SQL_MYSQL:
                if column.is_identifier:
                    if not column.unique:
                        # add surrogate key
                        # do not add AUTO_INCREMENT to strings or ENUMs:
                        str_list.insert(0, ("`{}_primary` INT AUTO_INCREMENT"
                                            .format(column.name)))
                        str_list.insert(1, ("`{}` {}"
                                            .format(column.name,
                                                    column.data_type)))
                        str_list.append("PRIMARY KEY ({}_primary)".format(
                            column.name))
                    else:
                        # do not add AUTO_INCREMENT to strings or ENUMs:
                        if column.data_type.upper().startswith(
                                ("ENUM", "VARCHAR", "TEXT")):
                            pattern = "`{}` {}"
                        else:
                            pattern = "`{}` {} AUTO_INCREMENT"
                        pattern = "`{}` {}"
                        str_list.append(pattern.format(column.name,
                                                       column.data_type))
                        str_list.append("PRIMARY KEY (`{}`)".format(
                            column.name))
                    # add generated index column for next token?
                    if index_gen:
                        if "mariadb" in self._DB.version.lower():
                            kwd = "PERSISTENT"
                        else:
                            kwd = "STORED"
                        # FIXME: GENERATED is available only in MySQL 5.7.5
                        # onward. There has to be a check for version.
                        #str_list.append("Next{id} INT NOT NULL GENERATED ALWAYS AS ({id} + 1) {kwd}".format(
                            #id=column.name, kwd=kwd))
                        #str_list.append("INDEX {id}Next{id} ({id}, Next{id})".format(
                            #id=column.name))
                else:
                    str_list.append("`{}` {}".format(
                        column.name,
                        column.data_type))
                columns_added.add(column.name)
            elif db_type == SQL_SQLITE:
                # replace ENUM by VARCHAR:
                match = re.match("^\s*enum\((.+)\)(.*)$",
                                 column.data_type,
                                 re.IGNORECASE)
                if match:
                    max_len = 0
                    for x in match.group(1).split(","):
                        max_len = max(max_len, len(x.strip(" '\"")))
                    data_type = "VARCHAR({max_len}) {spec}".format(
                        max_len=max_len, spec=match.group(2))
                else:
                    data_type = column.data_type

                if column.is_identifier:
                    if not column.unique:
                        # add surrogate key
                        str_list.insert(0, ("{}_primary INT PRIMARY KEY"
                                            .format(column.name)))
                        str_list.insert(1, ("{} {}"
                                            .format(column.name, data_type)))
                    else:
                        str_list.append(("{} {} PRIMARY KEY"
                                         .format(column.name, data_type)))
                else:
                    str_list.append("{} {}".format(
                        column.name, data_type))
                columns_added.add(column.name)
        if db_type == SQL_SQLITE:
            # make SQLite columns case-insensitive by default
            for i, x in enumerate(list(str_list)):
                field_type = x.split()[1]
                if ("VARCHAR" in field_type.upper() or
                        "TEXT" in field_type.upper()):
                    str_list[i] = "{} COLLATE NOCASE".format(x)
        S = ",\n\t".join(str_list)
        command_list.insert(0, S)
        table_str = "; ".join(command_list)
        if db_type == SQL_SQLITE:
            table_str = re.sub(r"\s*UNSIGNED", "", table_str)
        return table_str
