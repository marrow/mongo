# encoding: utf-8

from datetime import datetime, timedelta
from bson import ObjectId as oid
from bson.code import Code
from marrow.schema import Attribute

from . import Field


try:
	unicode
	bytes = str
	str = unicode
except:
	str = str
	bytes = bytes


class String(Field):
	__foreign__ = 'string'
	
	def to_foreign(self, obj, name, value):
		return str(value)


class Binary(Field):
	__foreign__ = 'binData'
	
	def to_native(self, obj, name, value):
		return bytes(value)


class ObjectId(Field):
	__foreign__ = 'objectId'
	
	default = Attribute(default=lambda: oid())
	
	def to_foreign(self, obj, name, value):
		if value is None:
			if self.required:
				raise ValueError()
			
			return value
		
		if isinstance(value, oid):
			return value
		
		return oid(str(value))


class Boolean(Field):
	__foreign__ = 'bool'
	
	def to_foreign(self, obj, name, value):
		if value is None:
			return None
		
		try:
			value = value.lower()
		except AttributeError:
			return bool(value)
		
		if value in ('true', 't', 'yes', 'y', 'on', '1', True):
			return True
		
		if value in ('false', 'f', 'no', 'n', 'off', '0', False):
			return False
		
		raise TypeError("Unknown or non-boolean value: " + value)


class Date(Field):
	__foreign__ = 'date'
	
	now = Attribute(default=False)
	autoupdate = Attribute(default=False)
	
	# TODO: use timeparser via context.locale to guess -- https://github.com/thomst/timeparser


class TTL(Date):
	"""A specialized Date field used to store dates in the future by timedelta from now."""
	
	__foreign__ = 'date'
	
	def to_foreign(self, obj, name, value):
		if not value:
			return None
		
		if isinstance(value, timedelta):
			return datetime.utcnow() + value
		
		if isinstance(value, datetime):
			return value
		
		if isinstance(value, int):  # TODO: abc.Number
			return datetime.utcnow() + timedelta(days=value)
		
		# TODO: use timeparser via context.locale to guess -- https://github.com/thomst/timeparser
		raise TypeError("Invalid TTL value: " + repr(value))


class Regex(String):
	__foreign__ = 'regex'


class JavaScript(String):
	scope = Attribute(default=None)
	
	def to_foreign(self, obj, name, value):
		if isinstance(value, tuple):
			return Code(*value)
		
		return Code(value)
	
	@property
	def __foreign__(self):
		if self.scope:
			return 'javascriptWithScope'
		
		return 'javascript'


class Timestamp(Field):
	__foreign__ = 'timestamp'
