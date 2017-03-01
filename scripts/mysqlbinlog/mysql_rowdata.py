
from mysqlbinlog import *
from abc import ABCMeta, abstractmethod


class MySQLRowDataHandler:
    current_table_name = None
    reader = None

    @abstractmethod
    def insert_data(self, data, header):
        pass

    @abstractmethod
    def update_data(self, data, header):
        pass

    @abstractmethod
    def delete_data(self, data, header):
        pass


"""
"""
class MySQLRowData:
    def __init__(self, handler, filename):
        self.handler = handler
        self.filename = filename
        self.reader = BinlogReader(filename)
        
        # set a concern event list
        self.reader.set_concern_events([
            EventType.STOP_EVENT,
            EventType.ROTATE_EVENT, 
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
        # counter = 0 # TODO
        for result in self.reader.read_all_events(forever=forever, sleep=0.1):
            
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

