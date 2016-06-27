
import datetime
from simplequeryhandle import *
from simplequeryfuncs import *

def sym_to_str(symbol):
    if len(symbol) == 2:
        return symbol[1]
    else:
        return sym_to_str(symbol[1]) + '.' + symbol[2]


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

class Evaluator:

    def __init__(self, exec_states):
        self.exec_states = exec_states

    
    def get_params(self, param_list):
        args = []
        for param in param_list:
            body = param[1]
            if isinstance(body, tuple):
                param_type = body[0]
                if param_type == 'assign' and not body[1].startswith('@'):
                    args.append(body)
                elif param_type == 'sym':
                    sym_str = sym_to_str(body)
                    value = self.get_symbol_value(sym_str)
                    args.append(value)
                elif param_type == 'arrval':
                    value = self.get_array_value(body)
                    args.append(value)
                elif param_type == 'filter':
                    value = self.get_filter_value(body)
                    args.append(value)
            elif isinstance(body, int):
                args.append(body)
            elif isinstance(body, str):
                args.append(body)

        return args        
    
    def get_func_obj(self, statement):
        body = statement[2]
        assert(body[0] == 'func')
        func_name = body[1]
        param_list = body[2]
        args = self.get_params(param_list)

        return Func(func_name, args)

    def exec_func(self, statement):
        func = self.get_func_obj(statement)
        ret = Funcs.call(func)
        return ret

    def get_filter_value(self, body):
        sym = body[1]
        filters = body[2]
        handle = self.get_val_value(sym_to_str(sym))
        handle.set_filters(filters)
        return handle

    # Get variable value (pattern 'a') as a Handle
    def get_val_value(self, var):
        for exec_state in self.exec_states:
            if var == exec_state[0]:
                return exec_state[1]
        raise Exception('Undefined symbol %s' % var)

    # get a symbol value with pattern 'a.b'
    def get_field_value(self, var, field):
        handle = self.get_val_value(var)
        if handle.get_type() != 'dataset':
            return []

        dataset_list = handle.get_value()
        values = []
        for dataset in dataset_list:
            values.append(dataset[field])
        return values

    def get_symbol_value(self, sym_str):
        var = sym_str
        if '.' in sym_str:
            var, field = sym_str.split('.')
            values = self.get_field_value(var, field)
            return values
        else:
            return self.get_val_value(var)

    # Get symbol[index] value
    def get_array_value(self, array_access):
        sym = array_access[1]
        index = array_access[2]
        sym_str = sym_to_str(sym)
        arr_handle = self.get_symbol_value(sym_str)
        array = arr_handle.get_value()
        if sym_str == 'argv':
            assert isinstance(array, list)
        if index < len(array):
            val = array[index]
            return val 
        else:
            raise Exception("Out of array bound")


    def get_value(self, e):
        print("EEEE", e)
        if e[0] == 'arrval':
            return self.get_array_value(e)
        elif e[0] == 'sym':
            sym_str = sym_to_str(e)
            v = self.get_symbol_value(sym_str)
            return v
        elif e[0] == 'func':
            if e[1] == '@today':
                today_start = str(datetime.date.today())
                today_end = str(datetime.date.today() + datetime.timedelta(1))
                return (today_start, today_end)
            return "Call"
