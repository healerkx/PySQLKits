
from .SqObject import *

class MySQLConnectionObject(SqObject):
    def __init__(self, conn):
        super().__init__()
        self.set_value(conn)

    def set_database(self, database):
        self.database = database

    def get_database(self):
        return self.database

    def use(self, database):
        self.set_database(database)

