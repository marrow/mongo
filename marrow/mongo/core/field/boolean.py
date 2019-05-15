from typing import Sequence

from .base import Field
from ....schema import Attribute


class Boolean(Field):
	__foreign__ = 'bool'
	__disallowed_operators__ = {'#array'}
	
	truthy: Sequence = Attribute(default=('true', 't', 'yes', 'y', 'on', '1', True))
	falsy: Sequence = Attribute(default=('false', 'f', 'no', 'n', 'off', '0', False))
	
	def to_foreign(self, obj, name:str, value) -> bool:  # pylint:disable=unused-argument
		try:
			value = value.lower()
		except AttributeError:
			pass
		
		if value in self.truthy:
			return True
		
		if value in self.falsy:
			return False
		
		return bool(value)
