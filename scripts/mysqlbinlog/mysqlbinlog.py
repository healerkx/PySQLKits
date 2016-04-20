
import struct
import time
from mysqldef import *

BINLOG_FILE_HEADER = b'\xFE\x62\x69\x6E'

BINLOG_EVENT_HEADER_LEN = 19    # (32 + 8 + 32 + 32 + 32 + 16) / 8


def from_unixtime(timestamp):
    x = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', x)

class BinlogReader:


    def __init__(self, filename):
        self.file = open(filename, 'rb')
        header = self.read_bytes(4)
        if header != BINLOG_FILE_HEADER:
            print('It is NOT a MySQL binlog file.')
            exit()



    def read_bytes(self, count):
        c = self.file.read(count)
        return c

    def read_uint64(self):
        c = self.read_bytes(8)
        r, = struct.unpack('Q', c)
        return r

    def read_uint32(self):
        c = self.read_bytes(4)
        r, = struct.unpack('I', c)
        return r

    def read_uint16(self):
        c = self.read_bytes(2)
        r, = struct.unpack('H', c)

    def read_uint8(self):
        c = self.read_bytes(1)
        r, = struct.unpack('B', c)
        return r


    def read_event_header(self):
        c = self.read_bytes(BINLOG_EVENT_HEADER_LEN)
        if len(c) > 0:
            header = struct.unpack('=IBIIIH', c)
            return header
        return None

    def read_event(self, header):
        event_len = header[3]
        # print(event_len)
        self.read_bytes(event_len - 19) # seek for Unknown type event


    def read_format_description_event(self, header):
        c = self.read_bytes(57)
        event_len = header[3]
        event_header = struct.unpack('=H50sIB', c)
        server_version = event_header[1].decode('utf-8').strip('\x00')
        print(event_len - 57 - 19)
        event = self.read_bytes(event_len - (57 + 19))
        c = 0
        for b in event:
            #print(c, hex(b))
            c += 1
        # Notice: seems MySQL some version has an end-of-event \x00. BUT 5.7 dose NOT have.
        return (event_header[0], server_version, event_header[2], event_header[3])


    def read_events(self):
        while True:
            header = self.read_event_header()
            if header is None:
                break
            timestamp, type_code, server_id, event_len, next_pos, flags = header
            print(timestamp, type_code, server_id, event_len, next_pos, flags )
            if type_code == EventType.FORMAT_DESCRIPTION_EVENT:
                self.read_format_description_event(header)
            else:
                self.read_event(header)

        





if __name__ == '__main__':
    br = BinlogReader('f:\\MySQL\\log\\data.000001')
    br.read_events()
    
