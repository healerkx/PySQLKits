
import struct
import time
from mysqldef import *
from table_map_event import *

BINLOG_FILE_HEADER = b'\xFE\x62\x69\x6E'

BINLOG_EVENT_HEADER_LEN = 19    # (32 + 8 + 32 + 32 + 32 + 16) / 8



eh = EventHandler()



"""
"""
class BinlogReader:
    """
    """
    def __init__(self, filename):
        self.file = None
        self.current_binlog_file = None
        self.openfile(filename)
        self.concern_events = []
        self.skip_next = False

    def openfile(self, filename):
        if self.file is not None:
            self.file.close()
            print(self.current_binlog_file + " closed")
            self.file = None

        self.file = open(filename, 'rb')
        if self.file is None:
            exit()
        self.current_binlog_file = filename
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

    def read_string(self, length, encoding='utf-8'):
        c = self.read_bytes(length)
        s = c.decode(encoding).strip('\0x')
        return s

    def open_next_binlog_file(self, filename=None):
        if filename is None:
            dot = self.current_binlog_file.rindex('.')
            next_binlog_id = int(self.current_binlog_file[dot + 1:]) + 1
            filename = self.current_binlog_file[:dot] + ('.%06d' % next_binlog_id)
        self.openfile(filename)

    def set_concern_events(self, concern_events):
        self.concern_events = concern_events

    def is_concern_event(self, event):
        if self.concern_events is None or len(self.concern_events) == 0:
            return True
        return event in self.concern_events

    """
    Only handle MySQL event header v4 (MySQL 5.0+) 
    """
    def read_event_header(self):
        c = self.read_bytes(BINLOG_EVENT_HEADER_LEN)
        if len(c) > 0:
            header_info = struct.unpack('=IBIIIH', c)
            header = EventHeader(header_info)
            return header
        return None
    
    """
    eh.handle decorate a method to register a handler against an event-type
    """
    @eh.handle(EventType.UNKNOWN_EVENT)
    def read_unknown_event(self, header):
        event_len = header.event_len
        # print(event_len)
        # seek for Unknown type event
        c = self.read_bytes(event_len - BINLOG_EVENT_HEADER_LEN)
        return c

    """
    TODO:
    """
    @eh.handle(EventType.ROTATE_EVENT)
    def read_rotate_event(self, header):
        # TODO: Read payload
        self.open_next_binlog_file()

        return ()

    @eh.handle(EventType.STOP_EVENT)
    def read_stop_event(self, header):
        self.open_next_binlog_file()
        return ()

    @eh.handle(EventType.QUERY_EVENT)
    def read_query_event(self, header):
        post_header_len = 13
        c = self.read_bytes(post_header_len)
        post_header = struct.unpack('=IIBHH', c) #
        # print(post_header)
        schema_len = post_header[2]
        status_vars_len = post_header[4]
        s = self.read_bytes(schema_len + status_vars_len + 1)

        # print(schema_len, status_vars_len)
        size = header.event_len - BINLOG_EVENT_HEADER_LEN - post_header_len - schema_len - status_vars_len - 1 
        sql_bytes = self.read_bytes(size - 4)
        sql = struct.unpack('=%ds' % (size - 4), sql_bytes)

        # According to the following code, # LINE 75-76
        # 5.6 Specific:
        # (optional) 4 bytes footer for checksum.
        # https://github.com/dropbox/godropbox/blob/master/database/binlog/query_event.go
        checksum = self.read_bytes(4)
        return (sql)

    @eh.handle(EventType.FORMAT_DESCRIPTION_EVENT)
    def read_format_description_event(self, header):
        c = self.read_bytes(57)
        
        description = struct.unpack('=H50sIB', c) #
        binlog_version = description[0]
        if binlog_version != 4:
            print("Only binlog v4 can be handled")
            exit()
        server_version = description[1].decode('utf-8').strip('\x00')
        create_time = description[2]
        event_header_len = description[3]
        assert(event_header_len == 19)
        
        length_array = self.read_bytes(header.event_len - (57 + 19))
        """
        for length in length_array:
            print(length) # each event type header length
        """
        # Notice: seems MySQL some version has an end-of-event \x00. BUT 5.7 dose NOT have.
        return ()
    

    @eh.handle(EventType.TABLE_MAP_EVENT)
    def read_table_map_event(self, header):
        c = self.read_bytes(9)  # post_header_len: table_id(6) + flags(2) + dbname_len(1)
        i1, i2, i3, flags, dbname_len = struct.unpack('=HHHHB', c)

        table_id = get_table_id(i1, i2, i3)
        dbname = self.read_string(dbname_len + 1)
        tablename_len = self.read_uint8()
        tablename = self.read_string(tablename_len + 1)
        
        # print("`%s`.`%s`" % (dbname, tablename))
        # 16 = 9(post_header_len) + 1(\x0) + 1(\x0) + 1(tablename_len) + 4(chunksum)
        data_len = header.event_len - BINLOG_EVENT_HEADER_LEN - 16 - dbname_len - tablename_len
        data = self.read_bytes(data_len)

        print("<<"*10)
        for i in data:
            pass
            #print('d', i)

        col_count, size = self.read_field_length(data)
        # print(col_count, size)

        col_types = data[size:size + col_count]
        
        data = data[size + col_count:]
        metadata_size, size = self.read_field_length(data)
        
        metadata = data[size:size + metadata_size]
        data = data[size + metadata_size:]
        # print(data)
        # print("---", metadata_size, metadata)
        nullable_bits_size = (col_count + 7) // 8
        nullable_bits = data[:nullable_bits_size]

        #pbytes(metadata)
        field_discriptors = parse_table_map(col_types, metadata, nullable_bits)
        self.cur_field_discriptors = field_discriptors
        chunksum = self.read_bytes(4)
        return (table_id, dbname, tablename)

    def bytes_2_leuint(self, bytes):
        val = 0
        i = 0
        for b in bytes:
            val += int(b << (int(i) * 8))
            print('-', val)
            i += 1
        
        return val
    

    def read_field_length(self, bytes):
        if len(bytes) == 0:
            return -1, 0
        val = int(bytes[0])
        if val < 251:
            return val, 1
        elif val == 251:
            return -1, 0

        size = 9
        if val == 252:
            size = 3
        elif val == 253:
            size = 4
        
        if len(bytes) < size:
            return -1, 0
        return self.bytes_2_leuint(bytes[1:size]), size

    """
    """
    def read_row_values(self, col_count, data):
        items = []
        null_array = []
        for i in range(0, col_count):
            is_null = (data[i // 8] & (1 << (i % 8))) != 0 # is_null OK?
            null_array.append(is_null)
        starts = (col_count + 7) // 8
        remain = data[starts:]

        #print(self.cur_field_discriptors)
        for i in range(0, col_count):
            
            fd = self.cur_field_discriptors[i]
            is_null = null_array[i]
            if not is_null:
                value, remain = fd.parse(remain)
                # print('value', value)
                items.append(value)
            else:
                items.append(None)
        return items, remain
    

    """
    insert, update, delete
    """
    def read_rows_event(self, header, update=False):
        post_header_len = 8
        c = self.read_bytes(post_header_len)
        # table_id mask by 0x00ffffff
        i1, i2, i3, flags = struct.unpack('=HHHH', c)
        table_id = get_table_id(i1, i2, i3)
        if flags & 0x1 != 0:
            pass    # end of statement

        print("table_id=%d" % table_id)    # TODO: check the table_id
        extra_data_len = 0
        if True: # MySQL 5.6
            extra_data_len = 2
            c = self.read_bytes(extra_data_len)
            extra_data_len, = struct.unpack('=H', c)
            if extra_data_len > 2:
                c = self.read_bytes(extra_data_len - 2)
                # print(c)
                rw_extra_info_tag, extra_row_len, extra_data = struct.unpack('=BB%ds' % (extra_data_len - 2), c)
                assert(rw_extra_info_tag == 0)
        

        data_len = header.event_len - BINLOG_EVENT_HEADER_LEN - post_header_len - extra_data_len
        data = self.read_bytes(data_len - 4)

        col_count, size = self.read_field_length(data)
        data = data[size:]
        print(col_count, size)

        bmp1_size = int((col_count + 7) / 8)
        bmp2_size = int((col_count + 7) / 8)
        bmp = data[: bmp1_size + bmp2_size]
        print(bmp)
        
        remain = data[bmp1_size:]
        if update:
            remain = data[bmp1_size + bmp2_size:]

        items, remain = self.read_row_values(col_count, remain)
        items2 = None
        if update:
            items2, _ = self.read_row_values(col_count, remain)

        # chucksum
        chucksum = self.read_bytes(4)

        return (items, items2)

    """
    insert values
    """
    @eh.handle(EventType.WRITE_ROWS_EVENT2)
    def read_write_rows_event(self, header):
        items = self.read_rows_event(header)
        return items

    """
    update
    """
    @eh.handle(EventType.UPDATE_ROWS_EVENT2)
    def read_update_rows_event(self, header):
        items = self.read_rows_event(header, True)
        return items

    @eh.handle(EventType.DELETE_ROWS_EVENT2)
    def read_delete_rows_event(self, header):
        items = self.read_rows_event(header)
        return items

    def bytes_2_leuint(self, bytes):
        val = 0
        i = 0
        for b in bytes:
            val += int(b << (int(i) * 8))
            print('-', val)
            i += 1
        
        return val
    

    def read_field_length(self, bytes):
        if len(bytes) == 0:
            return -1, 0
        val = int(bytes[0])
        if val < 251:
            return val, 1
        elif val == 251:
            return -1, 0

        size = 9
        if val == 252:
            size = 3
        elif val == 253:
            size = 4
        
        if len(bytes) < size:
            return -1, 0
        return self.bytes_2_leuint(bytes[1:size]), size


    """
    Doc says the payload contain 8 bytes, but 12 found in fact.
    """
    @eh.handle(EventType.XID_EVENT)
    def read_xid_event(self, header):
        c = self.read_bytes(12)
        xid, _ = struct.unpack('=Q4s', c) #
        return xid

    """
    File event loop
    """
    def read_all_events(self, forever=False):
        default_handler = eh.get_handler(EventType.UNKNOWN_EVENT)
        while True:
            header = self.read_event_header()
            if header is None:
                if forever:
                    time.sleep(1)
                    continue
                else:
                    break

            if not self.is_concern_event(header.type_code) or self.skip_next:
                # Skip this event
                default_handler(self, header)
                continue

            print(header)
            handler = eh.get_handler(header.type_code)
            results = handler(self, header)
            yield (header.type_code, results)




"""
Test main
"""
if __name__ == '__main__':

    br = BinlogReader('f:\\MySQL\\log\\data.000001')

    # set a concern event list
    # br.set_concern_events([EventType.TABLE_MAP_EVENT])
    
    # print all handlers registered
    # print(eh.handlers)
    for e in br.read_all_events():
        print(e)
    
