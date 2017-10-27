# Refer https://github.com/lexchou/utilities/blob/master/db_diff

import MySQLdb
import re, sys
from optparse import OptionParser

def db_scheme(server, user, passwd, db, table_name_pattern=None):
    host = server
    port = 3306
    if ':' in server:
        host, port = server.split(':')
        port = int(port)

    ret = []
    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset="utf8")
    print("-- Connected to server %s by %s" % (server, user))
    
    ct = db.cursor()
    ct.execute("SHOW TABLES")

    pattern = re.compile(table_name_pattern) if table_name_pattern else None

    for (table,) in ct.fetchall():
        if pattern and not pattern.match(table):
            continue
        ct.execute("SHOW FULL COLUMNS FROM " + table)
        fields = list(ct.fetchall())
        ret.append((table, fields))

    ct.close()
    return ret, db

def make_map(data, keys):
    return dict( [(d[0], d) for d in data if d[0] in keys] )

def items(data, keys):
    return [d for d in data if d[0] in keys]

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

def get_prev_field(field_names, name):
    return field_names[field_names.index(name) - 1]

# The 8th col is Privileges, do NOT compare it
def is_column_different(a, b, ignore_comments=False):
    if ignore_comments:
        return a[0:7] != b[0:7]
    else:
        return a[0:7] != b[0:7] or a[-1:] != b[-1:]

def get_alter_table_sql(src_db, dest_db, options):
    (added, changed, deleted) = diff(src_db[1], dest_db[1])
    ret = []

    src_db_field_names = [None] + [field[0] for field in src_db[1]]
    
    for name in added:
        prev = get_prev_field(src_db_field_names, name)

        alt = "ALTER TABLE `%s` ADD COLUMN %s" % (src_db[0], get_field(added[name]))
        if prev is not None:
            alt += " AFTER `%s`" % prev
        ret.append(alt + ';')

    key_changed = False # Key, index changed flag
    prev = None # Maybe BUG!!!

    ignore_comments = False
    if options.ignore and 'comments' in options.ignore.split(','):
        ignore_comments = True

    for columns in changed:
        a, b = columns
        
        if is_column_different(a, b, ignore_comments):
            after = 'AFTER `%s`' % prev if prev else ""

            ret.append("ALTER TABLE `%s` CHANGE COLUMN `%s` %s COMMENT '%s' %s;" % (src_db[0], b[0], get_field(a), a[8], after))
            if a[4] != b[4]:
                # TODO: PRI, MUL, UNI Should be checked here
                key_changed = True
                if a[4] == "PRI":   # add new primary key
                    ret.append("# WARNING: New primary key `%s` added" % a[0])
                else:   # drop primary key
                    ret.append("# WARNING: Old primary key `%s` removed" % b[0])
        
        prev = a[0] # For AFTER 

    if key_changed:
        new_pk = [f[0] for f in src_db[1] if f[4] == "PRI"]
        ret.append("ALTER TABLE `%s` DROP PRIMARY KEY;" % src_db[0])
        if len(new_pk) > 0:
            ret.append("ALTER TABLE `%s` ADD PRIMARY KEY (`%s`);" % (src_db[0], "`, `".join(new_pk)))

    for name in deleted:
        ret.append("ALTER TABLE `%s` DROP COLUMN `%s`;" % (dest_db[0], deleted[name][0]))

    return ret

def print_split_line(msg):
    print('-' * 20, msg, '-' * 20)

"""
a is src_db_args,
b is dest_db_args
"""
def diff_db(a, b, options, c=None):
    src_db = db_scheme(a[2], a[0], a[1], a[3], c)
    dest_db = db_scheme(b[2], b[0], b[1], b[3], c)

    (added, changed, deleted) = diff(src_db[0], dest_db[0])

    print_split_line("Tables Added")
    for name in added:
        print(get_create_table_sql(added[name], src_db[1]), end="\n\n")

    print_split_line("Tables changed")
    for dbs in changed:
        for sql in get_alter_table_sql(*dbs, options):
            print(sql)

    print_split_line("Tables removed")
    for name in deleted:
        print("DROP TABLE `%s`;" % name)

    src_db[1].close()
    dest_db[1].close()

usage = """
Usage:
    python3 mysqldiff.py --source=<source> --dest==<destination> [options]

    source, destination format:
        username:password@host[:port]/database
    Options:
    -i --ignore, support comments


    Examples:
    python3 mysqldiff.py --source=root:root@localhost/mydb --dest=root:123456@192.168.1.101:3307/mydb

Options:
    table-name-pattern
"""

def main(options, args):
    if not (options.source and options.dest):
        print(usage)
        exit('Invalid arguments')

    u = re.compile("(.*):(.*)@(.*)/(.*)")
    a, b = u.match(options.source), u.match(options.dest)
    
    if a is None or b is None:
        exit('Invalid database informations')

    src_db_args, dest_db_args = a.groups(), b.groups()

    diff_db(src_db_args, dest_db_args, options, options.pattern)


if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-s", "--source", action="store", dest="source", help="Provide source database")
    parser.add_option("-d", "--dest", action="store", dest="dest", help="Provide destination database")
    parser.add_option("-c", "--config", action="store", dest="config", help="Provide config file")    
    parser.add_option("-p", "--pattern", action="store", dest="pattern", help="Provide table name pattern on focus")
    parser.add_option("-i", "--ignore", action="store", dest="ignore", help="Provide settings to ignore ")
    parser.add_option("-f", "--file", action="store", dest="file", help="Provide filename for output sql")
    parser.add_option("-h", "--highlight", action="store", dest="highlight", help="Highlights the differences")
    
    options, args = parser.parse_args()
    main(options, args)
