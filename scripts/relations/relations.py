#
import MySQLdb
from functools import *
from tableinfo import *
from sys import argv
import re

usage = """
Usage:
    python3 relations.py <source> [options]

    source format:
        username:password@host[:port]/database
    python3 mysqldiff.py root:root@localhost/mydb

Options:
    --show-drop-table
    --file
"""

def db_scheme(server, user, passwd, db):
    host = server
    port = 3306
    if ':' in server:
        host, port = server.split(':')
        port = int(port)

    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset="utf8")
    print("#Reading database scheme")
    ct = db.cursor()
    ct.execute("SHOW TABLES")

    ret = []
    id_table_map = {}
    for (table,) in ct.fetchall():
        ct.execute("SHOW FULL COLUMNS FROM " + table)
        fields = ct.fetchall()
        table_info = TableInfo(table, fields)

        for id_field in table_info.id_fields:
            id_field_name = id_field[0]
            if id_field_name not in id_table_map:
                id_table_map[id_field_name] = [table_info]
            else:
                id_table_map[id_field_name].append(table_info)

        ret.append(table_info)
    ct.close()

    #for (a, b) in id_table_map.items():
    #    print(a, b[0])
    return ret, id_table_map, db


def fetch_database_info(user, password, server, database):
    return db_scheme(server, user, password, database)

def calc_tables_relations(tables, id_table_map):
    for table in tables:
        primary_key = table.primary_key[0]
        if primary_key not in id_table_map:
            continue
        follower_tables = id_table_map[table.primary_key[0]]
        for follower_table in follower_tables:
            table.add_follower_table(follower_table)

        # exit()

def main():
    # For local test
    argv = ["", 'root:root@127.0.0.1/school']
    if len(argv) < 2:
        print(usage)
        exit('Invalid arguments')

    u = re.compile("(.*):(.*)@(.*)/(.*)")
    a = u.match(argv[1])
    db_args = a.groups()

    ret, id_table_map, db = fetch_database_info(*db_args)
    
    calc_tables_relations(ret, id_table_map)

    # output the results
    print("----")
    for table in ret:
        print(table)

if __name__ == "__main__":
    main() 