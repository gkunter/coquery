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

from .defines import SQL_MYSQL, SQL_SQLITE, DEFAULT_CONFIGURATION
from .general import CoqObject, get_home_dir
from .unicode import utf8
from . import options

class Connection(CoqObject):
    def __init__(self, name, db_type=None):
        if name is None:
            raise TypeError
        self.name = name
        self._resources = {}
        self._db_type = db_type

    def db_type(self):
        return self._db_type

    def resource_path(self):
        path = os.path.join(get_home_dir(),
                            "connections", self.name, "corpora")
        return path

    def resources(self):
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
                    print(e)
                    warnings.warn("{} does not appear to be a valid corpus module.".format(corpus_name))
        return self._resources

    def add_resource(self, resource, corpus):
        self._resources[resource.name] = (resource, corpus)

    def remove_resource(self, name):
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
        if not options.use_mysql:
            return (False, None)
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
            path = os.path.join(get_home_dir(), "connections", name)

        if path is None:
            raise TypeError

        self.path = path

    def url(self, database):
        template = "sqlite+pysqlite:///{path}"
        path = os.path.join(self.path, "{}.db".format(database))
        return template.format(path=path)

    def remove_resource(self, name):
        raise NotImplementedError

    def rename(self, new_name):
        raise NotImplementedError

    def test(self):
        if os.access(self.path, os.X_OK | os.R_OK):
            return (True, None)
        else:
            return (False, IOError)


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

