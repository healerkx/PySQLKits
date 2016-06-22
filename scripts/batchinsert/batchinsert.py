# 
import random
from dateutil import parser as DateParse
import time

def unixtime(datestr):
    return int(DateParse.parse(datestr).timestamp())

# base class
class ValueGenerator:
    def __init__(self, **flags):
        self.flags = flags
        if hasattr(self, 'initialize'):
            self.initialize()

##########################################
# Generators
class ListGenerator(ValueGenerator):
    def adapt(self, v):
        self.v = v

    def __next__(self):
        return random.choice(self.v)


class DatetimeRange(ValueGenerator):
    def initialize(self):
        if 'begin' in self.flags:
            self.begin = unixtime(self.flags['begin'])
        if 'end' in self.flags:
            self.end = unixtime(self.flags['end'])

    def __next__(self):
        self.values = range(self.begin, self.end)
        ts = random.choice(self.values)
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) 

class IntegerRange(ValueGenerator):
    values = None
    current = None
    step = 1
    def adapt(self, values):
        self.values = values

    def initialize(self):
        if 'begin' in self.flags:
            self.current = self.flags['begin']
        if 'step' in self.flags:
            self.step = self.flags['step']

    def __next__(self):
        if self.values is None:
            self.values = range(self.flags['begin'], self.flags['end'])
        if 'order' in self.flags:
            if self.flags['order'] == 'asc':
                self.current += self.step
                return self.current
            elif self.flags['order'] == 'desc':
                self.current -= self.step
                return self.current

        return random.choice(self.values)        

"""
"""
class EnglishName(ValueGenerator):
    names = None
    def initialize(self):
        self.names = self.load('english_names.txt')

    def load(self, filename):
        # TODO: load names from a file
        return ['Albert', 'Bob', 'Helen', 'McDonald', 'Mike', 'Lucy', 'Lily', 'Sophy', 'Chris', 'John']

    def __next__(self):
        if self.names is None:
            self.initialize()
        try:
            name = random.choice(self.names)
            if self.flags['unique']:
                self.names.remove(name)
            return name            
        except:
            # Resource not enough for unique random
            return "<None>"


"""
"""
class ChineseName(ValueGenerator):
    names = None

    def initialize(self):
        self.names = self.__load('chinese_names.txt')

    def __load(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), file.readlines())))

    def __next__(self):
        if self.names is None:
            self.initialize()
        try:
            name = random.choice(self.names)
            if self.unique:
                self.names.remove(name)
            return name            
        except:
            # Resource not enough for unique random
            return "<None>"


class ChinaMobile(ValueGenerator):
    cache = set()

    def __next__(self):
        t = str(random.choice([3, 4, 5])) + str(random.randint(0, 9))
        return "1%s%s%s" % (t, random.randint(1000, 9999), random.randint(1000, 9999))

    def __iter__(self):
        count = 0
        while True:
            if count > 10:
                break
            count += 1
            v = next(self)
            yield v

"""
main class for insertion
"""
class Insert:
    table_name = None
    options = None

    def __init__(self, table_name, **options):
        self.table_name = table_name
        self.options = options
        self.fields_order = None

    def __generate_insert(self):
        f, v = [], []
        for field in self.fields_order:
            f.append(field)
            generator = self.generators[field]
            v.append("'%s'" % (next(generator)))
        return "insert into `%s` (%s) values (%s);" % (self.table_name, ", ".join(f), ", ".join(v))

    def generate(self, times):
        self.generators = {}

        for g in self.options:
            self.generators[g] = self.get_generator(g)

        if self.fields_order is None:
            self.fields_order = []
            for g in self.options:
                self.fields_order.append(g)
        for i in range(0, times):
            yield self.__generate_insert()

    def set_fields_order(self, fields_order):
        self.fields_order = fields_order

    def perform(self, cursor, times=1, filename=None):
        for sql in self.generate(times):
            print(sql)

    def get_generator(self, g):
        config = self.options[g]
        if isinstance(config, ValueGenerator):
            return config
        elif isinstance(config, list):
            r = ListGenerator()
            r.adapt(config)
            return r
        elif isinstance(config, range):
            r =  IntegerRange()
            r.adapt(config)
            return r
        return None



"""
"""
if __name__ == '__main__':

    i = Insert('kx_user', 
        company_id=[2, 3, 5], 
        username=EnglishName(unique=True), 
        age=range(20, 90), 
        mobile=ChinaMobile(),
        time=DatetimeRange(begin='2015-12-23', end='2016-12-23'),
        order_id=IntegerRange(begin=100, end=1000, step=2, order='asc'))

    i.set_fields_order(['username', 'age', 'mobile', 'company_id', 'time', 'order_id'])
    i.perform(None, 20)
















