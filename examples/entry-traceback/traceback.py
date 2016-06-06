
import os
import sys
from optparse import OptionParser
sys.path.append('D:\\Projects\\PySQLKits\\scripts\\mysqlbinlog')

from mysqlbinlog import *
from mysql_rowdata import *
import json


class TracebackHandler(MySQLRowDataHandler):
    def __init__(self, table_name, field, value):
        self.concern_tables = None  # use self.table_name
        self.table_name = table_name
        if field.isdigit():
            self.field_index = int(field)
        
        #TODO: Get self.field_index from field name
        self.value_str = str(value)

    def is_the_right_data(self, data):
        
        value_str = str(data[self.field_index])
        if self.value_str == value_str:
            return True
        return False

    def insert_data(self, data):
        if self.is_the_right_data(data[0]):
            print(data[0])

    def update_data(self, data):
        if self.is_the_right_data(data[1]):
            print(data[1])

    def delete_data(self, data):
        if self.is_the_right_data(data[0]):
            print(data[0])

    def set_current_table(self, data):
        table_name = data[2]
        if self.table_name != table_name:
            self.reader.skip_next = True
            return

        self.current_table_name = table_name
        self.reader.skip_next = False
        if self.concern_tables is not None:
            if table_name not in self.concern_tables:
                self.reader.skip_next = True
"""
Test main
"""
if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-t", "--table", action="store",
                  dest="table_name", help="Provide table name")

    parser.add_option("-f", "--field", action="store",
                  dest="field", help="Provide field name")

    parser.add_option("-i", "--field-index", action="store",
                  dest="field", help="Provide field name")

    parser.add_option("-v", "--value", action="store",
                  dest="value", help="Provide the value")

    sys.argv = ['_.py', '--table=kx_order', '--field-index=0', '--value=2']
    options, args = parser.parse_args()


    binlog_filename = os.path.join('D:\\Projects\\PySQLKits\\scripts\\mysqlbinlog', 'logs\\traceback\\data.000001')
    handler = TracebackHandler(options.table_name, options.field, options.value)
    br = MySQLRowData(handler, binlog_filename)

    # set a concern event list
    br.read_loop(False)