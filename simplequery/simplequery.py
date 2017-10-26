
import ply.lex as lex
import ply.yacc as yacc
import MySQLdb
from runtime import *
from simplequery_parser import *
from simplequery2sql import *
from buildin_funcs import *

def get_mysql_connection(**params):
    params = {'host':'localhost', 'user':'root', 'passwd':'root', 'db':'test'}
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

    def get_connection(self, db_name):
        handle = None
        for exec_state in self.exec_states:
            if exec_state[0] == db_name:
                handle = exec_state[1]
                break

        if isinstance(handle, MySQLConnectionObject):
            conn = handle.get_value()
            return conn
        elif isinstance(handle, RedisConnectionObject):
            conn = handle.get_value()
            return conn            

        return None

    """
    Execute MySQL query to fetch dataset.
    """
    def __exec_query(self, receiver, translator, conn_var, database, table_name, conditions):
        conn = self.get_connection(conn_var)
        
        with conn.cursor(MySQLdb.cursors.DictCursor) as cursor:
            sql = translator.simple_query_to_sql(database, table_name, conditions)

            r = cursor.execute(sql)
            
            results = cursor.fetchall()

            handle = DatasetObject()
            handle.set_name(receiver)
            handle.set_value(results)

            # set fields for order
            rows = cursor.execute('SHOW COLUMNS FROM `%s`.`%s`' % (database, table_name))
            columns = cursor.fetchall()
            fields = list(map(lambda x: x['Field'], columns))
            handle.set_default_fields(fields)
            
            exec_state = (receiver, handle, sql)
            self.__add_exec_state(exec_state)
            return True
        return False

    def __exec_redis_query(self, receiver, conn_var, database, key_name, params):
        conn = self.get_connection(conn_var)
        if conn is not None:
            handle = RedisConnectionObject.exec_command(conn, database, key_name, params)
            exec_state = (receiver, handle)
            self.__add_exec_state(exec_state)
            # print(self.exec_states)

    # append to exec_states and do more work here
    def __add_exec_state(self, exec_state):
        self.exec_states.append(exec_state)

    def __add_params(self, *params):
        receiver = 'argv'
        handle = ArrayValueObject()
        handle.set_name(receiver)
        handle.set_value(*params)
        exec_state = (receiver, handle, None)
        self.__add_exec_state(exec_state)

    def __run_statement(self, statement):
        receiver = statement[1]
        
        if is_mysql_query(statement):

            t = SimpleQueryTranslator()
            t.set_exec_states(self.exec_states)

            query = statement[2]
            conn_var = query[1]
            database = query[2]
            table_name = query[3]
            conditions = query[4]
            if self.__exec_query(receiver, t, conn_var, database, table_name, conditions):
                pass
                # self.__dump_exec_states()
        elif is_redis_query(statement):
            redis = statement[2]
            conn_var = redis[1]
            database = redis[2][1:]
            key_name = redis[3]
            params = redis[4]
            if self.__exec_redis_query(receiver, conn_var, database, key_name, params):
                pass

        elif is_buildin_func(statement):
            # t.set_exec_states(self.exec_states)
            e = Evaluator(self.exec_states)
            retval = e.exec_func(statement[2])

            exec_state = (receiver, retval)
            self.__add_exec_state(exec_state)

            
    """
    Run code with parameters
    """
    def run_code(self, code, params):
        s = SimpleQueryStatements()
        statements = s.parse(code)
        self.__add_params(params)

        for statement in statements:
            self.__run_statement(statement)
        print('\n---- END ----')
            

    def run_file(self, filename, params=None):
        # use_lex_print = True
        # use_yacc_print = True
        with open(filename, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
            self.run_code(''.join(lines), params)

