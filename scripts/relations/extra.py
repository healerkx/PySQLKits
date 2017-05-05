#
import os

def load_table_extra_info(db_name):
    config_file = "workspace/%s/config.json" % db_name
    if not os.path.exists(config_file):
        return None
    with open(config_file) as file:
        jstr = file.read()
        if jstr == '':
            return None
        extra = json.loads(jstr)
        return extra
    return None

def update_table_extra_info(db_name):
    info = load_table_extra_info(db_name)


    