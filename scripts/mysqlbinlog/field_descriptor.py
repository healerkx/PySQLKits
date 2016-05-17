import struct
from mysqldef import *

dh = DescriptorHandler()


class base_descriptor:
    def handle(self, metadata):
        if self.metadata_len == 0:
            return metadata
        return metadata[self.metadata_len:]

    def parse(self, data):
        return None, data

    @property
    def nullable(self):
        return self.__nullable

    @nullable.setter
    def nullable(self, value):
        self.__nullable = value

    def get_max_len(self):
        if 'max_len' in self.__dict__:  # TODO:
            return self.max_len
        return '@'

@dh.handle(FieldType.UNKNOWN)
class unknown_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 0

    def __str__(self):
        return "<Unknown> %d" % self.col_type

@dh.handle(FieldType.TINY)
class tiny_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 0

    def parse(self, data):
        c = data[0:1]
        d = data[1:]
        i, = struct.unpack('=B', c)
        return i, d


@dh.handle(FieldType.SHORT)
class short_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 0

    def parse(self, data):
        c = data[0:2]
        d = data[2:]
        i, = struct.unpack('=H', c)
        return i, d

@dh.handle(FieldType.LONG)
class long_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 0

    def parse(self, data):
        c = data[0:4]
        d = data[4:]
        i, = struct.unpack('=I', c)
        return i, d

@dh.handle(FieldType.DECIMAL)
class decimal_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 0

    def parse(self, data):
        c = data[0:4]
        d = data[4:]
        return struct.unpack('=I', c), d

# DATETIME
@dh.handle(FieldType.DATETIME2)
class datetime_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 1
        self.ms_precision = metadata[0]
        print("TIME MS PRECISION=", self.ms_precision)

    # Ref: https://github.com/dropbox/godropbox/blob/master/database/binlog/temporal_fields.go
    def parse(self, data):
        c = data[0:5]
        
        msec = 0
        if self.ms_precision == 1 or self.ms_precision == 2:
            msec = BigEndian.uint8(data[5:6]) * 10000
            data = data[6:]
        elif self.ms_precision == 3 or self.ms_precision == 4:
            msec = BigEndian.uint16(data[5:7]) * 100
            data = data[7:]
        elif self.ms_precision == 5 or self.ms_precision == 6:
            msec = BigEndian.uint24(data[5:8])
            data = data[8:]
        else:
            data = data[5:]

        datetimef_int_offset = 0x8000000000

        t = BigEndian.uint40(c) - datetimef_int_offset
        ymd = t >> 17
        ym = ymd >> 5
        hms = t % (1 << 17)

        day = ymd % (1 << 5)
        month = ym % 13
        year = ym / 13

        second = hms % (1 << 6)
        minute = (hms >> 6) % (1 << 6)
        hour = hms >> 12

        dt = "%02d-%02d-%02d %02d:%02d:%02d.%03d" % (year, month, day, hour, minute, second, msec // 1000)
        return dt, data



# VARCHAR, STRING
"""
VARCHAR
"""
@dh.handle(FieldType.VARCHAR)
class varchar_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 2
        self.max_len = metadata[0] | metadata[1] * 256

    def parse(self, data):
        plen = 2
        ptype = 'H'
        if self.max_len < 256:
            plen = 1
            ptype = 'B'
        strlen, = struct.unpack(ptype, data[0:plen])
        sbytes = data[plen:plen + strlen]
        s, = struct.unpack('=%ds' % strlen, sbytes)
        return s.decode('utf8'), data[plen + strlen:]


@dh.handle(FieldType.STRING)
class char_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 2
        self.max_len = metadata[0] | metadata[1] * 256

    def parse(self, data):
        strlen, = struct.unpack('B', data[0:1])
        bytes = data[1:1 + strlen]
        s = struct.unpack('=%ds' % strlen, bytes)
        return s, data[strlen + 1:]

#----------------------------------------------------------
"""
"""     
def get_descriptor(col_type, metadata, nullable):

    handler_class = dh.get_handler_class(col_type)
    handler = handler_class(metadata)
    if handler_class is unknown_descriptor:
        handler.col_type = col_type
    
    handler.nullable = nullable
    metadata = handler.handle(metadata)

    # print(handler.nullable)

    return handler, metadata
