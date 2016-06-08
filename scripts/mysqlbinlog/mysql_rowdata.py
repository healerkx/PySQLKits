
from mysqlbinlog import *


class MySQLRowDataHandler:
    current_table_name = None
    reader = None
    concern_tables = []

    def __init__(self):
        pass

    def insert_data(self, data, header):
        pass

    def update_data(self, data, header):
        pass

    def delete_data(self, data, header):
        pass

    def set_current_table(self, data, header):
        if self.reader is None:
            print('Binlog Reader can NOT be None')
            exit()
        table_name = data[2]
        self.current_table_name = table_name
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
    def read_loop(self, forever):
                    
        handler = self.handler

        # print all handlers registered
        # print(eh.handlers)
        for result in self.reader.read_all_events(forever):
            event = result[0]
            data = result[1]
            header = result[2]
            if event == EventType.WRITE_ROWS_EVENT2:
                handler.insert_data(data, header)
            elif event == EventType.UPDATE_ROWS_EVENT2:
                handler.update_data(data, header)
            elif event == EventType.DELETE_ROWS_EVENT2:
                handler.delete_data(data, header)
            elif event == EventType.TABLE_MAP_EVENT:
                handler.set_current_table(data, header)

