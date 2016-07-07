

from prettytable import PrettyTable
import webbrowser
import MySQLdb
from runtime import *

buildin_funcs = dict()


"""
"""
def buildin(func):
    func_name = '@' + func.__name__
    buildin_funcs[func_name] = func
    return func

def dict_to_list(dataset, filters):
    return [dataset[f] for f in filters]


def print_table(datesets, filter_list):
    x = PrettyTable(filter_list)
    for dataset in datesets:
        row = dict_to_list(dataset, filter_list)
        x.add_row(row)
    return x

@buildin
def p(handle):
    handle_type = type(handle)
    if handle_type == int or handle_type == str:
        print(handle)
        return True
    if SqObject.is_sq_object(handle):
        if isinstance(handle, MySQLConnectionObject):
            print(handle.conn)
            return True
        elif isinstance(handle, RedisConnectionObject):
            print("Redis")
            return True
        elif isinstance(handle, DatasetObject):
            datesets = handle.get_value()
            filters = handle.get_filters()
            if filters is not None:
                filter_list = list(map(lambda x: x[1], filters))
            else:
                filter_list = handle.get_default_fields()
            table = print_table(datesets, filter_list)
            print(table)
            return True
    return False


@buildin
def today(offset=0):
    import datetime
    today_start = str(datetime.date.today() + datetime.timedelta(offset))
    today_end = str(datetime.date.today() + datetime.timedelta(offset + 1))
    return (today_start, today_end)


@buildin
def fopen(filename):
    f = open(filename, 'w', encoding='UTF-8')
    handle = Handle()
    handle.set_type('file')
    handle.set_name(filename)
    handle.set_value(f)
    
    return handle


@buildin
def fwrite(handle, content):
    assert(isinstance(handle, Handle))
    f = handle.get_value()
    if f is not None:
        f.write(content)


@buildin
def fclose(handle):
    assert(isinstance(handle, Handle))
    if handle.get_type() == 'file':
        handle.get_value().close()
        return True
    return False


@buildin
def mysql(host, username, passwd, database=''):
    params = {'host': host, 'user': username, 'passwd': passwd, 'charset': 'utf8'}
    if len(database) > 0:
        params['db'] = database
    conn = MySQLdb.connect(**params)
    
    obj = MySQLConnectionObject(conn)
    obj.set_database(database)
    return obj

@buildin
def redis(host, database):
    conn = None
    # TODO:
    obj = RedisConnectionObject(conn)
    return obj

@buildin
def render(handle):
    assert(isinstance(handle, Handle))
    if handle.get_type() == 'file':
        url = handle.get_name()
        webbrowser.open(url) 
        return True

    # Only support File name as a param
    return False

"""
"""
class Func:
    func_name = None
    args = []

    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def __str__(self):
        """
        For dump the Func object
        """
        args_str_list = []
        for arg in self.args:
            if isinstance(arg, str):
                arg = "'%s'" % arg
            args_str_list.append(str(arg))
        args_str = ', '.join(args_str_list)
        return "<%s(%s)>" % (self.func_name, args_str)

class Funcs:
    @staticmethod
    def call(func):
        func_name = func.func_name
        buildin_func = buildin_funcs[func_name]
        # print("exec func => ", *func.args)
        return buildin_func(*func.args)

"""
"""
if __name__ == '__main__':
    from simplequery2sql import *
    func = Func('@p', [1333])
    l = Funcs.call(func)
    print(l)
