

class SqObject:
    def __init__(self):
        self.__type = None
        self.__name = None
        self.__value = None

    def set_type(self, handle_type):
        self.__type = handle_type

    def set_name(self, handle_name):
        self.__name = handle_name

    def set_value(self, handle_value):
        self.__value = handle_value

    def get_type(self):
        return self.__type

    def get_name(self):
        return self.__name

    def get_value(self):
        return self.__value

    def __str__(self):
        return "<Handle '%s'=(%s)>" % (self.__name, self.__value)

    @staticmethod
    def is_sq_object(obj):
        return isinstance(obj, SqObject)