#
import os
import json

class ExtraTableInfo:

    def __init__(self, db_name):
        self.db_name = db_name
        self.extra = self.load_table_extra_info()

    def load_table_extra_info(self):
        config_file = "workspace/%s/config.json" % self.db_name
        if not os.path.exists(config_file):
            return None
        with open(config_file) as file:
            jstr = file.read()
            if jstr == '':
                return None
            extra = json.loads(jstr)
            return extra
        return None

    def set_virtual_foreign_key(self, table_info, uncertain_id, table_name, field_name):
        if not self.extra:
            self.extra = {'virtualForeignKeys': {}}
        
        virtual_foreign_keys = self.extra['virtualForeignKeys']
        if table_info.table_name not in virtual_foreign_keys:
            virtual_foreign_keys[table_info.table_name] = {}
        
        foreign_key = "%s.%s" % (table_name, field_name)
        if uncertain_id not in virtual_foreign_keys[table_info.table_name]:
            virtual_foreign_keys[table_info.table_name][uncertain_id] = [foreign_key]
        else:
            # Avoid duplicated keys
            if foreign_key not in virtual_foreign_keys[table_info.table_name][uncertain_id]:
                virtual_foreign_keys[table_info.table_name][uncertain_id].append(foreign_key)

    def update_table_extra_info(self):
        config_file = "workspace/%s/config.json" % self.db_name
        with open(config_file, mode='w', encoding='utf8') as file:
            jstr = json.dumps(self.extra, sort_keys=True, indent=2)
            file.write(jstr)



    