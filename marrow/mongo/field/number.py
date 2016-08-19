# encoding: utf-8

from bson.int64 import Int64
from decimal import Decimal

from ..core import Field


class Number(Field):
	__foreign__ = 'number'
	
	def to_foreign(self, obj, name, value):
		try:
			return int(value)
		except ValueError:
			return float(value)
		
		return value


class Double(Number):
	__foreign__ = 'double'
	
	def to_foreign(self, obj, name, value):
		return float(value)


class Integer(Number):
	__foreign__ = 'integer'
	
	def to_foreign(self, obj, name, value):
		return int(value)


class Long(Number):
	__foreign__ = 'long'
	
	def to_foreign(self, obj, name, value):
		return Int64(int(value))


class Decimal(Number):
	"""A 128-bit IEEE 754-2008 deimal floating point number.
	
	Note: this is only compatible with MongoDB 3.4 and compatible, updated driver that exposes Decimal support.
	"""
	__foreign__ = 'decimal'
	
	def to_foreign(self, obj, name, value):
		return Decimal(value)

