
import sys
sys.path.append('D:\\Projects\\PySQLKits\\lib\\simplequery')

from simplequery import *
from tornado.template import Template

def table_data(file, *data):
    with open('table_data.html', 'r', encoding='utf-8') as r:
        content = r.read()
    
    datasets = []
    d = {}
    for item in data:
        if isinstance(item, Handle):
            v = item.get_value()
            datasets.append(list(v))
            print("DDDD~~~")
            print(v)
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