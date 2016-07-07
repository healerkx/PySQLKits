
from .SqObject import *

class DatasetObject(SqObject):
    __filters = None
    
    def __init__(self):
        super().__init__()
        
    def set_filters(self, filters):
        self.__filters = filters

    def get_filters(self):
        return self.__filters

    def set_default_fields(self, fields):
        self.__default_fields = fields

    def get_default_fields(self):
        return self.__default_fields        