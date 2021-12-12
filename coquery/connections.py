# -*- coding: utf-8 -*-
"""
connections.py is part of Coquery.

Copyright (c) 2017-2021 Gero Kunter (gero.kunter@coquery.org)

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
        self.name = name
        self._resources = {}
        self._db_type = db_type
        self.enabled = True

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
                logging.warning(s)
            else:
                try:
                    tup = (module.Resource, module.Corpus, module_name)
                    self._resources[module.Resource.name] = tup
                except AttributeError:
                    full_path = module_name
                    s = "{} does not appear to be a valid corpus module."
                    logging.warning(s.format(full_path))
                    print(s.format(full_path))

    def resources(self):
        return self._resources

    def add_resource(self, resource, corpus):
        self._resources[resource.name] = (resource, corpus)

    def remove_database(self, db_name):
        # As the virtual Connection class does not allocate any databases,
        # there is nothing to do here.
        pass

    def remove_resource(self, name, flags=(MODULE | DATABASE | INSTALLER)):
        resource = self.resources()[name][0]
        db_name = resource.db_name
        if flags & (Connection.DATABASE | Connection.MODULE):

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
                try:
                    os.remove("{}c".format(module_path))
                except FileNotFoundError:
                    pass

        # remove installer (only for adhoc corpora):
        if flags & Connection.INSTALLER:
            adhoc_path = os.path.join(self.base_path(),
                                      "adhoc",
                                      "coq_install_{}.py".format(db_name))
            if os.path.exists(adhoc_path):
                os.remove(adhoc_path)
            try:
                self._resources.pop(name)
            except KeyError:
                pass

    def get_resource(self, name):
        return self._resources.get(name, None)

    def rename(self, new_name):
        old_path = self.base_path()
        new_path = os.path.join(get_home_dir(), "connections", new_name)
        os.rename(old_path, new_path)
        self.name = new_name

    def count_resources(self):
        return len(self._resources)

    def get_engine(self, database=None):
        try:
            return sqlalchemy.create_engine(self.url(database))
        except ModuleNotFoundError:
            return None

    def url(self, db_name=None):
        return None

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
            The host address of the MySQL server, either by IP address or by
            name
        port : int
            The port that the MySQL server listens to
        user : str
            The username that will be used to authenticate the MySQL
            connection
        password : str
            The password that will be used to authenticate the MySQL
            connection
        params : list of strings
            A list of options that will be passed to the server on
            establishing the connection
            Default: ["charset=utf8mb4", "local_infile=1"]
        """
        super(MySQLConnection, self).__init__(name, SQL_MYSQL)
        if (host is None or
                port is None
                or user is None or
                password is None):
            raise TypeError
        self.host = host or "127.0.0.1"
        self.port = port
        self.user = user
        self.password = password
        if params is None:
            params = ["charset=utf8mb4", "local_infile=1"]
        self.params = params
        try:
            import pymysql
        except ImportError:
            self.enabled = False
        else:
            self.enabled = True

    def url(self, db_name=None):
        template = ("mysql+pymysql://{user}:{password}@{host}:{port}"
                    "{database}{params}")
        kwargs = dict(self.__dict__)

        if db_name:
            kwargs["database"] = "/{}".format(db_name)
        else:
            kwargs["database"] = ""
        if db_name and self.params:
            kwargs["params"] = "?{}".format("&".join(self.params))
        else:
            kwargs["params"] = ""
        return template.format(**kwargs)

    def test(self):
        engine = self.get_engine()
        if not engine:
            return False, ""

        try:
            with engine.connect() as connection:
                result = connection.execute("SELECT VERSION()")
        except sqlalchemy.exc.SQLAlchemyError as e:
            res = (False, e)
        except Exception as e:
            engine.dispose()
            raise e
        else:
            res = (True, result.fetchall()[0][0])
            result.close()
            engine.dispose()
        return res

    def create_database(self, db_name):
        engine = self.get_engine()
        sql_str = """
            CREATE DATABASE {}
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            """.format(db_name.split()[0])
        with engine.connect() as connection:
            connection.execute(sql_str)
        engine.dispose()

    def remove_database(self, db_name):
        engine = self.get_engine(db_name)
        sql_template = f"DROP DATABASE {db_name}"
        with engine.connect() as connection:
            connection.execute(sql_template)
        engine.dispose()

    def has_database(self, db_name):
        engine = self.get_engine(db_name)
        sql_template = """
            SELECT SCHEMA_NAME
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME = '{}'
            """.format(db_name)
        try:
            with engine.connect() as connection:
                connection.execute(sql_template)
        except (sqlalchemy.exc.InternalError,
                sqlalchemy.exc.OperationalError):
            engine.dispose()
            return False
        except Exception as e:
            print(type(e))
            engine.dispose()
            raise e
        engine.dispose()
        return True

    def get_database_size(self, db_name):
        engine = self.get_engine(db_name)
        sql_template = """
            SELECT data_length+index_length
            FROM information_schema.tables
            WHERE table_schema = '{}'""".format(db_name)
        with engine.connect() as connection:
            size = connection.execute(sql_template).fetchone()[0]
        engine.dispose()
        return size

    def has_user(self, user):
        """
        Checks if the user specified by the argument exists on the current
        host.

        This method assumes that the user account for which the connection has been created is privileged to query the currently existing users.
        """
        sql_template = "SELECT User, Host from mysql.user"

        engine = self.get_engine()
        with engine.connect() as connection:
            results = connection.execute(sql_template)
        engine.dispose()

        local_hosts = ["127.0.0.1", "localhost"]

        if self.host in local_hosts:
            hosts = local_hosts
        else:
            hosts = [self.host]

        for existing_user, host in results:
            if user == existing_user and host in hosts:
                return True
        else:
            return False

    def create_user(self, user, pwd):
        sql_new_user = f"CREATE USER {user}@{self.host} IDENTIFIED BY {pwd}"
        sql_privileges = f"GRANT ALL PRIVILEGES ON * . * TO {user}@{self.host}"
        sql_flush = "FLUSH PRIVILEGES"

        engine = self.get_engine()
        try:
            with engine.connect() as connection:
                connection.execute(sql_new_user)

            # now that the user has been created, grant it all privileges
            # it needs:
            try:
                with engine.connect() as connection:
                    connection.execute(sql_privileges)
                    connection.execute(sql_flush)
            except Exception as e:
                self.drop_user(user)
                raise RuntimeError(f"User not created:\n{str(e)}")
        finally:
            engine.dispose()

    def drop_user(self, user):
        sql_remove_user = f"DROP USER '{user}'@'{self.host}'"

        engine = self.get_engine()
        try:
            with engine.connect() as connection:
                connection.execute(sql_remove_user)
        finally:
            engine.dispose()


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

    def db_path(self, db_name):
        return os.path.join(self.path, "{}.db".format(db_name))

    def url(self, db_name=None):
        template = "sqlite+pysqlite:///{path}"
        return template.format(path=self.db_path(db_name))

    def test(self):
        if os.access(self.path, os.X_OK | os.R_OK):
            return True, None
        else:
            return False, IOError

    def create_database(self, db_name):
        pass

    def remove_database(self, db_name):
        os.remove(self.db_path(db_name))

    def has_database(self, db_name):
        return os.path.exists(self.db_path(db_name))

    def get_database_size(self, db_name):
        return os.path.getsize(self.db_path(db_name))


def get_connection(name, dbtype=None,
                   host=None, port=None, user=None, password=None,
                   path=None):
    """
    Returns a valid connection based on the dbtype.

    An TypeError exception is raised if not all required parameters are set.
    """
    if dbtype == SQL_MYSQL:
        return MySQLConnection(name, host, port, user, password)
    elif dbtype == SQL_SQLITE:
        return SQLiteConnection(name, path)
