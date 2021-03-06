#! python3 
from dateutil import parser as DateParse
import pytoml
from optparse import OptionParser
import random, re, sys, time, hashlib, base64

g_methods = dict()

def method(name):
    def m(func):
        def inner(a):
            return func(a)
        g_methods[name] = func
        return inner
    
    return m

def unixtime(datestr):
    return int(DateParse.parse(datestr).timestamp())

@method("md5")
def md5(s):
    return hashlib.new('md5', str(s).encode("utf8")).hexdigest()

@method("format_time")
def format_time(unix_timestamp):
    time_s = time.localtime(int(unix_timestamp))
    return time.strftime("%Y-%m-%d %H:%M:%S", time_s) 


@method("unix_time")
def unix_time(datestr):
    return unixtime(datestr)    

@method("base64encode")
def base64encode(s):
    return base64.b64encode(s)

@method("strlen")
def strlen(s):
    return len(str(s))

def identity(x):
    return x

def load_method(method_name):
    if method_name in g_methods:
        return g_methods[method_name]
    return identity

