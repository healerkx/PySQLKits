
import os
import sys

sys.path.append('D:\\Projects\\PySQLKits\\scripts\\mysqlbinlog')

from mysqlbinlog import *
from mysql_rowdata import *
import json


class TracebackHandler(MySQLRowDataHandler):
    def __init__(self):
        pass

    def insert_data(self, data):
        print(1)
        pass

    def update_data(self, data):
        print(2)
        pass

    def delete_data(self, data):
        print(3)
        pass

    def set_current_table(self, data):
        table_name = data[2]
        self.current_table_name = table_name
        self.reader.skip_next = False
        if self.concern_tables is not None:
            if table_name in self.concern_tables:
                self.reader.skip_next = True
"""
Test main
"""
if __name__ == '__main__':

    binlog_filename = os.path.join('D:\\Projects\\PySQLKits\\scripts\\mysqlbinlog', 'logs\\traceback\\data.000001')
    handler = TracebackHandler()
    br = MySQLRowData(handler, binlog_filename)

    # set a concern event list
    br.read_loop(False)