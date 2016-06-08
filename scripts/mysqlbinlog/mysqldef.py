
import time

class EventType : 
    UNKNOWN_EVENT = 0
    START_EVENT_V3 = 1
    QUERY_EVENT = 2
    STOP_EVENT = 3
    ROTATE_EVENT = 4
    INTVAR_EVENT = 5
    LOAD_EVENT = 6
    SLAVE_EVENT = 7
    CREATE_FILE_EVENT = 8
    APPEND_BLOCK_EVENT = 9
    EXEC_LOAD_EVENT = 10
    DELETE_FILE_EVENT = 11
    NEW_LOAD_EVENT = 12
    RAND_EVENT = 13
    USER_VAR_EVENT = 14
    FORMAT_DESCRIPTION_EVENT = 15
    XID_EVENT = 16
    BEGIN_LOAD_QUERY_EVENT = 17
    EXECUTE_LOAD_QUERY_EVENT = 18
    TABLE_MAP_EVENT  = 19
    PRE_GA_WRITE_ROWS_EVENT  = 20
    PRE_GA_UPDATE_ROWS_EVENT  = 21
    PRE_GA_DELETE_ROWS_EVENT  = 22
    """
    From MySQL 5.1.18 events
    """    
    WRITE_ROWS_EVENT  = 23
    UPDATE_ROWS_EVENT  = 24
    DELETE_ROWS_EVENT  = 25
    # ----------------------------------

    INCIDENT_EVENT = 26
    HEARTBEAT_LOG_EVENT = 27

    """
    From MySQL 5.6.2 events
    """
    WRITE_ROWS_EVENT2 = 30
    UPDATE_ROWS_EVENT2 = 31
    DELETE_ROWS_EVENT2 = 32
    # ----------------------------------

    

def from_unixtime(timestamp):
    x = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', x)


def get_table_id(b1, b2, b3):
    return b3 * (2 ** 32)  + b2 * (2 * 16) + b1

def pbytes(bytes, delimiter='--', prefix='@@'):
    print(delimiter * 20)
    for i in bytes:
        print(prefix, i)
    print(delimiter * 20)

class EventHandler:
    def __init__(self):
        self.handlers = dict()

    """
    Decorator for Event handler
    """
    def handle(self, event):
        def handler(func):
            self.handlers[event] = func # Register a event handler

        return handler

    def get_handler(self, event):
        if event in self.handlers:
            return self.handlers[event]
        else:
            return self.handlers[EventType.UNKNOWN_EVENT]


class DescriptorHandler:
    def __init__(self):
        self.handlers = dict()

    """
    Decorator for Field decriptor handler
    """
    def handle(self, col_type):
        def handler(clz):
            self.handlers[col_type] = clz # Register a event handler
            return clz
        return handler

    def get_handler_class(self, col_type):
        if col_type in self.handlers:
            return self.handlers[col_type]
        else:
            return self.handlers[FieldType.UNKNOWN]


class EventHeader:
    #__slots__ = []
    def __init__(self, header_info):
        self.timestamp = header_info[0]
        self.type_code = header_info[1]
        self.server_id = header_info[2]
        self.event_len = header_info[3]
        self.next_pos = header_info[4]
        self.flags = header_info[5]

    def __str__(self):
        return "[%s] %d %d %d %d" % (from_unixtime(self.timestamp), 
            self.type_code, self.server_id, self.event_len, self.next_pos)

    def time(self):
        return "%s" % from_unixtime(self.timestamp)


class FieldType:
    UNKNOWN =       -1
    DECIMAL =     0
    TINY =        1
    SHORT =       2
    LONG =        3
    FLOAT =       4
    DOUBLE =      5
    NULL =        6
    TIMESTAMP =   7
    LONGLONG =    8
    INT24 =       9
    DATE =        10
    TIME =        11
    DATETIME =    12
    YEAR =        13
    NEWDATE =     14
    VARCHAR =     15
    BIT =         16
    TIMESTAMP2 =  17
    DATETIME2 =   18
    TIME2 =       19
    NEWDECIMAL =  246
    ENUM =        247
    SET =         248
    TINY_BLOB =   249
    MEDIUM_BLOB = 250
    LONG_BLOB =   251
    BLOB =        252
    VAR_STRING =  253
    STRING =      254
    GEOMETRY =    255

    @staticmethod
    def to_name(field):
        for (k, v) in FieldType.__dict__.items():
            if v == field:
                return k
        return ""



class BigEndian:

    

    @staticmethod
    def uint8(b):
        return b[0]

    @staticmethod
    def uint16(b):
        return b[0] <<8 | b[1]

    @staticmethod
    def uint24(b):
        return b[0] <<16 | b[1] <<8 | b[2]

    @staticmethod
    def uint32(b):
        return b[0] <<24 | b[1] <<16 | b[2] <<8 | b[3]

    @staticmethod
    def uint40(b):
        return (b[0]) <<32 | (b[1]) <<24 | (b[2]) <<16 | (b[3]) <<8 | (b[4])