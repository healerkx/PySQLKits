
import ply.lex as lex
import ply.yacc as yacc

from simplequerydef import *
from simplequery2sql import *

class SimpleQueryStatements:
    def __init__(self):
        pass

    def __dump(self, statements):
        s = 0
        for statement in statements:
            print("Statement(%d):" % s, statement)
            s += 1

    def __compile(self, code):
        lex.lex()
        parser = yacc.yacc(start = 'statements')
        
        statements = parser.parse(code)
        #self.__dump(statements)
        return statements

    def __run_statement(self, statement):
        print(statement)
        if can_convert_to_sql(statement):
            sql = simple_query_to_sql(statement)
            print(sql)
        else:
            pass
        

    def run(self, code):
        statements = self.__compile(code)
        for statement in statements:
            self.__run_statement(statement)

code = """
com = kx_company(company_id=4, time=@today, @limit=5, @asc=company_id);
@show(com, 5, '');
user = kx_user(user_id=13, name='healer', time=@today, status=com.a.status);
"""


if __name__ == '__main__':
    s = SimpleQueryStatements()
    s.run(code)
    