from __future__ import unicode_literals 

try:
    import MySQLdb as mysql
    import MySQLdb.cursors as mysql_cursors
except ImportError:
    import pymysql as mysql
    import pymysql.cursors as mysql_cursors

import logging
import copy

verbose = False
name = ""
logger = None

class DBConnection(object):
    def __init__(self, db_user="mysql", db_host="localhost", db_port=3306, db_pass="mysql", local_infile=0, encoding="utf8"):
        
        self.Con = mysql.connect(host=db_host, user=db_user, passwd=db_pass, local_infile=local_infile, charset=encoding)
        self.dry_run = False

        self.set_variable("NAMES", encoding)
        self.set_variable("CHARACTER SET", encoding)
        self.set_variable("autocommit", 0)
        self.set_variable("unique_checks", 0)
        self.set_variable("foreign_key_checks", 0)
        self._encoding = encoding

    def start_transaction(self):
        cur = self.Con.cursor()
        self.execute(cur, "START TRANSACTION")

    def has_database(self, database_name):
        cur = self.Con.cursor()
        self.execute(cur, "SHOW DATABASES")
        try:
            for x in cur:
                if x[0] == database_name.split()[0]:
                    return database_name
        except mysql.ProgrammingError as ex:
            if cur:
                print(cur.messages)
            else:
                print(self.Con.messages)
        return False

    def create_database(self, database_name):
        cur = self.Con.cursor()
        self.execute(cur, "CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(database_name.split()[0]))
        return

    def use_database(self, database_name):
        cur = self.Con.cursor()
        self.execute(cur, "USE {}".format(database_name.split()[0]))
        self.db_name = database_name

    def execute(self, cursor, command, override=False):
        if verbose:
            logger.info(command)
        try:
            if not self.dry_run or override:
                return cursor.execute(command)
            else:
                return True
        except Exception as e:
            print
            print
            print command
            raise e

    def has_table(self, table_name):
        cur = self.Con.cursor()
        return self.execute(cur, "SELECT * FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}'".format(self.db_name, table_name), override=True)

    def load_data(self, table_name, path, arguments=""):
        cur = self.Con.cursor()
        return self.execute(cur, "LOAD DATA LOCAL INFILE '{}' INTO TABLE {} {}".format(path, table_name, arguments))

    def create_table(self, table_name, description, override=False):
        cur = self.Con.cursor()
        return self.execute(cur, 'CREATE TABLE {} ({})'.format(table_name, description), override=override)
    
    def drop_table(self, table_name):
        cur = self.Con.cursor()
        return self.execute(cur, 'DROP TABLE {}'.format(table_name))

    def has_index(self, table_name, index_name):
        cur = self.Con.cursor()
        return self.execute(cur, 'SHOW INDEX FROM %s WHERE Key_name = "%s"' % (table_name, index_name), override=True)
    
    def create_index(self, table_name, index_name, variables, index_type, index_length):
        cur = self.Con.cursor()
        self.execute(cur, "SELECT * FROM {} LIMIT 1".format(table_name))
        if not cur.fetchone():
            return
        if index_length:
            variables = ["%s(%s)" % (variables[0], index_length)]
        if index_type:
            self.execute(cur, 'CREATE INDEX {} ON {}({}) USING {}'.format(index_name, table_name, ",".join(variables), index_type))
        else:
            self.execute(cur, 'CREATE INDEX {} ON {}({})'.format(index_name, table_name, ",".join(variables)))
            
    def get_field_type(self, table_name, column_name):
        cur = self.Con.cursor()
        self.execute(cur, "SHOW FIELDS FROM %s WHERE Field = '%s'" % (table_name, column_name), override=True)
        Results = unicode(cur.fetchone())
        if Results:
            field_type = Results[1]
            if Results[2] == "NO":
                field_type += " NOT NULL"
            return unicode(field_type)
        else:
            return None
        
    def get_optimal_field_type(self, table_name, column_name):
        cur = self.Con.cursor()
        self.execute(cur, "SELECT %s FROM %s PROCEDURE ANALYSE()" % (column_name, table_name), override=True)
        return str(cur.fetchone()[-1])
        
    def modify_field_type(self, table_name, column_name, new_type):
        cur = self.Con.cursor()
        old_field = self.get_field_type(table_name, column_name)
        self.execute(cur, "ALTER TABLE %s MODIFY %s %s" % (table_name, column_name, new_type))

    def read_table(self, table_name, FUN):
        cur = self.Con.cursor(MySQLdb.cursors.SSCursor)
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
        cur = self.Con.cursor()
        self.execute(cur, 'SELECT MAX(%s) FROM %s' % (column_name, table_name), override=True)
        try:
            return int(max(0, cur.fetchall() [0] [0]))
        except (TypeError, ValueError):
            return None

    def get_number_of_rows(self, table_name):
        cur = self.Con.cursor()
        self.execute(cur, 'SELECT COUNT(*) FROM %s' % (table_name), override=True)
        try:
            return int(max(0, cur.fetchall() [0] [0]))
        except TypeError:
            return None        

    def find(self, table_name, values, additional_variables=[], case=False):
        """ Obtain all records from table_name that match the column-value
        pairs given in the dict values."""
        cur = self.Con.cursor(mysql_cursors.DictCursor)
        variables = values.keys() + additional_variables
        where = []
        for column, value in values.items():
            where.append('{} = "{}"'.format(column, unicode(value).replace('"', '""')))
        if case:
            S = "SELECT {} FROM {} WHERE BINARY {}".format(", ".join(variables), table_name, " AND BINARY ".join(where))
        else:
            S = "SELECT {} FROM {} WHERE {}".format(", ".join(variables), table_name, " AND ".join(where))
        S = S.replace("\\", "\\\\")
        self.execute(cur, S, override=True)
        return cur.fetchall()

    def insert(self, table_name, data):
        cur = self.Con.cursor()
        # take care of quote characters and backslashes:
        new_data = copy.copy(data)
        for x in new_data:
            new_data[x] = "%s" % unicode(new_data[x]).replace('"', '""')
            new_data[x] = new_data[x].replace("\\", "\\\\")

        S = "INSERT INTO {}({}) VALUES({})".format(
            table_name, ",".join(new_data.keys()), ",".join('"%s"' % x for x in new_data.values()))
        self.execute(cur, S)
        for x in data:
            if not isinstance(data[x], (unicode, str, long, int)):
                print(x)
                print(data)
                print(S)
                asd
        return

    def insert_id(self):
        return self.Con.insert_id()

    def set_variable(self, variable, value):
        cur = self.Con.cursor()
        if isinstance(value, (str, unicode)):
            self.execute(cur, "SET {} '{}'".format(variable, value), override=True)
        else:
            self.execute(cur, "SET {}={}".format(variable, value), override=True)
        
    def commit(self):
        if not self.dry_run:
            self.Con.commit()

    def rollback(self):
        if not self.dry_run:
            self.Con.commit()

    def close(self):
        self.Con.commit()
        self.Con.close()