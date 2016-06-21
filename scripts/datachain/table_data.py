
import sys
sys.path.append('D:\\Projects\\PySQLKits\\lib\\simplequery')

from simplequery import *
from tornado.template import Template



def filter_dataset(handle):
    filters = handle.get_filters()
    if filters is not None:
        filter_list = list(map(lambda x: x[1], filters))
    else:
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
def table_data(file, *data):
    with open('table_data.html', 'r', encoding='utf-8') as r:
        content = r.read()
    
    datasets = []
    d = {}
    for handle in data:
        if isinstance(handle, Handle):
            v = filter_dataset(handle)
            # v is a tuple with n entries.
            datasets.append(v)

    d['datasets'] = datasets
    t = Template(content)
    c = t.generate(**d)

    file.write(c.decode('utf-8'))
    


@buildin
def t(handle, *data):
    
    f = handle.get_value()
    if f is not None:
        table_data(f, *data)
    return None