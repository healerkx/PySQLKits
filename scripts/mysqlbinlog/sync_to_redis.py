
# pip install redis

import redis
from mysqlbinlog import *
from mysql_rowdata import *
import json

class RedisHandler(MySQLRowDataHandler):
    client = None
    reader = None
    concern_tables = []
    def __init__(self):
        pass

    def get_redis(self):
        try:
            # Seems no need to try Redis
            self.client = redis.Redis(host='127.0.0.1', port=6379, db=0)
            print("dbsize=", self.client.dbsize())
            return self.client
        except Exception as e:
            print("-" * 40)
            print(e)
            print("-" * 40)
            exit()

    def get_json(self, item):
        print("$", self.current_table_name)
        if self.table_define is None or self.current_table_name not in self.table_define:
            return json.dumps(item)
        table_define = self.table_define[self.current_table_name]
        d = dict()
        idx = 0
        for field in table_define:
            d[field] = item[idx]
            idx += 1
        return json.dumps(d)




"""
Test main
"""
if __name__ == '__main__':
    handler = RedisHandler()
    br = MySQLRowData(handler, 'f:\\MySQL\\log\\data.000001')

    # set a concern event list
    br.read_loop(True)

