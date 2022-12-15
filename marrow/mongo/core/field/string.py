from .base import Field
from ....schema import Attribute


class String(Field):
	__foreign__ = 'string'
	__disallowed_operators__ = {'#array'}
	
	strip = Attribute(default=False)
	case = Attribute(default=None)
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		value = str(value)
		
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
