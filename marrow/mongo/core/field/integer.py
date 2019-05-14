from .number import NumberABC, Union


class Integer(Number):
	__foreign__ = 'integer'
	
	def to_foreign(self, obj, name, value:Union[str,NumberABC]) -> int:  # pylint:disable=unused-argument
		return int(value)
