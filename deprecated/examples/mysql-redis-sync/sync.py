
import os
import sys
from os.path import dirname

root_path = dirname(dirname(os.getcwd()))
require_path = os.path.join(root_path, 'scripts\\mysqlbinlog')
sys.path.append(require_path)

from sync_to_redis import *
import json


# TODO: Loading HOT data only, not from data.000001, too much time to load


"""
Example for flush data into Redis from reading MySQL binlog files.
"""
class ExampleRedisHandler(RedisHandler):
    def __init__(self):
        self.client = self.get_redis()
        self.concern_tables = ['kx_user', 'kx_order']
        # user add table define here
        self.load_fields_map('root', 'root', 'test')

        # if you want add fields info not from load_fields_map
        # self.append_fields_info('kx_user', [])
        
    """
    Business coding here
    """
    def insert_data(self, data, header):
        if self.current_table_name == 'kx_user':
            item = data[0]
            json = self.get_json(item, [])
            self.client.hset("user", item[0], json)
        elif self.current_table_name == 'kx_order':
            item = data[0]
            json = self.get_json(item, [])
            self.client.hset("order", item[0], json)

    def update_data(self, data, header):
        if self.current_table_name == 'kx_user':
            item = data[1]
            json = self.get_json(item)
            self.client.hset("user", item[0], json)
        elif self.current_table_name == 'kx_order':
            item = data[1]
            json = self.get_json(item)
            self.client.hset("order", item[0], json)

    def delete_data(self, data, header):
        if self.current_table_name == 'kx_user':
            item = data[0]
            self.client.hdel("user", item[0])
        elif self.current_table_name == 'kx_order':
            item = data[0]
            self.client.hdel("order", item[0])



"""
Test main
"""
if __name__ == '__main__':

    handler = ExampleRedisHandler()
    binlog_filename = os.path.join(root_path, 'scripts\\mysqlbinlog\\logs\\redis\\data.000001')
    if os.path.exists(binlog_filename):
        br = MySQLRowData(handler, binlog_filename)

        # set a concern event list
        br.read_loop(False)