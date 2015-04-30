from __future__ import unicode_literals 

import MySQLdb
import logging

verbose = False
name = ""
logger = None

class DBConnection(object):
    def __init__(self, db_name, local_infile=0):
        self.Con = MySQLdb.connect (host="localhost", user="mysql", passwd="mysql", db=db_name, local_infile=local_infile)
        cur = self.Con.cursor()
        self.db_name = db_name
        self.dry_run = False

        self.set_variable("autocommit", 0)
        self.set_variable("unique_checks", 0)
        self.set_variable("foreign_key_checks", 0)
        self.Con.commit()

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

    def has_index(self, table_name, index_name):
        cur = self.Con.cursor()
        return self.execute(cur, 'SHOW INDEX FROM %s WHERE Key_name = "%s"' % (table_name, index_name), override=True)
    
    def create_index(self, table_name, index_name, variables, index_type, index_length):
        cur = self.Con.cursor()
        if index_length:
            variables = ["%s(%s)" % (variables[0], index_length)]
        if index_type:
            self.execute(cur, 'CREATE INDEX {} ON {}({}) USING {}'.format(index_name, table_name, ",".join(variables), index_type))
        else:
            self.execute(cur, 'CREATE INDEX {} ON {}({})'.format(index_name, table_name, ",".join(variables)))
            
    def get_field_type(self, table_name, column_name):
        cur = self.Con.cursor()
        self.execute(cur, "SHOW FIELDS FROM %s WHERE Field = '%s'" % (table_name, column_name), override=True)
        Results = cur.fetchone()
        if Results:
            field_type = Results[1]
            if Results[2] == "NO":
                field_type += " NOT NULL"
            return field_type.upper()
        else:
            return None
        
    def get_optimal_field_type(self, table_name, column_name):
        cur = self.Con.cursor()
        self.execute(cur, "SELECT %s FROM %s PROCEDURE ANALYSE()" % (column_name, table_name), override=True)
        return cur.fetchone()[-1]
        
    def modify_field_type(self, table_name, column_name, new_type):
        cur = self.Con.cursor()
        old_field = self.get_field_type(table_name, column_name)
        self.execute(cur, "ALTER TABLE %s MODIFY %s %s" % (table_name, column_name, new_type))

    def read_table(self, table_name, FUN):
        cur = self.Con.cursor(MySQLdb.cursors.SSCursor)
        self.execute(cur, "SELECT * FROM %s" % table_name, override=True)
        D = {}
        for current_entry in cur.fetchall():
            D[FUN(current_entry)] = current_entry
        return D

    def get_max(self, table_name, column_name):
        cur = self.Con.cursor()
        self.execute(cur, 'SELECT MAX(%s) FROM %s' % (column_name, table_name), override=True)
        try:
            return int(max(0, cur.fetchall() [0] [0]))
        except TypeError:
            return None

    def get_number_of_rows(self, table_name):
        cur = self.Con.cursor()
        self.execute(cur, 'SELECT COUNT(*) FROM %s' % (table_name), override=True)
        try:
            return int(max(0, cur.fetchall() [0] [0]))
        except TypeError:
            return None        

    def find(self, table_name, column_name, value):
        cur = self.Con.cursor()
        self.execute(cur, 'SELECT {column} FROM {table} WHERE {column} = "{value}"'.format(
            table=table_name, column=column_name, value=value), override=True)
        return cur.fetchall()

    def set_variable(self, variable, value):
        cur = self.Con.cursor()
        self.execute(cur, 'SET {}={}'.format(variable, value), override=True)

    def insert(self, table_name, data):
        assert len(data) == (len(table_description[table_name]["CREATE"]) -1 )
        cur = self.Con.cursor()
        
        # take care of single quotation marks:
        if any("'" in str(x) for x in data):
            values = ", ".join(['"%s"' % x for x in data]).encode("utf-8")
        else:
            values = ", ".join(["'%s'" % x for x in data]).encode("utf-8")
        # take care of backslashes:
        values = values.replace("\\", "\\\\")

        S = "INSERT INTO {table} VALUES({values})".format(table = table_name, values = values)
        self.execute(cur, S)
        
    def commit(self):
        if not self.dry_run:
            self.Con.commit()

    def rollback(self):
        if not self.dry_run:
            self.Con.commit()
