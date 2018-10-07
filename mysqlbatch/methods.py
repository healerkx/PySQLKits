#! python3 
from dateutil import parser as DateParse
import pytoml
import MySQLdb
from optparse import OptionParser
from functools import *
import random, re, sys, time, hashlib

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

@method("unix_time")
def unix_time(datestr):
    return unixtime(datestr)

print(unix_time("2018-01-01"))


def identity(x):
    return x

def get_method(method_name):
    if method_name in g_methods:
        return g_methods[method_name]
    return identity

