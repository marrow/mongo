from .base import Field


class Binary(Field):
	__foreign__ = 'binData'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value) -> bytes:  # pylint:disable=unused-argument
		return bytes(value)
