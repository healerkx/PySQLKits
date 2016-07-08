
"""
"""
class Func:
    func_name = None
    args = []

    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def __str__(self):
        """
        For dump the Func object
        """
        args_str_list = []
        for arg in self.args:
            if isinstance(arg, str):
                arg = "'%s'" % arg
            args_str_list.append(str(arg))
        args_str = ', '.join(args_str_list)
        return "<%s(%s)>" % (self.func_name, args_str)

