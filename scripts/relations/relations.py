#
import MySQLdb
from functools import *
from tableinfo import *
from sys import argv
import os, re
import json
from graph import *
from extra import *
from defines import *

usage = """
Usage:
    python3 relations.py <source> [--options]

    <source> format:
        username:password@host[:port]/database
    python3 relations.py root:root@localhost/mydb
"""

sub_systems_analysis = True


def fetch_database_info(extra_info, user, password, server, db):
    """
    Fetch database info and mixin extra info from json config
    """
    host = server
    port = 3306
    if ':' in server:
        host, port = server.split(':')
        port = int(port)

    db = MySQLdb.connect(host=host, user=user, passwd=password, db=db, port=port, charset="utf8")
    print("#Reading database scheme")
    ct = db.cursor()
    ct.execute("SHOW TABLES")

    table_info_list = []
    id_table_map = {} # Stores id-field names => tableInfo mapping
    for (table,) in ct.fetchall():
        ct.execute("SHOW FULL COLUMNS FROM " + table)
        fields = ct.fetchall()
        table_info = TableInfo(table, fields, extra_info)

        id_fields = table_info.get_id_fields()

        for id_field in id_fields:
            id_field_name = id_field[0]
            if id_field_name not in id_table_map:
                id_table_map[id_field_name] = [table_info]
            else:
                id_table_map[id_field_name].append(table_info)

        table_info_list.append(table_info)

    ct.close()
    return table_info_list, id_table_map, db


def calc_tables_relations(tables, id_table_map):
    """
    Calc the tables' relations
    """
    for table in tables:
        primary_key = table.primary_key[0]
        if primary_key not in id_table_map:
            continue
        follower_tables = id_table_map[primary_key]
        for follower_table in follower_tables:
            table.add_follower_table(follower_table)

def update_logic_foreign_key(table_info, uncertain_id, key):
    pass            

def query_uncertain_id_fields(table_info_list):
    """
    """
    for table_info in table_info_list:
        id_fields = table_info.get_id_fields()
        depends = table_info.depends
        if len(id_fields) == len(depends):
            continue

        ids = list(map(lambda x: x[0], id_fields))
        depends_ids = list(map(lambda x: x[0], depends.keys()))
        uncertain_ids = set(ids) - set(depends_ids)
        if len(uncertain_ids) > 0:
            for uncertain_id in uncertain_ids:
                print("Could you point out `%s`.`%s` corresponds to which primary key?" 
                    % (green_text(table_info.table_name), green_text(uncertain_id)))
                key = input('')
                if len(key) > 0 and '.' in key:
                    update_logic_foreign_key(table_info, uncertain_id, key)

# show all tables' followers and depends
def print_relations(results):
    for table in results:
        print(table)
        for f in table.followers:
            print("\t", f)
        print("\t", '-' * 30)
        for d in table.depends:
            print("\t", d)
        print("=" * 40, end='\n\n')


def init_graph_from_relations(results, func):
    graph = Graph()
    for table in results:
        v = Vertex(table)
        graph.add_vertex(table.table_name, v)

    # connect each Vertex
    for g in graph.vertex_map.values():
        adjacencies = getattr(g.inner, func)
        for a in adjacencies:
            g.add_adjacency(graph.get_vertex(a.table_name))

    return graph

def main(db, other_args):
    # For local test

    if '--without-sub-systems-analysis' in other_args:
        sub_systems_analysis = False

    u = re.compile("(.*):(.*)@(.*)/(.*)")
    a = u.match(db)
    db_args = a.groups()

    extra_info = load_table_extra_info(db_args[3])

    table_info_list, id_table_map, db = fetch_database_info(extra_info, *db_args)

    calc_tables_relations(table_info_list, id_table_map)
    try:
        query_uncertain_id_fields(table_info_list)
    except KeyboardInterrupt as e:
        print('Ignore all uncertain foreign keys')
        pass
    

    graph = init_graph_from_relations(table_info_list, 'followers')
    Graph.prints(graph)

    paths = graph.all_paths(graph.get_vertex('bo_merchant'),
                            graph.get_vertex('bo_store_page'))
    count = 0
    for path in paths:
        print('-' * 5, "Way %d" % count, '-' * 5)
        Graph.prints(path)
        count += 1

    path = graph.find_path(graph.get_vertex('bo_merchant'),
                           graph.get_vertex('bo_store_page'))
    Graph.prints(path)

    # output the results
    print("*" * 20, "table relations", "*" * 20)
    print_relations(table_info_list)

def read_local_config():
    with open('relations.conf') as file:
        return file.readline()
    return None

if __name__ == "__main__":
    """
    TODO: get args from sys.argv
    """
    db = '' 
    if len(argv) < 2:
        db = read_local_config()
    else:
        db = argv[1]

    main(db, argv[2:])

