# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta
from numbers import Number

from .date import Date
from ...util import utcnow


class TTL(Date):
	"""A specialized Date field used to store dates in the future by timedelta from now."""
	
	__foreign__ = 'date'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):
		if isinstance(value, timedelta):
			value = utcnow() + value
		elif isinstance(value, datetime):
			value = value
		elif isinstance(value, Number):
			value = utcnow() + timedelta(days=value)
		else:
			raise ValueError("Invalid TTL value: " + repr(value))
		
		return super(TTL, self).to_foreign(obj, name, value)
