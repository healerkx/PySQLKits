

import os
import sys
from os.path import dirname
from optparse import OptionParser

root_path = dirname(dirname(os.getcwd()))
require_path = os.path.join(root_path, 'scripts/mysqlbinlog')
sys.path.append(require_path)
print(require_path)
from mysqlbinlog import *

from mysqlbinlog import *
from mysql_rowdata import *
import json


class WatcherHandler(MySQLRowDataHandler):
    def __init__(self, db_name_pattern, table_name_pattern):
        self.concern_tables = None
        self.db_name_pattern = db_name_pattern
        self.table_name_pattern = table_name_pattern

    def prints(self, header, data):
        print("[%s] %s" % (header.time(), data))

    def insert_data(self, data, header):
        print('INSERT INTO %s.%s' % (self.current_db_name, self.current_table_name))
        self.prints(header, data[0])

    def update_data(self, data, header):
        print('UPDATE %s.%s' % (self.current_db_name, self.current_table_name))
        self.prints(header, data[0])
        self.prints(header, data[1])

    def delete_data(self, data, header):
        print('DELETE FROM %s.%s' % (self.current_db_name, self.current_table_name))
        self.prints(header, data[0])

    @staticmethod
    def match(pattern, name):
        if pattern == '*':
            return True
        # TODO: How to match the name
        return True

    def set_current_table(self, data, header):
        db_name = data[1]
        table_name = data[2]

        if not WatcherHandler.match(self.table_name_pattern, table_name) or not WatcherHandler.match(self.db_name_pattern, db_name):
            self.reader.skip_next = True
            return
        
        self.current_db_name = db_name
        self.current_table_name = table_name
        self.reader.skip_next = False
        if self.concern_tables is not None:
            if table_name not in self.concern_tables:
                self.reader.skip_next = True
    

def watch(db_name_pattern, table_name_pattern, binlog_file):
    handler = WatcherHandler(db_name_pattern, table_name_pattern)
    
    if os.path.exists(binlog_file):
        br = MySQLRowData(handler, binlog_file)

        # set a concern event list
        br.read_loop(True)    


def main(options, args):
    pattern = options.table_name_pattern
    db_name_pattern = '*'
    if '.' in pattern:  # db name given
        db_name_pattern, table_name_pattern = pattern.split('.')
    else:
        table_name_pattern = pattern

    binlog_file = options.binlog_file
    watch(db_name_pattern, table_name_pattern, binlog_file)


if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option("-t", "--table", action="store",
                    dest="table_name_pattern", help="Provide table name pattern")

    parser.add_option('-s', '--sleep', action="store",
                    dest="sleep_seconds", help="Provide read binlog file minimal sleep seconds")

    parser.add_option('-b', '--binlog', action="store",
                    dest="binlog_file", help="Provide read binlog filename")


    """
    If can NOT connect MySQL service, neither nor fetch CREATE TABLE info
    parser.add_option("-f", "--field", action="store",
                      dest="field", help="Provide field name")
    """

    options, args = parser.parse_args()
    print(options)
    main(options, args)



