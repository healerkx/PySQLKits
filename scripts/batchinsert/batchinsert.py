
# 
import random

class Unique:
    def __init__(self, **flags):
        pass
        

class ValueGenerator:
    def __init__(self, **flags):
        pass


class ListGenerator(ValueGenerator):
    def __init__(self, v):
        self.v = v

    def __next__(self):
        return random.choice(self.v)

class RangeGenerator(ValueGenerator):
    def __init__(self, v):
        self.v = v        

    def __next__(self):
        return random.choice(self.v)

"""
"""
class EnglishName(ValueGenerator):
    def __init__(self):
        self.names = self.load('english_names.txt')

    def load(self, filename):
        # TODO: load names from a file
        return ['Mike', 'Lucy', 'Lily', 'Sophy', 'Chris', 'John']

    def __next__(self):
        name = random.choice(self.names)
        return name

"""
"""
class ChineseName(ValueGenerator):

    def __next__(self):
        pass


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


class Insert:
    table_name = None
    options = None

    def __init__(self, table_name, **options):
        self.table_name = table_name
        self.options = options
        self.fields_order = None

    def __generate_insert(self):
        f = []
        v = []
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
            return ListGenerator(config)
        elif isinstance(config, range):
            return RangeGenerator(config)
        return None



"""
"""
if __name__ == '__main__': 
    i = Insert('kx_user', company_id=[2, 3], username=EnglishName(), age=range(20, 90), mobile=ChinaMobile(Unique=True))
    i.set_fields_order(['username', 'age', 'mobile', 'company_id', ])
    i.perform(None, 3)
















