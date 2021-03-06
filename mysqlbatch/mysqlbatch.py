#! python3 
from dateutil import parser as DateParse
import pytoml
import pymysql
from optparse import OptionParser
import random, re, sys, time, hashlib
from functools import cmp_to_key
from methods import *

def usage():
    return """
    Any
    """

def handle_open_close(exp: str, s: int, e: int):
    if exp.startswith("("): s += 1
    if exp.endswith("]"): e += 1
    return range(s, e)

def parse_int_range(exp: str):
    exp = exp.strip()
    digits = re.findall("\s*\d+\s*", exp)
    s, e = int(digits[0]), int(digits[1])
    return handle_open_close(exp, s, e)

def parse_time_range(exp: str):
    exp = exp.strip()
    times = re.findall("\s*\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}\s*", exp)
    s, e = unixtime(times[0]), unixtime(times[1])
    return handle_open_close(exp, s, e)

g_generator_types = dict()
g_source_types = dict()

def FieldValueGenerator(**args):
    generator_name = args['name']
    if not generator_name:
        print("FieldValueGenerator MUST have a name")
        exit()
    def field_value_generator(clz):
        class FieldValueGeneratorClass(clz):
            args = dict()
            source = None
            method = None

            def set_field_name(self, field_name):
                self.field_name = field_name

            def get_field_name(self):
                return self.field_name

            def set_source(self, source):
                self.source = source

            def get_source(self):
                return self.source

            def get_generator_name(self):
                return generator_name

            def set_method(self, method):
                self.method = method
            
            def get_method(self):
                return self.method

        g_generator_types[generator_name] = FieldValueGeneratorClass
        return FieldValueGeneratorClass
           
    return field_value_generator


@FieldValueGenerator(name='random')
class RandomGenerator:
    def __str__(self):
        return "<Random(%s)>" % self.get_field_name()

    def __next__(self):
        v = random.choice(self.get_source())
        method = self.get_method()
        if method:
            return method(v)
        else:
            return v

@FieldValueGenerator(name='rolling')
class RollingGenerator:
    def __str__(self):
        return "<Rolling(%s)>" % self.get_field_name()

    def initialize(self):
        self.iterator = iter(self.get_source())

    def __next__(self):
        try:
            v = next(self.iterator)
            method = self.get_method()
            if method:
                return method(v)
            else:
                return v            
        except:
            self.iterator = iter(self.iterator)


@FieldValueGenerator(name='depends')
class DependsGenerator:
    reletive_row_index = 0
    __field_name = ''
    method = None
    field_index = -1

    def __str__(self):
        return "<!Depends %s>" % self.get_field_name()

    def initialize(self):
        if 'field_name' in self.args:
            self.__field_name = self.args['field_name']
        if 'init_value' in self.args:
            self.init_value = self.args['init_value']
        if 'converter' in self.args:
            self.converter = self.args['converter']

    def set_depends_field_name(self, field_name):
        self.depends_field_name = field_name
    
    def set_row_data(self, row_data, last_row_data):
        self.row_data = row_data
        self.last_row_data = last_row_data

    def __next__(self):
        if self.reletive_row_index == 0:
            v = self.row_data[self.depends_field_name]
            method = self.get_method()
            if method:
                return method(v)
            else:
                return v  
        elif self.reletive_row_index == -1:
            raise Exception("???")
            if not self.last_row_data:
                return self.init_value
            if self.converter:
                return self.converter(self.last_row_data[self.field_index])
            else:
                return self.last_row_data[self.field_index]

@FieldValueGenerator(name='china.mobile')
class ChinaMobileGenerator:
    def __next__(self):
        t = str(random.choice([3, 4, 5])) + str(random.randint(0, 9))
        return "1%s%s%s" % (t, random.randint(1000, 9999), random.randint(1000, 9999))

def depends_depth_cmp(x, y) -> int:
    return 0

def generator_cmp(x, y) -> int:
    gn1 = x.get_generator_name()
    gn2 = y.get_generator_name()
    if gn1 == 'depends' and gn2 == 'depends':
        return depends_depth_cmp(x, y)
    if gn1 == 'depends':
        return 1
    if gn2 == 'depends':
        return -1
    return -1
        

