from .base import Field


class Binary(Field):
	__foreign__ = 'binData'
	__disallowed_operators__ = {'#array'}
	__annotation__ = bytes
	
	def to_foreign(self, obj, name:str, value) -> bytes:  # pylint:disable=unused-argument
		return bytes(value)
