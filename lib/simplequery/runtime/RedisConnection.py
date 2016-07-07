
from .SqObject import *

class RedisConnectionObject(SqObject):

    def __init__(self, conn):
        super(SqObject, self)
        self.conn = conn