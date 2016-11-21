# encoding: utf-8

from datetime import datetime, timedelta
from numbers import Number
from bson import ObjectId as oid
from bson.code import Code
from marrow.schema import Attribute

from . import Field
from ...util.compat import unicode


class String(Field):
	__foreign__ = 'string'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):
		return unicode(value)


class Binary(Field):
	__foreign__ = 'binData'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):
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
				self.default = lambda: oid()
	
	def to_foreign(self, obj, name, value):
		if isinstance(value, oid):
			return value
		
		if isinstance(value, datetime):
			return oid.from_datetime(value)
		
		if isinstance(value, timedelta):
			return oid.from_datetime(datetime.utcnow() + value)
		
		return oid(unicode(value))


class Boolean(Field):
	__foreign__ = 'bool'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):
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
	
	now = Attribute(default=False)
	autoupdate = Attribute(default=False)
	
	# TODO: use timeparser via context.locale to guess -- https://github.com/thomst/timeparser


class TTL(Date):
	"""A specialized Date field used to store dates in the future by timedelta from now."""
	
	__foreign__ = 'date'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):
		if isinstance(value, timedelta):
			return datetime.utcnow() + value
		
		if isinstance(value, datetime):
			return value
		
		if isinstance(value, Number):
			return datetime.utcnow() + timedelta(days=value)
		
		# TODO: use timeparser via context.locale to guess -- https://github.com/thomst/timeparser
		raise ValueError("Invalid TTL value: " + repr(value))


class Regex(String):
	__foreign__ = 'regex'
	__disallowed_operators__ = {'#array'}


class Timestamp(Field):
	__foreign__ = 'timestamp'
	__disallowed_operators__ = {'#array'}
