
import datetime
from simplequeryhandle import *
from simplequeryvalues import *

def is_sym(sym):
    return sym[0] == 'sym'

def is_func(sym):
    return sym[0] == 'func'

def is_buildin_func(statement):
    body = statement[2]
    return body[0] == 'func' and body[1].startswith('@')

def is_query(statement):
    body = statement[2]
    return body[0] == 'query' and not body[1].startswith('@')




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

"""
"""
class SimpleQueryTranslator:
    exec_states = []

    def set_exec_states(self, exec_states):
        self.exec_states = exec_states



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

    # Get variable value (pattern 'a') as a Handle
    def get_val_value(self, var):
        for exec_state in self.exec_states:
            if var == exec_state[0]:
                return exec_state[1]
        raise Exception('Undefined symbol %s' % var)
  
    # get symbol value from str, a.b or a
    def get_symbol_value(self, sym_str):
        var = sym_str
        if '.' in sym_str:
            var, field = sym_str.split('.')
            values = self.get_field_value(var, field)
            return values
        else:
            return self.get_val_value(var)


    def get_filter_value(self, body):
        sym = body[1]
        filters = body[2]
        handle = self.get_val_value(sym_to_str(sym))
        handle.set_filters(filters)
        return handle

    def can_convert_to_sql(self, statement):
        body = statement[2]
        return body[0] == 'query'
            

    def get_rvalue(self, rvalue):
        e = Evaluator(self.exec_states)
        v = e.get_value(rvalue)
        
        return v
        
    """
    a > 1 ==> a > 1
    a > ''

    """
    def get_select_condition(self, relation, lvalue, rvalue):
        
        field = sym_to_str(lvalue)
        
        v = self.get_rvalue(rvalue)

        
        if relation != '=':
            return "%s %s '%s'" % (field, relation, v)
        else:
            if isinstance(v, tuple):
                return "%s >= '%s' and %s < '%s'" % (field, v[0], field, v[1])
            else:
                return "%s = '%s'" % (field, v)


    def get_select_orderby_limit(self, assign):
        return ""

    def get_select_conditions(self, condition_list):
        conditions = []
        rules = []
        for condition in condition_list:
            if condition[0] == 'condition':
                relation = condition[1] # == or >=, or ...
                lvalue = condition[2]
                rvalue = condition[3]
                if isinstance(lvalue, str) and lvalue.startswith('@'):
                    pass
                else:
                    condition = self.get_select_condition(relation, lvalue, rvalue)
                    if condition:
                        conditions.append(condition)
        return ' AND '.join(conditions), ' '.join(rules)



    """
    Get func's params
    """
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

    """
    :param: exec_states []
    """
    def simple_query_to_sql(self, statement):
        receiver_name = statement[1]
        body = statement[2]
        if body[0] == 'query':
            table_name = body[1]
            param_list = body[2]

            conditions, other_rules = self.get_select_conditions(param_list)
            print(conditions)
            sql = "select * from %s" % table_name
            if len(conditions.strip()) > 0:
                sql += ' where %s %s' % (conditions, other_rules)
            print(sql)
            return sql
        return None

    def get_func_obj(self, statement):
        body = statement[2]
        assert(body[0] == 'func')
        func_name = body[1]
        param_list = body[2]
        args = self.get_params(param_list)

        return Func(func_name, args)
            
