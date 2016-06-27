
import ply.lex as lex
import ply.yacc as yacc
import MySQLdb

from simplequerydef import *
from simplequery2sql import *
from simplequeryfuncs import *

def get_mysql_connection(**params):
    params = {'host':'localhost', 'user':'root', 'passwd':'root', 'db':"test"}
    conn = MySQLdb.connect(**params)

    with conn.cursor() as c:
        c.execute('show databases;')
        print(list(map(lambda x: x[0], c.fetchall())))
    return conn

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
        if statements is not None:
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

    def __exec_query(self, receiver, sql, table_name):
        with self.conn.cursor(MySQLdb.cursors.DictCursor) as cursor:
            r = cursor.execute(sql)

            results = cursor.fetchall()
            handle = Handle()
            handle.set_type('dataset')
            handle.set_name(receiver)
            handle.set_value(results)

            # set fields for order
            rows = cursor.execute('SHOW COLUMNS FROM %s' % table_name)
            columns = cursor.fetchall()
            fields = list(map(lambda x: x['Field'], columns))
            handle.set_default_fields(fields)
            
            exec_state = (receiver, handle, sql)
            self.__add_exec_state(exec_state)
            return True
        return False

    # append to exec_states and do more work here
    def __add_exec_state(self, exec_state):
        self.exec_states.append(exec_state)

    def __add_params(self, *params):
        receiver = 'argv'
        handle = Handle()
        handle.set_type('array')
        handle.set_name(receiver)
        handle.set_value(*params)
        exec_state = (receiver, handle, None)
        self.__add_exec_state(exec_state)

    def __run_statement(self, statement):
        
        receiver = statement[1]
        t = SimpleQueryTranslator()
        if is_query(statement):
            t.set_exec_states(self.exec_states)

            sql = t.simple_query_to_sql(statement)
            if self.conn is None:
                assert(False)
            table_name = statement[2][1]
            if self.__exec_query(receiver, sql, table_name):
                pass
                # self.__dump_exec_states()
        elif is_buildin_func(statement):
            # t.set_exec_states(self.exec_states)
            e = Evaluator(self.exec_states)
            handle = e.exec_func(statement)

            exec_state = (receiver, handle)
            self.__add_exec_state(exec_state)

            if isinstance(handle, MySQLdb.connections.Connection):
                # print(handle)
                self.set_connection(handle)
            

    def run_code(self, code, params):
        s = SimpleQueryStatements()
        statements = s.parse(code)
        self.__add_params(params)

        for statement in statements:
            self.__run_statement(statement)
        print('\n---- END ----')
            

    def run_file(self, filename, params=None):
        with open(filename, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            self.run_code(''.join(lines), params)

