
# pip install redis

import redis
from mysqlbinlog import *


class RedisHandler:
    def __init__(self):
        self.client = redis.Redis(host='127.0.0.1', port=6379, db=0)
        self.concern_tables = []
        self.reader = None

    def insert_data(self, data):
        pass

    def update_data(self, data):
        pass

    def delete_data(self, data):
        pass

    def set_current_table(self, data):
        table_name = data[1]
        self.reader.skip_next = False
        if self.concern_tables is not None:
            if table_name in self.concern_tables:
                self.reader.skip_next = True



class MySQLRowData:
    def __init__(self, handler, filename):
        self.handler = handler
        self.filename = filename
        self.reader = BinlogReader(filename)
                
        # set a concern event list
        self.reader.set_concern_events([
            EventType.TABLE_MAP_EVENT, 
            EventType.WRITE_ROWS_EVENT2,
            EventType.UPDATE_ROWS_EVENT2, 
            EventType.DELETE_ROWS_EVENT2])

        self.handler.reader = self.reader

    """
    """
    def read_loop(self):
                    
        handler = self.handler

        # print all handlers registered
        # print(eh.handlers)
        for result in self.reader.read_all_events():
            event = result[0]
            data = result[1]
            if event == EventType.WRITE_ROWS_EVENT2:
                handler.insert_data(data)
            elif event == EventType.UPDATE_ROWS_EVENT2:
                handler.update_data(data)
            elif event == EventType.DELETE_ROWS_EVENT2:
                handler.delete_data(data)
            elif event == EventType.TABLE_MAP_EVENT:
                handler.set_current_table(data)




"""
Test main
"""
if __name__ == '__main__':
    handler = RedisHandler()
    br = MySQLRowData(handler)

    # set a concern event list
    br.read_loop('f:\\MySQL\\log\\data.000001')

