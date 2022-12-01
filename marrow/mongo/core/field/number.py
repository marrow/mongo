from numbers import Number as NumberABC

from .base import Field


class Number(Field):
	__foreign__ = 'number'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		if isinstance(value, NumberABC):
			return value
		
		if isinstance(value, str):
			if value.isnumeric():
				return int(value)
			else:
				return float(value)
		
		return int(value)
