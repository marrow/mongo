from .number import Number, NumberABC, Union


class Double(Number):
	__foreign__ = 'double'
	
	def to_foreign(self, obj, name:str, value:Union[str,NumberABC]) -> float:  # pylint:disable=unused-argument
		return float(value)
