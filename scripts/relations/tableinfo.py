#
def get_primary_key(table_fields):
    pri = list(filter(lambda x: x[4] == 'PRI',  table_fields))
    return pri[0] if len(pri) > 0 else None

def get_id_fields(table_fields):
    return list(filter(lambda x: x[0].endswith('id') and x[4] != 'PRI',  table_fields))    

class TableInfo:

    def __init__(self, table_name, fields):
        self.table_name = table_name
        self.fields = fields
        self.primary_key = get_primary_key(fields)
        self.id_fields = get_id_fields(fields)
        self.depends = {}
        self.followers = []

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
        """
        self.followers.append(table_info)
        # update depend table
        table_info.__add_depend_table(self.primary_key, self)

    def __str__(self):
        return "<table=%s %d / %d >" % (self.table_name, len(self.depends), len(self.followers))