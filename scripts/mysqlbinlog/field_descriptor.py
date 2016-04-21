
from mysqldef import *

dh = DescriptorHandler()


class base_descriptor:
	def handle(self, metadata):
		return metadata[self.metadata_len:]

	@property
	def nullable(self):
		return self.__nullable

	@nullable.setter
	def nullable(self, value):
		self.__nullable = value

	def get_max_len(self):
		if 'max_len' in self.__dict__:	# TODO:
			return self.max_len
		return '@'

@dh.handle(FieldType.UNKNOWN)
class unknown_descriptor(base_descriptor):
	def __init__(self, metadata):
		self.metadata_len = 0

@dh.handle(FieldType.DECIMAL)
class decimal_descriptor(base_descriptor):
	def __init__(self, metadata):
		self.metadata_len = 0

# VARCHAR, STRING
"""
VARCHAR
"""
@dh.handle(FieldType.VARCHAR)
class varchar_descriptor(base_descriptor):
	def __init__(self, metadata):
		self.metadata_len = 2
		self.max_len = metadata[0] | metadata[1] * 256

def get_descriptor(col_type, metadata, nullable):

	handler_class = dh.get_handler_class(col_type)
	# print(col_type, handler_class)
	handler = handler_class(metadata)
	handler.nullable = nullable
	metadata = handler.handle(metadata)

	# print(handler.nullable)

	return handler, metadata
