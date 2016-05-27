
import datetime

def is_sym(sym):
    return sym[0] == 'sym'

def sym_to_str(sym):
    if len(sym) == 2:
        return sym[1]
    else:
        return sym_to_str(sym[1]) + '.' + sym[2]


class Arg:
    def __init__(self):
        self.__name = None

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return "<%s=%s>" % (self.__name, self.__value)


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

"""
"""
class SimpleQueryTranslator:
    exec_states = []

    def set_exec_states(self, exec_states):
        self.exec_states = exec_states

    def get_param_symbol_str(symbol):
        return symbol[1]

    def get_param_assign_str(assign):
        return "="

    def get_param_str(param):
        p = param[1]
        if isinstance(p, tuple):
            if p[0] == 'assign':
                return get_param_assign_str(p)
            elif p[0] == 'sym':
                return get_param_symbol_str(p)
        elif isinstance(p, str):
            return "'%s'" % p
        elif isinstance(p, int) or isinstance(p, float):
            return "%s" % p

    def get_field_value(self, var, field):
        dataset_list = self.get_val_value(var)
        values = []
        for dataset in dataset_list:
            values.append(dataset[field])
        return values

    def get_val_value(self, var):
        dataset_list = []
        for exec_state in self.exec_states:
            if var == exec_state[0]:
                dataset_list = list(exec_state[1])
                break
        return dataset_list     

    def get_symbol_value(self, sym_str):
        var = sym_str
        if '.' in sym_str:
            var, field = sym_str.split('.')
            values = self.get_field_value(var, field)
            return values
        else:
            return self.get_val_value(var)


    def can_convert_to_sql(self, statement):
        body = statement[2]
        if body[0] == 'func':
            func_name = body[1]
            if not func_name.startswith('@'):
                return True
        return False

    def is_buildin_call(self, statement):
        body = statement[2]
        if body[0] == 'func':
            func_name = body[1]
            if func_name.startswith('@'):
                return True
        return False        

    def get_select_condition(self, assign):
        lvalue = assign[1]
        rvalue = assign[2]

        if isinstance(rvalue, str):
            return "%s = '%s'" % (lvalue, rvalue)
        elif isinstance(rvalue, int):
            return "%s = %s" % (lvalue, rvalue)
        elif isinstance(rvalue, float):
            return "%s = %s" % (lvalue, rvalue)
        elif is_sym(rvalue):
            if rvalue[1] == '@today':
                today_start = str(datetime.date.today())
                today_end = str(datetime.date.today() + datetime.timedelta(1))
                return "%s >= '%s' AND %s <= '%s'" % (lvalue, today_start, lvalue, today_end)
            a = sym_to_str(rvalue)
            value = self.get_symbol_value(a)

            value_list = ",".join(map(lambda x: "%s" % x, value))
            equals = "%s in (%s)" % (lvalue, value_list)
            return equals

    def get_select_orderby_limit(self, assign):
        return ""

    def get_select_conditions(self, param_list):
        conditions = []
        for param in param_list:
            body = param[1]
            if body[0] == 'assign' and not body[1].startswith('@'):
                conditions.append(self.get_select_condition(body))
        return ' AND '.join(conditions)

    def parse_arg(self, body):
        return None

    def get_args(self, param_list):
        args = []
        for param in param_list:
            body = param[1]
            if isinstance(body, tuple):
                param_type = body[0]
                if param_type == 'assign' and not body[1].startswith('@'):
                    args.append(body)
                elif param_type == 'sym':
                    arg = Arg()
                    sym_str = sym_to_str(body)
                    
                    arg.name = sym_str
                    arg.value = self.get_symbol_value(sym_str)
                    print("~~~", arg)
                    args.append(arg)
            elif isinstance(body, int):
                args.append(body)
            elif isinstance(body, str):
                args.append(body)

        return args

    """
    :param: exec_states []
    """
    def simple_query_to_sql(self, statement):
        receiver_name = statement[1]
        body = statement[2]
        if body[0] == 'func':
            table_name = body[1]
            param_list = body[2]

            conditions = self.get_select_conditions(param_list)

            sql = "select * from %s where %s" % (table_name, conditions)
            # print(sql)
            return sql
        return None

    def simple_query_to_call(self, statement):
        receiver_name = statement[1]
        body = statement[2]
        if body[0] == 'func':
            func_name = body[1]
            param_list = body[2]

            args = self.get_args(param_list)

            return Func(func_name, args)
            
        return None        