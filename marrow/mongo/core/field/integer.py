from .number import NumberABC, Union

from .number import Number


class Integer(Number):
	__foreign__ = 'integer'
	__annotation__ = int
	
	def to_foreign(self, obj, name:str, value:Union[str,NumberABC]) -> int:  # pylint:disable=unused-argument
		return int(value)
