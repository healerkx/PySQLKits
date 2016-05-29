
# Lex
tokens = (
    'NAME',
    'FLOAT',
    'INT',
    'STR',
    'COMMA',
    'SEMI',
    'DOT',
    'LPAREN',
    'RPAREN',
    'EQU',

)

t_COMMA     = ','
t_SEMI      = ';'
t_DOT       = '\.'
t_LPAREN    = '\('
t_RPAREN    = '\)'
t_EQU       = '='

reserved = {
    
}

use_lex_print = False
use_yacc_print = False


def lex_print(*p):
    if not use_lex_print:
        return
    print('Lex:', p)

def yacc_print(*p):
    if not use_yacc_print:
        return    
    print('Yacc:', p)


def t_NAME(t):
    r'[A-Za-z_@][_A-Za-z0-9]*'
    t.type = reserved.get(t.value, 'NAME')    # Check for reserved words
    lex_print(t)
    return t   

def t_FLOAT(t):
    r'\d+(\.\d+)'
    t.value = float(t.value)
    return t 

def t_INT(t):
    r'[+|-]?\d+'
    t.value = int(t.value)
    return t

def t_STR(t):
    r'\'.*\''
    t.value = t.value.strip("\"'")
    #symprint('%' * 40, t)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    # symprint("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore  = ' \t'
######################################################################
# yacc
def p_error(p):
    yacc_print("Error:", p)


def p_rvalue(p):
    """rvalue       : symbol
                    | INT
                    | FLOAT
                    | STR"""
    p[0] = p[1]

def p_symbol(p):
    """symbol       : NAME
                    | symbol DOT NAME"""
    yacc_print('symbol', p)
    if len(p) == 2:
        p[0] = ('sym', p[1])
    else:
        p[0] = ('sym', p[1], p[3])

def p_assign(p):
    """assign       : NAME EQU rvalue"""
    p[0] = ('assign', p[1], p[3])

def p_param(p):
    """param        : assign
                    | rvalue"""
    p[0] = ('param', p[1])

def p_param_list(p):    
    """param_list   : param_list COMMA param
                    | param"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_params(p):
    """params       : LPAREN param_list RPAREN
                    | LPAREN RPAREN"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_func(p):
    """func         :   NAME params"""
    p[0] = ('func', p[1], p[2])




"""
Statement
"""
def p_statememt(p):
    """statement    :   NAME EQU func SEMI
                    |   func SEMI"""
    if len(p) > 3:
        yacc_print("statement", p[1], p[3])
        p[0] = ("statement", p[1], p[3])
    else:    
        yacc_print("statement", '_r', p[1])
        p[0] = ("statement", '_r', p[1])

"""
yacc start 
"""
def p_statements(p):
    """statements   :   statements statement
                    |   statement """
    # print("#", len(p))
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])
    
