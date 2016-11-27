# encoding: utf-8

from __future__ import unicode_literals

from numbers import Number as NumberABC

from bson.int64 import Int64

from . import Field
from ....schema.compat import unicode


class Number(Field):
	__foreign__ = 'number'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
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
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return float(value)


class Integer(Number):
	__foreign__ = 'integer'
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return int(value)


class Long(Number):
	__foreign__ = 'long'
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return Int64(int(value))
