#
from defines import *

def get_primary_key(table_fields):
    pri = list(filter(lambda x: x[4] == 'PRI',  table_fields))
    return pri[0] if len(pri) > 0 else None

def get_id_fields(table_fields):
    return list(filter(lambda x: x[0].endswith('id') and x[4] != 'PRI',  table_fields))    

class TableInfo:

    def __init__(self, table_name, fields, extra_info=None):
        self.table_name = table_name
        self.fields = fields
        self.primary_key = get_primary_key(fields)
        self.id_fields = get_id_fields(fields)
        self.depends = {}
        self.followers = []
        self.extra_info = extra_info

    def __add_depend_table(self, field_name, table_info):
        """
        private
        Add tables I depend on
        """
        self.depends[field_name] = table_info

    def add_follower_table(self, table_info):
        """
        :param table_info
        Add the tables follow me. (My PK is other table FK)
        For the Graph vertex view:
            MyTable -> OtherTable
        """
        self.followers.append(table_info)
        # update depend table
        table_info.__add_depend_table(self.primary_key, self)

    def __str__(self):
        return "%s[%s]%s %d / %d >" % (COLOR_GREEN, self.table_name, COLOR_RESET, len(self.depends), len(self.followers))

    def set_extra_info(self, extra_info):
        self.extra_info = extra_info

    def get_id_fields(self, extra=True):
        """
        config.json provide supplimental relationship between tables.
        if extra is True, this method returns id_list + extra_id_list
        """
        if not extra:
            return self.id_fields

        if not self.extra_info:
            return self.id_fields

        if table_name not in self.extra_info["fkMapping"]:
            return self.id_fields

        extra_info = self.extra_info["fkMapping"][table_name]
        if len(extra_info) == 0:
            return self.id_fields
        
        get_field_name = lambda x: (x[x.find('.')+1:],) if '.' in x else (x,)
        extra_id_fields = []
        for id_name in extra_info:
            field_names = extra_info[id_name]
            extra_id_fields += list(map(get_field_name, field_names))

        return self.id_fields + extra_id_fields