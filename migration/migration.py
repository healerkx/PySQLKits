

import pymysql, re, sys
from pymysql.cursors import DictCursor

class Field:
    def __init__(self, table, field, converter=None):
        self.__table = table
        self.__field = field
        self.__converter = converter

    def table(self):
        return self.__table

    def field_name(self):
        return self.__field


class Table:
    def __init__(self, database, table):
        self.__database = database
        self.__table = table

    def database(self):
        return self.__database

    def field(self, field, converter=None):
        return Field(self, field, converter)

class Connection:
    def __init__(self, conn):
        self.conn = conn

    def db(self, database):
        print(database)
        return Database(self.conn)


class Database:
    def __init__(self, conn):
        self.conn = conn

    def table(self, table):
        return Table(self, table)

class Receiver:
    __key_values = {}
    __migration = None

    def __init__(self, migration):
        self.__dict__['__migration'] = migration
        setattr(self, '__migration', migration)

    def __get_condition(self):
        
        return getattr(self, '__migration').get_condition()

    def __setattr__(self, field, value):
        if field in self.__dict__:
            self.__dict__[field] = value
        else:
            condition = self.__get_condition()
            condition.set(field, value)

class Condition:
    __pairs = {}
    
    def __init__(self, database, table, field, condition):
        self.database = database
        self.table = table
        self.field = field
        self.condition = condition

    def set(self, field, value):
        # print("set", field, value)
        self.__pairs[field] = value

    def pairs(self):
        return self.__pairs

class Migration:

    __condition = None

    def __init__(self):
        pass

    def connect(self, server, username, passwd, port=3306):
        try:
            self.conn = pymysql.connect(host=server, user=username, passwd=passwd, port=port, charset="utf8")
            print("Server [%s:%d] connected" % (server, port))
            conn = Connection(self.conn)
            return conn
        except:
            print("Server [%s:%d] failed to connect" % (server, port))
            exit()        

    def receiver(self):
        return Receiver(self)

    def begin(self, field, condition=None):
        table = field.table()
        database = table.database()
        if not self.__condition:
            self.__condition = Condition(database, table, field, condition)

    def end(self):
        return self.__condition

    def get_condition(self):
        return self.__condition

    def generate(self):
        if self.__condition:
            self.__generate(self.__condition)

    def __generate(self, condition):
        cursor = self.conn.cursor(DictCursor)
        cursor.execute("select * from kits.pet")
        data = cursor.fetchall()
        for item in data:
            for (d, s) in condition.pairs().items():
                print(d, s, item[s.field_name()])


if __name__ == "__main__":
    
    m = Migration()
    conn = m.connect("127.0.0.1", "root", "root")
    table = conn.db("kits").table('pet')

    r = m.receiver()
    
    m.begin(table.field("id"), lambda x: x % 2 == 0)
    r.id = table.field('pet_id')
    r.created_at = table.field('pet_name')
    m.end()

    m.generate()



