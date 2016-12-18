
import os
from os.path import dirname
import sys
import MySQLdb

root_path = dirname(dirname(os.getcwd()))
require_path = os.path.join(root_path, 'lib/simplequery')
sys.path.append(require_path)

print(require_path)

from table_data import *
from simplequery import *


def usage():
    print("""Help:
    python datachain.py simplequery.sq [argv1]
        """)

"""
Run file with argv[]
"""
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit()

    e = SimpleQueryExecutor()
    
    filename = sys.argv[1]
    params = None
    if len(sys.argv) > 2:
        params = sys.argv[2:]
    if os.path.exists(filename):
        e.run_file(filename, params)


