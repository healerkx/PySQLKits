
from simplequeryhandle import *
import webbrowser

buildin_funcs = dict()


"""
"""
def buildin(func):
    func_name = '@' + func.__name__
    buildin_funcs[func_name] = func
    return func

@buildin
def p(handle):
    print('@' * 40)
    print(handle)
    if handle.get_type() == 'dataset':
        datesets = handle.get_value()
        for dataset in datesets:
            print(dataset)
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
        # print("exec func => ", func_name)
        buildin_func = buildin_funcs[func_name]
        return buildin_func(*func.args)

"""
"""
if __name__ == '__main__':
    from simplequery2sql import *
    func = Func('@p', [1333])
    l = Funcs.call(func)
    print(l)
