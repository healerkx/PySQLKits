
# pip install redis

import redis
import MySQLdb
from mysqlbinlog import *
from mysql_rowdata import *
import json


class RedisHandler(MySQLRowDataHandler):
    client = None
    reader = None
    concern_tables = []
    fields_map = {}

    def __init__(self):
        pass

    def get_redis(self, host='127.0.0.1', port=6379):
        try:
            # Seems no need to try Redis
            self.client = redis.Redis(host = host, port = port, db = 0)
            print("dbsize=", self.client.dbsize())
            return self.client
        except Exception as e:
            print("-" * 40)
            print(e)
            print("-" * 40)
            exit()

    def load_fields_map(self, user, passwd, db, host='127.0.0.1', port=3306):
        if len(self.concern_tables) == 0:
            return

        db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset="utf8")
        with db.cursor() as cursor:
            for table in self.concern_tables:
                cursor.execute('SHOW FULL COLUMNS FROM `%s`;' % table)
                e = cursor.fetchall()
                self.fields_map[table] = list(map(lambda x:x[0], e))
        # print(self.fields_map)   
    
    def append_fields_info(self, table_name, table_fields):
        self.fields_map[table_name] = table_fields

    """
    """
    def get_json(self, data, expected_fields=None):
        table_name = self.current_table_name
        if self.fields_map is None or table_name not in self.fields_map:
            if expected_fields is None:
                return json.dumps(data)
            else:
                parts = []
                for index in expected_fields:
                    parts.append(data[index])
                return json.dumps(parts)

        # 
        fields = self.fields_map[table_name]

        d = dict()
        idx = 0
        for field in fields:
            if expected_fields is not None and field not in expected_fields:
                continue

            d[field] = data[idx]
            idx += 1
        return json.dumps(d)

    def set_current_table(self, data, header):
        if self.reader is None:
            print('Binlog Reader can NOT be None')
            exit()
        table_name = data[2]
        self.current_table_name = table_name

        self.reader.skip_next = False        
        if table_name not in self.concern_tables:
            self.reader.skip_next = True



"""
Test main
"""
if __name__ == '__main__':
    handler = RedisHandler()
    br = MySQLRowData(handler, 'f:\\MySQL\\log\\data.000001')

    # set a concern event list
    br.read_loop(True)

