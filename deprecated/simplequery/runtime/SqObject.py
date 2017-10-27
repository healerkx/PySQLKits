
"""
SqObject is the base class for all Types in SimpleQuery-lang

"""
class SqObject:
    def __init__(self):
        self.__name = None
        self.__value = None

    def set_name(self, handle_name):
        self.__name = handle_name

    def set_value(self, handle_value):
        self.__value = handle_value

    def get_name(self):
        return self.__name

    def get_value(self):
        return self.__value

    def __str__(self):
        return "<Object '%s': (%s)>" % (self.__name, self.__value)

    @staticmethod
    def is_sq_object(obj):
        return isinstance(obj, SqObject)