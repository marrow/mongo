from .array import Array


class Set(Array):
	List = list
	__annotation__ = set
	
	def to_native(self, obj, name:str, value) -> set:  # pylint:disable=unused-argument
		result = super(Set, self).to_native(obj, name, value)
		
		if result is not None:
			result = set(result)
		
		return result
