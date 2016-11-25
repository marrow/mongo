# encoding: utf-8

from numbers import Number as NumberABC
from bson.int64 import Int64

from . import Field
from ...util.compat import unicode


class Number(Field):
	__foreign__ = 'number'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # noqa
		if isinstance(value, NumberABC):
			return value
		
		if isinstance(value, unicode):
			if value.isnumeric():
				return int(value)
			else:
				return float(value)
		
		return int(value)


class Double(Number):
	__foreign__ = 'double'
	
	def to_foreign(self, obj, name, value):  # noqa
		return float(value)


class Integer(Number):
	__foreign__ = 'integer'
	
	def to_foreign(self, obj, name, value):  # noqa
		return int(value)


class Long(Number):
	__foreign__ = 'long'
	
	def to_foreign(self, obj, name, value):  # noqa
		return Int64(int(value))
