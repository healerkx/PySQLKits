
from simplequeryhandle import *
from prettytable import PrettyTable
import webbrowser

buildin_funcs = dict()


"""
"""
def buildin(func):
    func_name = '@' + func.__name__
    buildin_funcs[func_name] = func
    return func

def dict_to_list(dataset, filters):
    return [dataset[f] for f in filters]


def print_table(datesets, filters):
    filter_list = list(map(lambda x: x[1], filters))
    x = PrettyTable(filter_list)
    for dataset in datesets:
        row = dict_to_list(dataset, filter_list)
        x.add_row(row)
    print(x)

@buildin
def p(handle):
    if handle.get_type() == 'dataset':
        datesets = handle.get_value()
        filters = handle.get_filters()
        print_table(datesets, filters)
        return True
    return False


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
def render(handle):
    assert(isinstance(handle, Handle))
    if handle.get_type() == 'file':
        url = handle.get_name()
        webbrowser.open(url) 
        return True
    assert(False)
    # Only support File name as a param
    return False



class Funcs:
    @staticmethod
    def call(func):
        func_name = func.func_name
        buildin_func = buildin_funcs[func_name]
        print("exec func => ", func.args)
        return buildin_func(*func.args)

"""
"""
if __name__ == '__main__':
    from simplequery2sql import *
    func = Func('@p', [1333])
    l = Funcs.call(func)
    print(l)
