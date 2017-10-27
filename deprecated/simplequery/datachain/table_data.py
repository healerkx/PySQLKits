
import sys
sys.path.append('D:\\Projects\\PySQLKits\\lib\\simplequery')

from simplequery import *
from tornado.template import Template



def filter_dataset(handle):
    filter_list = handle.get_filters()
    if filter_list is None:
        filter_list = handle.get_default_fields()

    rows = handle.get_value()
    ret = {'data':[], 'fields': filter_list}
    for row in rows:
        line_data = []
        for field in filter_list:

            line_data.append(row[field])
        ret['data'].append(line_data)
    return ret


# data is dataset's list, each is a dataset Handle
def table_data(*data):
    # TODO: Relearn tornado templates...
    with open('templates/table_data.html', 'r', encoding='utf-8') as r:
        content = r.read()
    
    datasets = []
    d = {}
    for handle in data:
        if isinstance(handle, DatasetObject):
            v = filter_dataset(handle)
            # v is a tuple with n entries.
            datasets.append(v)

    d['datasets'] = datasets

    print(d['datasets'])
    t = Template(content)
    c = t.generate(**d)

    with open('tmp.html', 'w', encoding='utf-8') as file:
        file.write(c.decode('utf-8'))
    
@buildin
def t(exec_states, *handle):
    if len(handle) > 0:
        table_data(*handle)
    return None