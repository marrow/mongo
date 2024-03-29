from .number import Number


class Double(Number):
	__foreign__ = 'double'
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return float(value)
