# encoding: utf-8

from __future__ import unicode_literals

from .base import Field
from ....schema import Attribute


class Boolean(Field):
	__foreign__ = 'bool'
	__disallowed_operators__ = {'#array'}
	
	truthy = Attribute(default=('true', 't', 'yes', 'y', 'on', '1', True))
	falsy = Attribute(default=('false', 'f', 'no', 'n', 'off', '0', False))
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		try:
			value = value.lower()
		except AttributeError:
			return bool(value)
		
		if value in self.truthy:
			return True
		
		if value in self.falsy:
			return False
		
		raise ValueError("Unknown or non-boolean value: " + value)
