# encoding: utf-8

from __future__ import unicode_literals

from .base import Field
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
