
import sys
sys.path.append('D:\\Projects\\PySQLKits\\lib\\simplequery')

from simplequery import *


def table_data(file, *data):
    pass


@buildin
def t(handle, *data):
    print("$$$" * 40)
    f = handle.get_value()
    if f is not None:
        table_data(f, *data)
    return None