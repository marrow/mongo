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
		value = super(TTL, self).to_foreign(obj, name, value)
		
		if isinstance(value, timedelta):
			return utcnow() + value
		
		if isinstance(value, datetime):
			return value
		
		if isinstance(value, Number):
			return utcnow() + timedelta(days=value)
		
		raise ValueError("Invalid TTL value: " + repr(value))
