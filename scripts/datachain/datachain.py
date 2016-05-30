
import os
import sys
import MySQLdb
sys.path.append('D:\\Projects\\PySQLKits\\lib\\simplequery')

from simplequery import *

code = """
h = @fopen('d:\\a.html');
@fwrite(h, '<div>World</div>');
@fclose(h);
@render(h);

com = kx_company(create_time=@today, @limit=5, @asc=company_id);
@p(com);
user = kx_user(company_id=com.company_id);
"""

def get_mysql_connection():
    args = {'host':'localhost', 'user':'root', 'passwd':'root', 'db':"test"}
    conn = MySQLdb.connect(**args)

    with conn.cursor() as c:
        c.execute('show databases;')
        
        print(list(map(lambda x: x[0], c.fetchall())))
    return conn

"""
"""
if __name__ == '__main__':

    e = SimpleQueryExecutor()
    conn = get_mysql_connection()
    #print(conn)
    #exit()
    e.set_connection(conn)
    e.run_file(sys.argv[1])


