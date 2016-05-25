
import datetime

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

def can_convert_to_sql(statement):
    body = statement[2]
    if body[0] == 'func':
        func_name = body[1]
        if not func_name.startswith('@'):
            return True
    return False

def is_sym(sym):
    return sym[0] == 'sym'

def sym_to_str(sym):
    return "SYM"

def get_select_condition(assign):
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
        equals = "%s = %s" % (lvalue, a)
        return equals

def get_select_orderby_limit(assign):
    return ""

def get_select_conditions(param_list):
    conditions = []
    for param in param_list:
        body = param[1]
        if body[0] == 'assign' and not body[1].startswith('@'):
            conditions.append(get_select_condition(body))
    return ' AND '.join(conditions)

def simple_query_to_sql(statement):
    receiver_name = statement[1]
    body = statement[2]
    if body[0] == 'func':
        table_name = body[1]
        param_list = body[2]

        conditions = get_select_conditions(param_list)

        sql = "select * from %s where %s" % (table_name, conditions)
        print(sql)
    return None