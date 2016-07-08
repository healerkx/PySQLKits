

from prettytable import PrettyTable
import webbrowser
import MySQLdb
from runtime import *
from evaluator import *



def dict_to_list(dataset, filters, exec_states):
    result = []
    
    for item in filters:
        if isinstance(item, str):
            result.append(dataset[item])
        elif isinstance(item, tuple) and item[0] == 'func':
            func_name = item[1]
            params = item[2]
            filed = None
            val = None
            if len(params) > 0:
                # The first param MUST be field
                if params[0][0] != 'param':
                    print(params)
                    exit()
                field = params[0][1][1]
                val = dataset[field]

            f = Func(func_name, [val])
            ret = Funcs.call(f, exec_states)

            result.append(ret)
    
    return result


def print_table(datesets, filters, exec_states):
    if filters is not None:
        filter_list = get_filter_list(filters)
    else:
        filter_list = handle.get_default_fields()
    x = PrettyTable(filter_list)
    for dataset in datesets:
        row = dict_to_list(dataset, filters, exec_states)
        x.add_row(row)
    return x


def get_filter_list(filters):
    filter_list = []
    for item in filters:
        if isinstance(item, str):
            filter_list.append(item)
        elif isinstance(item, tuple) and item[0] == 'func':
            params = item[2]
            field = params[0][1][1]
            filter_list.append(field)
    return filter_list


    

@buildin
def p(exec_states, handle):
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

            table = print_table(datesets, filters, exec_states)
            print(table)
            return True
    return False


@buildin
def today(exec_states, offset=0):
    import datetime
    today_start = str(datetime.date.today() + datetime.timedelta(offset))
    today_end = str(datetime.date.today() + datetime.timedelta(offset + 1))
    return (today_start, today_end)


@buildin
def yes(exec_states, val):
    # print("Yes", val)
    return 'Yes' if val == 1 else 'No'

@buildin
def fopen(exec_states, filename):
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
def fclose(exec_states, handle):
    assert(isinstance(handle, Handle))
    if handle.get_type() == 'file':
        handle.get_value().close()
        return True
    return False


@buildin
def mysql(exec_states, host, username, passwd, database=''):
    params = {'host': host, 'user': username, 'passwd': passwd, 'charset': 'utf8'}
    if len(database) > 0:
        params['db'] = database
    conn = MySQLdb.connect(**params)
    
    obj = MySQLConnectionObject(conn)
    obj.set_database(database)
    return obj

@buildin
def redis(exec_states, host, database):
    conn = None
    # TODO:
    obj = RedisConnectionObject(conn)
    return obj

@buildin
def render(exec_states, handle):
    assert(isinstance(handle, Handle))
    if handle.get_type() == 'file':
        url = handle.get_name()
        webbrowser.open(url) 
        return True

    # Only support File name as a param
    return False

from runtime import *



"""
"""
if __name__ == '__main__':
    from simplequery2sql import *
    func = Func('@p', [1333])
    l = Funcs.call(func)
    print(l)
