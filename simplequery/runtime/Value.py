

from .SqObject import *

class ValueObject(SqObject):

    def __init__(self, dataset):
        super(SqObject, self)
        self.dataset = dataset