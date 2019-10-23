from collections.abc import Iterable, Mapping

from ... import Field
from ..types import check_argument_types, Set, List
from .base import _HasKind, _CastingKind


class Array(_HasKind, _CastingKind, Field):
	__foreign__: str = 'array'
	__allowed_operators__: Set[str] = {'#array', '$elemMatch', '#rel', '$eq'}
	
	class List(list):
		"""Placeholder list shadow class to identify already-cast arrays."""
		
		@classmethod
		def new(cls):
			return cls()
	
	def __init__(self, *args, **kw):
		if kw.get('assign', False):
			kw.setdefault('default', self.List.new)
		
		super(Array, self).__init__(*args, **kw)
	
	@property
	def __annotation__(self):
		return List[super().__annotation__]
	
	def to_native(self, obj, name:str, value:Iterable) -> list:
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		if isinstance(value, self.List):
			return value
		
		cast = super().to_native
		result = self.List(cast(obj, name, i) for i in value)
		obj.__data__[self.__name__] = result
		
		return result
	
	def to_foreign(self, obj, name:str, value) -> list:
		"""Transform to a MongoDB-safe value."""
		cast = super().to_foreign
		
		if isinstance(value, Iterable) and not isinstance(value, Mapping):
			return self.List(cast(obj, name, i) for i in value)
		
		return super().to_foreign(obj, name, value)