"""
main class for insertion
"""
class RowsDataGenerator:
    __table_name = None
    __config = None
    related_data_source = None
    last_row = None
    format = 'insert'

    def __init__(self, config: dict):
        self.__table_name = config['table']['name']
        print("table name -> %s" % self.__table_name)
        self.__config = config

    def set_related_data_source(self, related_data_source):
        self.related_data_source = related_data_source

    def __generate_value(self, times, i, sorted_generator_list):
        f, v, row_data = [], [], dict()
        # field_names = self.__config['field'].keys()
        for generator in sorted_generator_list:
            # print(generator)
            field = generator.get_field_name()
            f.append(field)
            
            # if not generator:
            #     print("No generator for field `%s`" % field)
            if isinstance(generator, DependsGenerator):   
                generator.set_row_data(row_data, self.last_row)

            if generator is None:
                row_data[field] = None
                v.append("null")
            else:
                val = next(generator)
                row_data[field] = val
                if isinstance(val, str):
                    # print("#", generator, val)
                    v.append("'%s'" % str(val))
                elif isinstance(val, int) or isinstance(val, float):
                    v.append("%s" % str(val))
                else:
                    v.append(val)
        
        self.last_row = row_data

        if self.format == 'inserts':
            return "insert into `%s` (%s) values (%s);" % (self.table_name, ", ".join(f), ", ".join(v))
        elif self.format == 'insert':
            return "(%s)%s " % (", ".join(v), ',' if times - i > 1 else ';')
        elif self.format == 'csv':
            v = list(map(lambda x: x.strip("'"), v))
            return ','.join(v)

    def generate(self, times, file):
        self.__generators = {}
        
        field_configs = self.__config['field']
        for field_name in field_configs:
            generator = self.create_generator(field_name)
            self.__generators[field_name] = generator

        generator_list = list(self.__generators.values())
        for generator in generator_list:
            pass
        sorted_generator_list = sorted(generator_list, key=cmp_to_key(generator_cmp))
        
        fields = [generator.get_field_name() for generator in sorted_generator_list]

        if self.format == 'csv':
            file.write(','.join(fields) + "\n")
        elif self.format == 'insert':
            fields_list = map(lambda x: "`%s`" % x, fields)
            insert = "insert into `%s` (%s) values " % (self.__table_name, ", ".join(fields_list))
            
            file.write(insert + "\n")

        for i in range(0, times):
            value = self.__generate_value(times, i, sorted_generator_list)
            yield value

            #if self.related_data_source is not None:
            #    self.related_data_source.reset_choice()


    def perform(self, times, filename, format='inserts'):
        encoding = 'utf-8'
        if format == 'csv':
            encoding = 'gbk'
        file = open(filename, 'w', encoding=encoding)

        self.format = format
        for line in self.generate(times, file):
            file.write(line + "\n")

        file.close()

    def create_generator(self, field_name):
        field_config = self.__config['field'][field_name]
        generator_name = field_config['generator']
        g = None
        if generator_name not in g_generator_types:
            print("Not this generator named `%s`" % generator_name)
            exit()

        generator_type = g_generator_types[generator_name]
        g = generator_type()
        g.set_field_name(field_name)

        source = None
        if 'source' in field_config:
            source_def = field_config['source']
            if isinstance(source_def, list):
                source = source_def
            elif source_def.startswith('int.range'):
                source = parse_int_range(source_def[len('int.range'):])
            elif source_def.startswith('time.range'):
                source = parse_time_range(source_def[len('time.range'):])
        elif 'sourcefile' in field_config:
            with open(field_config['sourcefile'], 'r', encoding='UTF-8') as file:
                lines = file.readlines()
                source = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), lines)))
        if generator_name == "depends":
            g.set_depends_field_name(field_config['depends'])

        if 'method' in field_config:
            g.set_method(load_method(field_config['method']))

        g.set_source(source)
        if hasattr(g, 'initialize'):
            g.initialize()

        return g

def perform(toml: dict, options):
    toml['times'] = int(options.times)
    toml['filename'] = options.filename
    toml['database'] = options.database
    gen = RowsDataGenerator(toml)
    gen.perform(int(options.times), options.filename, "insert")

def main(options, args):
    with open(options.config, "rb") as file:
        toml = pytoml.load(file)
    if not toml:
        print("Bad toml file")
        exit()

    perform(toml, options)

"""
"""
if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-d", "--database", action="store", dest="database", help="Provide destination database")
    parser.add_option("-c", "--config", action="store", dest="config", help="Provide config file")
    parser.add_option("-o", "--operate", action="store", dest="operate", help="Provide config operate", default="inserts")
    parser.add_option("-t", "--times", action="store", dest="times", help="Provide config times", default="20")
    parser.add_option("-f", "--filename", action="store", dest="filename", help="Provide config filename", default="insert.sql")

    options, args = parser.parse_args()
    if not options.config:
        print(usage())
        exit()
    main(options, args)
