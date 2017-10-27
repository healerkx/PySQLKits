#
import MySQLdb, os, re, json
from functools import *
from tableinfo import *
from sys import argv
from graph import *
from extra import *
from defines import *
import readline
from optparse import OptionParser

usage = """
Usage:
    python3 relations.py --source=<database> [--options]

    <source> format:
        username:password@host[:port]/database
    python3 relations.py root:root@localhost/mydb
"""


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

        for id_field_name in id_fields:
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

def update_logic_foreign_key(table_info_list, table_info, uncertain_id, keys, extra):
    keys = keys.split(',')
    for key in keys:
        key = key.strip()
        table_name, field_name = key.split(".")
        if table_name not in map(lambda x: x.table_name, table_info_list):
            raise Exception("Table `%s` not found" % red_text(table_name))
        this_table_info = list(filter(lambda x: x.table_name==table_name, table_info_list))[0]

        if field_name not in this_table_info.id_fields and field_name != this_table_info.primary_key[0]:
            raise Exception("Field `%s`.`%s` not found" % (red_text(table_name), red_text(field_name)))
        
        extra.set_virtual_foreign_key(table_info, uncertain_id, table_name, field_name)
        extra.update_table_extra_info()
    
    return True

def query_uncertain_id_fields(table_info_list, extra):
    """
    """
    for table_info in table_info_list:
        id_fields = table_info.get_id_fields()
        depends = table_info.depends
        if len(id_fields) == len(depends):
            continue
        
        depends_ids = list(map(lambda x: x[0], depends.keys()))
        uncertain_ids = list(set(id_fields) - set(depends_ids))
        if len(uncertain_ids) == 0:
            continue
        index = 0
        while index < len(uncertain_ids):
            uncertain_id = uncertain_ids[index]
            try:
                print("Could you point out `%s`.`%s` corresponds to which primary key?" 
                    % (green_text(table_info.table_name), green_text(uncertain_id)))
                keys = input('')
                if len(keys) > 0 and '.' in keys:
                    if update_logic_foreign_key(table_info_list, table_info, uncertain_id, keys, extra):
                        index += 1
                elif keys == 'i':
                    # Ignore it this time
                    index += 1
                elif keys == 'n':
                    # It's not an Id.
                    index += 1
                elif keys == 'e':
                    # The fields means an id from extra system
                    extra.set_virtual_foreign_key(table_info, uncertain_id, '', '')
                    extra.update_table_extra_info()
                    index += 1
                    
            except Exception as e:
                print(e)
            

# show all tables' followers and depends
def print_relations(results):
    for table in results:
        print(table)
        for f in table.followers:
            print("\t", f)
        # print("\t", '-' * 30)
        # for d in table.depends:
        #     print("\t", d)
        print("=" * 40, end='\n\n')


def init_graph_from_relations(results):
    graph = Graph()
    for table in results:
        graph.add_vertex(table.table_name, table)

    for table in results:
        for follow in table.followers:
            graph.add_edge(table.table_name, follow.table_name)
    
    return graph


def plot(graph):
    from igraph import plot
    layout = graph.layout("circle")
    visual_style = dict()
    visual_style["vertex_size"] = 20
    visual_style["vertex_label_size"] = 30
    visual_style["vertex_label_dist"] = 2
    visual_style["vertex_color"] = "white"
    visual_style["vertex_label_color"] = "blue"
    visual_style["vertex_label"] = graph.vs["name"]
    visual_style["edge_width"] = 2
    visual_style["layout"] = layout
    visual_style["bbox"] = (1200, 1000)
    visual_style["margin"] = 100
    plot(graph, "social_network.png", **visual_style)

def calc_database_table_relations(db_args):
    extra = ExtraTableInfo(db_args[3])
    extra_info = extra.load_table_extra_info()

    table_info_list, id_table_map, db = fetch_database_info(extra_info, *db_args)

    calc_tables_relations(table_info_list, id_table_map)

    return table_info_list, extra

def main(db, other_args):
    # For local test
    u = re.compile("(.*):(.*)@(.*)/(.*)")
    a = u.match(db)
    db_args = a.groups()

    table_info_list, extra = calc_database_table_relations(db_args)
    print("Press [i] to ignore this time, [n] means not an id(key), [e] means an id from an external system.")
    print("")

    try:
        query_uncertain_id_fields(table_info_list, extra)
    except KeyboardInterrupt as e:
        print('Ignore all uncertain foreign keys')

    table_info_list, extra = calc_database_table_relations(db_args)
    graph = init_graph_from_relations(table_info_list)
    plot(graph)
    
    #
    paths = graph.all_paths('bo_merchant', 'bo_app')
    count = 1
    for path in paths:
        print('-' * 5, "Way %d" % count, '-' * 5)
        graph.prints(path)
        count += 1

#
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-s", "--source", action="store", dest="source", help="Provide source database")
    options, args = parser.parse_args()

    main(options.source, argv[2:])

