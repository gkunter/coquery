# -*- coding: utf-8 -*-
"""
connections.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import glob
import sqlalchemy
import imp
import logging

from .defines import SQL_MYSQL, SQL_SQLITE, DEFAULT_CONFIGURATION
from .general import CoqObject, get_home_dir
from .unicode import utf8

class Connection(CoqObject):
    MODULE = 1 << 1
    INSTALLER = 1 << 2
    DATABASE = 1 << 3

    def __init__(self, name, db_type=None):
        if name is None:
            raise TypeError
        self.name = name
        self._resources = {}
        self._db_type = db_type

    def db_type(self):
        return self._db_type

    def base_path(self):
        path = os.path.join(get_home_dir(), "connections", self.name)
        return path

    def resource_path(self):
        path = os.path.join(self.base_path(), "corpora")
        return path

    def find_resources(self):
        self._resources = {}
        path = os.path.join(self.resource_path(), "*.py")
        for module_name in glob.glob(path):
            corpus_name, _ = os.path.splitext(os.path.basename(module_name))
            corpus_name = utf8(corpus_name)

            try:
                find = imp.find_module(corpus_name, [self.resource_path()])
                module = imp.load_module(corpus_name, *find)
            except Exception as e:
                s = ("There is an error in corpus module '{}': {}\n"
                     "The corpus is not available for queries.").format(
                         corpus_name, str(e))
                print(s)
                logging.warn(s)
            else:
                try:
                    tup = (module.Resource, module.Corpus, module_name)
                    self._resources[module.Resource.name] = tup
                except AttributeError as e:
                    full_path = module_name
                    s = "{} does not appear to be a valid corpus module."
                    logging.warn(s.format(full_path))
                    print(s.format(full_path))

    def resources(self):
        return self._resources

    def add_resource(self, resource, corpus):
        self._resources[resource.name] = (resource, corpus)

    def remove_resource(self, name, flags=(MODULE | DATABASE | INSTALLER)):
        resource = self.resources()[name][0]

        # remove database:
        if flags & Connection.DATABASE:
            self.remove_database(db_name)

        # remove corpus module:
        if flags & Connection.MODULE:
            module_path = os.path.join(self.resource_path(),
                                       "{}.py".format(db_name))
            if os.path.exists(module_path):
                os.remove(module_path)

            # also remove the compiled python module:
            os.remove("{}c".format(module_path))

        # remove installer (only for adhoc corpora):
        if flags & Connection.INSTALLER:
            adhoc_path = os.path.join(self.base_path(),
                                      "adhoc",
                                      "coq_install_{}.py".format(db_name))
            if os.path.exists(adhoc_path):
                os.remove(adhoc_path)
            self._resources.pop(name)

    def get_resource(self, name):
        return self._resources.get(name, None)

    def rename(self, new_name):
        self.name = new_name

    def count_resources(self):
        return len(self._resources)

    def __len__(self):
        return len(self.resources())

    def get_engine(self, database=None):
        return sqlalchemy.create_engine(self.url(database))

    def __repr__(self):
        template = "{name}({arguments})"
        name = self.__class__.__name__
        arguments = ["{}='{}'".format(x, y) if type(x) == str else
                     "{}={}".format(x, y)
                     for x, y in self.__dict__.items()
                     if not x.startswith("_")]
        return template.format(name=name, arguments=", ".join(arguments))


class MySQLConnection(Connection):
    """
    Define a MySQL connection.

    """
    def __init__(self, name, host, port, user, password, params=None):
        """
        Parameters
        ----------
        name : str
            The name of the connection
        host : str
            The host address of the MySQL server, either by IP address or by name
        port : int
            The port that the MySQL server listens to
        user : str
            The user name that will be used to authenticate the MySQL connection
        password : str
            The password that will be used to authenticate the MySQL connection
        params : list of strings
            A list of options that will be passed to the server on establishing
            the connection, default: ["charset=utf8mb4", "local_infile=1"]
        """
        super(MySQLConnection, self).__init__(name, SQL_MYSQL)
        if (host is None or port is None or user is None or password is None):
            raise TypeError
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        if params is None:
            params = ["charset=utf8mb4", "local_infile=1"]
        self.params = params

    def url(self, database=None):
        template = ("mysql+pymysql://{user}:{password}@{host}:{port}"
                    "{database}{params}")
        kwargs = dict(self.__dict__)

        if database:
            kwargs["database"] = "/{}".format(database)
        else:
            kwargs["database"] = ""
        if database and self.params:
            kwargs["params"] = "?{}".format("&".join(self.params))
        else:
            kwargs["params"] = ""
        return template.format(**kwargs)

    def test(self):
        try:
            engine = sqlalchemy.create_engine(self.url())
            with engine.connect() as connection:
                result = connection.execute("SELECT VERSION()")
        except sqlalchemy.exc.SQLAlchemyError as e:
            res = (False, e)
        except Exception as e:
            raise e
        else:
            res = (True, result.fetchall()[0][0])
            result.close()
            try:
                engine.dispose()
            except UnboundLocalError:
                pass
        return res

    def create_database(self, db_name):
        engine = self.get_engine(db_name)
        with engine.connect() as connection:
            S = """
                CREATE DATABASE {}
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
                """.format(db_name.split()[0])
            connection.execute(S)
        engine.dispose()

    def remove_database(self, db_name):
        sql_string = "DROP DATABASE {}".format(db_name)
        with self.get_engine().connect() as connection:
            connection.execute(sql_string)

    def has_database(self, db_name):
        engine = self.get_engine(db_name)
        S = """
            SELECT SCHEMA_NAME
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME = '{}'
            """.format(db_name)
        try:
            engine.execute(S)
            engine.dispose()
        except sqlalchemy.exc.InternalError as e:
            return False
        except Exception as e:
            raise e
        else:
            return True

    def get_database_size(self, db_name):
        engine = self.get_engine(db_name)
        S = """
            SELECT data_length+index_length
            FROM information_schema.tables
            WHERE table_schema = '{}'""".format(db_name)
        with engine.connect() as connection:
            size = connection.execute(S).fetchone()[0]
        engine.dispose()
        return size


class SQLiteConnection(Connection):
    """
    Define an SQLite connection.
    """
    def __init__(self, name, path=None):
        """
        Parameters
        ----------
        name : str
            The name of the connection
        path : str
            The path where the database files are stored for this connection
        """
        super(SQLiteConnection, self).__init__(name, SQL_SQLITE)

        if name == DEFAULT_CONFIGURATION:
            path = os.path.join(self.base_path(), "databases")

        if path is None:
            raise TypeError

        self.path = path

    def rename(self, new_name):
        raise NotImplementedError

    def url(self, db_name):
        template = "sqlite+pysqlite:///{path}"
        path = os.path.join(self.path, "{}.db".format(db_name))
        return template.format(path=path)

    def test(self):
        if os.access(self.path, os.X_OK | os.R_OK):
            return (True, None)
        else:
            return (False, IOError)

    def create_database(self, db_name):
        pass

    def remove_database(self, db_name):
        os.remove(os.path.join(self.path, "{}.db".format(db_name)))

    def has_database(self, db_name):
        path = os.path.join(self.path, "{}.db".format(db_name))
        return os.path.exists(path)

    def get_database_size(self, db_name):
        path = os.path.join(self.path, "{}.db".format(db_name))
        return os.path.getsize(path)

def get_connection(name, dbtype,
                   host=None, port=None, user=None, password=None,
                   path=None, **kwargs):
    """
    Returns a valid connection based on the dbtype.

    An TypeError exception is raised if not all required parameters are set.
    """
    if dbtype == SQL_MYSQL:
        return MySQLConnection(name, host, port, user, password)
    elif dbtype == SQL_SQLITE:
        return SQLiteConnection(name, path)

