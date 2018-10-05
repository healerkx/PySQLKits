
import os
import sys
from os.path import dirname
from optparse import OptionParser

root_path = dirname(dirname(os.getcwd()))
require_path = os.path.join(root_path, 'scripts/mysqlbinlog')
sys.path.append(require_path)

from mysqlbinlog import *

from mysqlbinlog import *
from mysql_rowdata import *
import json

COLOR_RESET       = "\x1b[0m"
COLOR_RED         = "\x1b[31m"
COLOR_GREEN       = "\x1b[32m"
COLOR_YELLOW      = "\x1b[33m"
COLOR_BOLD_WHITE  = "\x1b[1;37m"

class WatcherHandler(MySQLRowDataHandler):
    def __init__(self, db_name_pattern, table_name_pattern):
        self.concern_tables = None
        self.db_name_pattern = db_name_pattern
        self.table_name_pattern = table_name_pattern

    def prints(self, header, data):
        print("%s[%s]%s %s" % (COLOR_BOLD_WHITE, header.time(), COLOR_RESET, data))

    def prints2(self, header, data):
        print("%s[%s]%s [" % (COLOR_BOLD_WHITE, header.time(), COLOR_RESET), end='')
        for i in data:
            if isinstance(i, tuple):
                print("%s(%s -> %s)%s" % (COLOR_YELLOW, i[0], i[1], COLOR_RESET), end=', ')
            else:
                print(i, end=', ')
        print(']\n')

    def insert_data(self, data, header):
        print('%sINSERT INTO%s %s.%s' % (COLOR_GREEN, COLOR_RESET, self.current_db_name, self.current_table_name))
        self.prints(header, data[0])

    def update_data(self, data, header):
        print('%sUPDATE%s %s.%s' % (COLOR_YELLOW, COLOR_RESET, self.current_db_name, self.current_table_name))
        idx = 0
        length = min(len(data[0]), len(data[1]))
        display = []
        
        while idx < length:
            origin = data[0][idx]
            current = data[1][idx]
            if origin != current:
                display.append((origin, current))
            else:
                display.append(origin)
            idx += 1
                
        self.prints2(header, display)
        

    def delete_data(self, data, header):
        print('%sDELETE FROM%s %s.%s' % (COLOR_RED, COLOR_RESET, self.current_db_name, self.current_table_name))
        self.prints(header, data[0])

    @staticmethod
    def match(pattern, name):
        if pattern == '%':
            return True
        if '%' in pattern:
            p = pattern.replace('%', '')
            return p in name
        return pattern == name

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
    

def watch(db_name_pattern, table_name_pattern, binlog_file, options):
    # print(db_name_pattern, table_name_pattern, binlog_file)
    
    handler = WatcherHandler(db_name_pattern, table_name_pattern)
    
    if os.path.exists(binlog_file):
        br = MySQLRowData(handler, binlog_file)

        if options.begin_time:
            print('Read events after %s' % options.begin_time)
            br.read_after(options.begin_time)
            
        # set a concern event list
        br.read_loop(True)
    else:
        print('Invalid binlog file given.')
        exit()          


def main(options, args):
    pattern = options.table_name_pattern
    db_name_pattern = '%'
    
    if '.' in pattern:  # db name given
        db_name_pattern, table_name_pattern = pattern.split('.')
    else:
        table_name_pattern = pattern

    binlog_file = options.binlog_file
    if not binlog_file:
        print('No binlog file provided')
        exit()
    
    watch(db_name_pattern, table_name_pattern, binlog_file, options)


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-t", "--table", action="store",
                    dest="table_name_pattern", help="Provide table name pattern, using % as the wildchar")

    parser.add_option('-s', '--sleep', action="store",
                    dest="sleep_seconds", help="Provide read binlog file minimal sleep seconds")

    parser.add_option('-b', '--binlog', action="store",
                    dest="binlog_file", help="Provide read binlog filename")

    parser.add_option('-a', '--begin-time', action="store",
                    dest="begin_time", help="Provide read binlog from time")                    

    options, args = parser.parse_args()
    main(options, args)



