import struct
import decimal
from mysqldef import *


dh = DescriptorHandler()

def pb(b):
    print("=" * 40)
    for i in b:
        print(i)
    print("=" * 40)    


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

@dh.handle(FieldType.FLOAT)
class float_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 0
        
    def parse(self, data):
        c = data[0:4]
        d = data[4:]
        f, = struct.unpack('<f', c)
        return f, d

@dh.handle(FieldType.DOUBLE)
class double_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 0
        
    def parse(self, data):
        c = data[0:8]
        d = data[8:]
        f, = struct.unpack('<d', c)
        return f, d

@dh.handle(FieldType.NEWDECIMAL)
class decimal_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 2
        self.precision = metadata[0]
        self.decimals =  metadata[1]
        print(self.precision, self.decimals) # ? print

    """
    https://github.com/wenerme/myfacility/blob/master/binlog/decimal.go
    http://python-mysql-replication.readthedocs.io/en/latest/_modules/pymysqlreplication/row_event.html
    """
    def parse(self, bytes):
    #def __read_new_decimal(self, column):
        """Read MySQL's new decimal format introduced in MySQL 5"""

        # This project was a great source of inspiration for
        # understanding this storage format.
        # https://github.com/jeremycole/mysql_binlog

        digits_per_integer = 9
        compressed_bytes = [0, 1, 1, 2, 2, 3, 3, 4, 4, 4]
        integral = self.precision - self.decimals
        uncomp_integral = int(integral / digits_per_integer)
        uncomp_fractional = int(self.decimals / digits_per_integer)
        comp_integral = integral - (uncomp_integral * digits_per_integer)
        comp_fractional = self.decimals - (uncomp_fractional * digits_per_integer)

        data = bytearray(bytes)

        # Support negative
        # The sign is encoded in the high bit of the the byte
        # But this bit can also be used in the value
        value = data[0]
        if value & 0x80 != 0:
            res = ""
            mask = 0
        else:
            mask = -1
            res = "-"

        byte = struct.pack('<B', value ^ 0x80)
        data[0] = BigEndian.uint8(byte)

        size = compressed_bytes[comp_integral]

        if size > 0:
            i = BigEndian.uint_by_size(data, size)
            data = data[size:]
            value = i ^ mask
            res += str(value)

        for i in range(0, uncomp_integral):
            b = data[0:4]
            data = data[4:]
            value = struct.unpack('>i', b)[0] ^ mask

            res += '%09d' % value

        res += "."

        for i in range(0, uncomp_fractional):
            b = data[0:4]
            data = data[4:]
            value = struct.unpack('>i', b)[0] ^ mask
            res += '%09d' % value

        size = compressed_bytes[comp_fractional]
        if size > 0:
            i = BigEndian.uint_by_size(data[0:size], size)
            data = data[size:]
            value = i ^ mask
            res += '%0*d' % (comp_fractional, value)

        return decimal.Decimal(res), data

# DATETIME
@dh.handle(FieldType.DATETIME2)
class datetime_descriptor(base_descriptor):
    def __init__(self, metadata):
        self.metadata_len = 1
        self.ms_precision = metadata[0]
        # print("TIME MS PRECISION=", self.ms_precision)

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
