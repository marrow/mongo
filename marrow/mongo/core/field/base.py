# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta
from numbers import Number
from collections import MutableMapping

from bson import ObjectId as OID

from . import Field
from ...util import utcnow, datetime_period
from ....schema import Attribute
from ....schema.compat import unicode


class String(Field):
	__foreign__ = 'string'
	__disallowed_operators__ = {'#array'}
	
	strip = Attribute(default=False)
	case = Attribute(default=None)
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		value = unicode(value)
		
		if self.strip is True:
			value = value.strip()
		elif self.strip:
			value = value.strip(self.strip)
		
		if self.case in (1, True, 'u', 'upper'):
			value = value.upper()
		
		elif self.case in (-1, False, 'l', 'lower'):
			value = value.lower()
		
		elif self.case == 'title':
			value = value.title()
		
		return value


class Binary(Field):
	__foreign__ = 'binData'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return bytes(value)


class ObjectId(Field):
	__foreign__ = 'objectId'
	__disallowed_operators__ = {'#array'}
	
	default = Attribute()
	
	def __fixup__(self, document):
		super(ObjectId, self).__fixup__(document)
		
		try:  # Assign a default if one has not been given.
			self.default
		except AttributeError:
			if self.__name__ == '_id':  # But only if we're actually the primary key.
				self.default = lambda: OID()  # pylint:disable=unnecessary-lambda
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		if isinstance(value, OID):
			return value
		
		if isinstance(value, datetime):
			return OID.from_datetime(value)
		
		if isinstance(value, timedelta):
			return OID.from_datetime(datetime.utcnow() + value)
		
		if isinstance(value, MutableMapping) and '_id' in value:
			return OID(value['_id'])
		
		return OID(unicode(value))


class Boolean(Field):
	__foreign__ = 'bool'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		try:
			value = value.lower()
		except AttributeError:
			return bool(value)
		
		if value in ('true', 't', 'yes', 'y', 'on', '1', True):
			return True
		
		if value in ('false', 'f', 'no', 'n', 'off', '0', False):
			return False
		
		raise ValueError("Unknown or non-boolean value: " + value)


class Date(Field):
	__foreign__ = 'date'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		if isinstance(value, OID):
			return value.generation_time
		
		return value


class Period(Date):
	"""A specialized Date field used to store dates rounded down to the start of a given period."""
	
	hours = Attribute(default=None)
	minutes = Attribute(default=None)
	seconds = Attribute(default=None)
	
	@property
	def delta(self):
		return timedelta(hours=self.hours or 0, minutes=self.minutes or 0, seconds=self.seconds or 0)
	
	def to_foreign(self, obj, name, value):
		value = super(Period, self).to_foreign(obj, name, value)
		
		return datetime_period(value, hours=self.hours, minutes=self.minutes, seconds=self.seconds)


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


class Regex(String):
	__foreign__ = 'regex'
	__disallowed_operators__ = {'#array'}


class Timestamp(Field):
	__foreign__ = 'timestamp'
	__disallowed_operators__ = {'#array'}
