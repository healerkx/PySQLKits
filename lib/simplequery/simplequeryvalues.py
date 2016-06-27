
import datetime

def sym_to_str(symbol):
    if len(symbol) == 2:
        return symbol[1]
    else:
        return sym_to_str(symbol[1]) + '.' + symbol[2]

class Evaluator:

    def __init__(self, exec_states):
        self.exec_states = exec_states



    def get_func_return_value(self, call):
        return None

    # Get variable value (pattern 'a') as a Handle
    def get_val_value(self, var):
        for exec_state in self.exec_states:
            if var == exec_state[0]:
                return exec_state[1]
        raise Exception('Undefined symbol %s' % var)

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
        if e[0] == 'arrval':
            return self.get_array_value(e)
        elif False:
            pass
        elif e[0] == 'func':
            if e[1] == '@today':
                today_start = str(datetime.date.today())
                today_end = str(datetime.date.today() + datetime.timedelta(1))
                return (today_start, today_end)
            return "Call"
