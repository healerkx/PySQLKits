
import datetime
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
class SimpleQueryTranslator:
    exec_states = []

    def set_exec_states(self, exec_states):
        self.exec_states = exec_states


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
            elif isinstance(v, list):
                vlist = ','.join(map(lambda x: "%s" % x, v))
                return "%s in (%s)" % (field, vlist)
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
    :param: exec_states []
    """
    def simple_query_to_sql(self, statement):
        receiver_name = statement[1]
        body = statement[2]
        if body[0] == 'query':
            table_name = body[1]
            param_list = body[2]

            conditions, other_rules = self.get_select_conditions(param_list)
            print("#", conditions)
            sql = "select * from %s" % table_name
            if len(conditions.strip()) > 0:
                sql += ' where %s %s' % (conditions, other_rules)
            print(sql)
            return sql
        return None


            
