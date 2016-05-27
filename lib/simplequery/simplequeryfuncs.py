

buildin_funcs = dict()

def buildin(func):
    func_name = '@' + func.__name__
    buildin_funcs[func_name] = func
    return func

@buildin
def p(c):
    print('-' * 40)
    print(c)
    return len(str(c))


class Funcs:
    @staticmethod
    def call(func):
        func_name = func.func_name
        buildin_func = buildin_funcs[func_name]
        return buildin_func(*func.args)

"""
"""
if __name__ == '__main__':
    from simplequery2sql import *
    func = Func('p', [1333])
    l = Funcs.call(func)
    print(l)
