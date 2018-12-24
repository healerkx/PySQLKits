

# Lex
tokens = (
    'NS',
    'NAME',
    'FLOAT',
    'INT',
    'STR',
    'COMMA',
    'DOT',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'EQU',
    'GT',
    'LT',
    'GTE',
    'LTE',
    'TO'
)

t_COMMA     = r','
t_DOT       = r'.'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_EQU       = r'='
t_GT        = r'>'
t_LT        = r'<'
t_GTE       = r'>='
t_LTE       = r'<='
t_TO        = r'=>'

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


def t_NS(t):
    r'@[_A-Za-z0-9]*'
    t.type = reserved.get(t.value, 'NS')    # Check for reserved words
    lex_print(t)
    return t

def t_NAME(t):
    r'[A-Za-z_][_A-Za-z0-9]*'
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
    r'\'([^\'\\\n]|(\\.))*?\''
    t.value = t.value.strip("\"'")
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    # symprint("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore            = r" \t"
t_ignore_COMMENT    = r'\#.*'
######################################################################
# yacc
def p_error(p):
    yacc_print("Error?", p)

def p_expr(p):
    """expr         : INT
                    | FLOAT
                    | STR
                    | symbol
                    | arrayaccess
                    | func"""
    p[0] = p[1]

def p_symbol(p):
    """symbol       : NAME
                    | symbol DOT NAME"""
    yacc_print('symbol', p)
    if len(p) == 2:
        p[0] = ('sym', p[1])
    elif len(p) == 4:
        p[0] = ('sym', p[1], p[3])

def p_arrayaccess(p):
    """arrayaccess  : symbol LBRACKET expr RBRACKET"""
    yacc_print('arrayaccess', p)
    if len(p) == 5:
        p[0] = ('arrayaccess', p[1], p[3])

def p_list_items(p):
    """list_items   : list_items COMMA expr
                    | expr"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

# [1, 2, ....]
def p_list(p):
    """list         : LBRACKET list_items RBRACKET"""
    p[0] = p[2]


def p_param(p):
    """param        : expr"""
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
    """func         : NS DOT NAME params
                    | NAME params"""
    if len(p) > 3:
        print("--" * 4)
        print(len(p), p[3], p[4])
        p[0] = ('func', p[3], p[4], p[1])
    else:
        p[0] = ('func', p[1], p[2], '<@build-in>')
    
def p_statement(p):
    """statement    :   expr TO expr"""
    p[0] = ("statement", p[1], p[3])

"""
yacc start 
"""
def p_statements(p):
    """statements   :   statements statement
                    |   statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


if __name__ == '__main__':
    import ply.lex as lex
    import ply.yacc as yacc

    use_lex_print = True
    use_yacc_print = True
    lex.lex()
    parser = yacc.yacc(start = 'statements')
    
    code = """
@mysql.hash(aa) => b.f
f(a.b) => b.c
"""
    statements = parser.parse(code)
    print("=" * 40)
    print(statements)
    for s in statements:
        print(s)
