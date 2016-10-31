#!/usr/bin/env python
# Ref https://github.com/lexchou/utilities/blob/master/db_diff

import MySQLdb
from sys import argv
import re


def is_table_name_pattern_match(table_name, table_name_reg_pattern):
    if table_name_reg_pattern is None:
        return True

    m = table_name_reg_pattern.match(table_name)
    if m is not None:
        return True
    return False
"""
"""
def db_scheme(server, user, passwd, db, table_name_pattern=None):
    host = server
    port = 3306
    if ':' in server:
        host, port = server.split(':')
        port = int(port)

    ret = []
    print("#Connecting to server %s by %s" % (server, user))
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset="utf8")
    print("#Reading database scheme")
    ct = db.cursor()
    ct.execute("SHOW TABLES")

    table_name_reg_pattern = None
    if table_name_pattern is not None:
        table_name_reg_pattern = re.compile(table_name_pattern)

    for (table,) in ct.fetchall():
        if not is_table_name_pattern_match(table, table_name_reg_pattern):
            continue
        ct.execute("SHOW FULL COLUMNS FROM " + table)
        fields = list(ct.fetchall())
        ret.append((table, fields))
    ct.close()
    return ret, db

def make_map(data, keys):
    ret = {}
    for d in data:
        if d[0] in keys:
            ret[d[0]] = d
    return ret

def items(data, keys):
    ret = []
    for d in data:
        if d[0] in keys:
            ret.append(d)
    return ret


def diff(a, b):
    sa = set([x[0] for x in a])
    sb = set([x[0] for x in b])
    d = sa.intersection(sb)

    d1 = make_map(a, sa - sb)
    d2 = list(zip(items(a, d), items(b, d)))
    d3 = make_map(b, sb - sa)
    return d1, d2, d3

# get field modify description
def get_field(field):
    ret = "`%s` %s" % (field[0], field[1])
    if field[3] == "NO":
        ret += " NOT NULL"
    if field[5] == '':
        ret += " DEFAULT ''"
    if field[5] == 'None':
        ret += " DEFAULT ''"
    else:
        ret += " DEFAULT '%s'" % field[5]
    return ret

def get_create_table_sql(table, db):
    ct = db.cursor()
    create_table_sql = "SHOW CREATE TABLE %s;" % table[0]
    ct.execute(create_table_sql)
    r = ct.fetchone()
    ct.close()
    return r[1] + ";"

def find_prev_field(fields, name):
    last_field = None
    for field in fields:
        if field[0] == name:
            return last_field
        last_field = field
    return None

# The 8th col is Privileges
def is_column_different(a, b):
    return a[0:7] + a[-1:] != b[0:7] + b[-1:]

def get_alter_table_sql(src_db, dest_db):
    (added, changed, deleted) = diff(src_db[1], dest_db[1])
    ret = []

    for name in added:
        prev = find_prev_field(src_db[1], name)

        alt = "ALTER TABLE `%s` ADD COLUMN %s" % (src_db[0], get_field(added[name]))
        if prev is not None:
            alt += " AFTER `%s`" % prev[0]
        ret.append(alt + ';')

    pk_changed = False
    for columns in changed:
        a, b = columns
        if is_column_different(a, b):
            ret.append("ALTER TABLE `%s` CHANGE COLUMN `%s` %s COMMENT '%s';" % (src_db[0], b[0], get_field(a), a[8]))
            if a[4] != b[4]:
                pk_changed = True
                if a[3] == "PRI":   # add new primary key
                    ret.append("# WARNING: New primary key `%s` added" % a[0])
                else:   # drop primary key
                    ret.append("# WARNING: Old primary key `%s` removed" % b[0])

    if pk_changed:
        new_pk = [f[0] for f in src_db[1] if f[3] == "PRI"]
        ret.append("ALTER TABLE `%s` DROP PRIMARY KEY;" % src_db[0])
        if len(new_pk) > 0:
            ret.append("ALTER TABLE `%s` ADD PRIMARY KEY (`%s`);" % (src_db[0], "`, `".join(new_pk)))

    for name in deleted:
        ret.append("ALTER TABLE `%s` DROP COLUMN `%s`;" % (dest_db[0], deleted[name][0]))
    return ret

"""
a is src_db_args,
b is dest_db_args
"""
def diff_db(a, b, c=None):

    src_db = db_scheme(a[2], a[0], a[1], a[3], c)
    dest_db = db_scheme(b[2], b[0], b[1], b[3], c)

    (added, changed, deleted) = diff(src_db[0], dest_db[0])

    # Added
    print("-- " * 20)
    print("-- Tables Added")
    for name in added:
        print(get_create_table_sql(added[name], src_db[1]))
        print()

    # Changed
    print("-- " * 20)
    print("-- Tables changed")
    for dbs in changed:
        for sql in get_alter_table_sql(*dbs):
            print(sql)

    # Removed
    print("-- " * 20)
    print("-- Tables removed")
    for name in deleted:
        print("DROP TABLE `%s`;" % name)

    src_db[1].close()
    dest_db[1].close()

# Main entrypoint
usage = """
Usage:
    python3 mysqldiff.py <source> <destination> [options]

    source, destination format:
        username:password@host[:port]/database
    python3 mysqldiff.py root:root@localhost/mydb root:123456@192.168.1.101:3307/mydb jk_*

Options:
    table-name-pattern
"""

def main():
    if len(argv) < 3:
        print(usage)
        exit('Invalid arguments')

    u = re.compile("(.*):(.*)@(.*)/(.*)")
    a = u.match(argv[1])
    b = u.match(argv[2])
    if a is None or b is None:
        exit('Invalid arguments')

    table_name_pattern = None
    if len(argv) > 3: # table name pattern
        table_name_pattern = argv[3]

    src_db_args = a.groups()
    dest_db_args = b.groups()
    diff_db(src_db_args, dest_db_args, table_name_pattern)

if __name__ == "__main__":
    main()
