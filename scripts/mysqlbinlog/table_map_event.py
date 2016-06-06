from mysqldef import *
from table_map_event import *
from field_descriptor import *

# http://bugs.mysql.com/bug.php?id=37426
# http://lists.mysql.com/commits/48751
def parse_type_length(bytes):
    pass

def parse_table_map(col_types, metadata, nullable_bits):

    col_count = len(col_types)
    nullable_list = []
    for i in range(0, col_count):
        bit = (nullable_bits[i // 8]) & (1 << (i % 8))
        nullable_list.append(bit != 0)

    # print(nullable_list)
    i = 0
    handlers = []
    for col_type in col_types:
        nullable = nullable_list[i]
        # print(i, col_type, FieldType.to_name(col_type))
        # Notice, NOT VARCHAR=15
        if col_type == FieldType.VAR_STRING or col_type == FieldType.STRING:
            parse_type_length(metadata)
        i += 1
        # TODO: more

        handler, metadata = get_descriptor(col_type, metadata, nullable)
        handlers.append(handler)
        # print("MAX-Len", handler.get_max_len())
    return handlers

