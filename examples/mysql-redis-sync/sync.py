
import os
import sys
from os.path import dirname

root_path = dirname(dirname(os.getcwd()))
require_path = os.path.join(root_path, 'scripts\\mysqlbinlog')
sys.path.append(require_path)

from sync_to_redis import *
import json


class ExampleRedisHandler(RedisHandler):
    def __init__(self):
        self.client = self.get_redis()
        self.concern_tables = []
        # user add table define here
        self.table_define = {
            'kx_user': ['user_id', 'user_name', 'company_id', 'user_mobile', 'user_age', 'user_avatar', 'user_resume', 'province', 'city', 'county', 'status', 'create_time', 'update_time']
        }

    def insert_data(self, data):
        item = data[0]
        json = self.get_json(item)
        self.client.hset("user", item[0], json)

    def update_data(self, data):
        print("update", data)
        item = data[1]
        json = self.get_json(item)
        self.client.hset("user", item[0], json)

    def delete_data(self, data):
        item = data[0]
        self.client.hdel("user", item[0])




"""
Test main
"""
if __name__ == '__main__':

    handler = ExampleRedisHandler()
    br = MySQLRowData(handler, 'f:\\MySQL\\log\\data.000001')

    # set a concern event list
    br.read_loop(True)