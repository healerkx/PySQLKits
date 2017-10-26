
from .SqObject import *

class RedisConnectionObject(SqObject):

    def __init__(self, conn):
        super(SqObject, self)
        self.set_value(conn)
        self.database = 0

    def set_database(self, database):
        self.database = database
    
    def exec(self, command):
        return self.conn.get(command)

    
    @staticmethod
    def exec_command(conn, database, key_name, params):
        # conn.select(int(database)) # conn is a connection to a database...
        if conn.type(key_name) == b'string':
            value = conn.get(key_name)
            return value.decode()
        return None
