
import ply.lex as lex
import ply.yacc as yacc
import MySQLdb

from simplequerydef import *
from simplequery2sql import *
from simplequeryfuncs import *

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

    def __dump_exec_states(self):
        for exec_state in self.exec_states:
            print(exec_state) 

    def __exec_query(self, receiver, sql):
        with self.conn.cursor(MySQLdb.cursors.DictCursor) as cursor:
            r = cursor.execute(sql)

            results = cursor.fetchall()
            handle = Handle()
            handle.set_type('dataset')
            handle.set_name(receiver)
            handle.set_value(results)
            exec_state = (receiver, handle, sql)
            self.exec_states.append(exec_state)
            return True
        return False

    def __exec(self, receiver, func):
        print("~", receiver, func)
        result = Funcs.call(func)
        return result

    def __add_params(self, *params):
        receiver = 'argv'
        handle = Handle()
        handle.set_type('array')
        handle.set_name(receiver)
        handle.set_value(*params)
        exec_state = (receiver, handle, None)
        self.exec_states.append(exec_state)
        

    def __run_statement(self, statement):
        print(statement)
        receiver = statement[1]
        t = SimpleQueryTranslator()
        if t.can_convert_to_sql(statement):
            t.set_exec_states(self.exec_states)
            sql = t.simple_query_to_sql(statement)
            if self.conn is None:
                assert(False)

            if self.__exec_query(receiver, sql):
                self.__dump_exec_states()
        elif t.is_buildin_call(statement):
            t.set_exec_states(self.exec_states)
            func = t.simple_query_to_call(statement)
            # call func and get return value
            handle = self.__exec(receiver, func)
            exec_state = (receiver, handle)
            self.exec_states.append(exec_state)
            

    def run_code(self, code, params):
        s = SimpleQueryStatements()
        statements = s.parse(code)
        self.__add_params(params)

        for statement in statements:
            # print(statement)
            self.__run_statement(statement)
            print('=' * 40)
            print()

    def run_file(self, filename, params=None):
        with open(filename, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            self.run_code(''.join(lines), [2])

