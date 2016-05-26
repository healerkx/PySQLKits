
import os
import sys
sys.path.append('D:\\Projects\\PySQLKits\\lib\\simplequery')

from simplequery import *

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


