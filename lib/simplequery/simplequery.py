
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


    def parse(self, code):
        statements = self.__compile(code)
        for statement in statements:
            yield statement

"""
SimpleQueryExecutor
"""
class SimpleQueryExecutor:
    conn = None

    def __init__(self):
        self.exec_states = []

    def set_connection(self, conn):
        self.conn = conn

    def __run_statement(self, statement):
        print(statement)
        t = SimpleQueryTranslator()
        if t.can_convert_to_sql(statement):
            t.set_exec_states(self.exec_states)
            sql = t.simple_query_to_sql(statement)
            if self.conn:
                cursor = self.conn.cursor()
                r = cursor.execute(sql)
                results = cursor.fetchall()
                exec_state = (statement[1], results)
                self.exec_states.append(exec_state)
                cursor.close()
            print("~", sql)
        else:
            pass

    def run(self, code):
        s = SimpleQueryStatements()
        statements = s.parse(code)
        for statement in statements:
            # print(statement)
            self.__run_statement(statement)


code = """
com = kx_company(company_id=4, time=@today, @limit=5, @asc=company_id);
@show(com, 5, '');
user = kx_user(user_id=13, name='healer', time=@today, status=com.a.status);
"""


if __name__ == '__main__':
    e = SimpleQueryExecutor()
    conn = None
    e.set_connection(conn)
    e.run(code)
    