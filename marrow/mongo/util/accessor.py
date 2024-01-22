"""Data attributes (properties) useful in conjunction with Marrow Mongo data model classes."""

from typing import Any, Optional, Union
from warnings import warn

from marrow.mongo.field import Set
from marrow.mongo.trait import Queryable


class Flag:
	"""Given a Set field, allow access and manipulation of a specific element as a boolean.
	
	While it's preferable to directly access the set itself, this field-like data attribute can be a useful shortcut
	and provide a mechanism for generating query fragments. For example:
	
		for administrator in Account.admin: ...
	"""
	
	__slots__ = ('field', 'value', 'deprecate')
	
	field: Set  # A target field to add or remove values from.
	value: Any  # The value to look for (and add or remove from) the backing field.
	deprecate: Optional[Union[bool,str]]  # Generate (if True) or utilize an explicit deprecation warning on access.
	
	def __init__(self, field:Set, value:Any, deprecate:Optional[Union[bool,str]]=None):
		self.field = field
		self.value = value
		self.deprecate = deprecate
	
	def __get__(self, obj, cls=None) -> bool:
		if self.deprecate is True:
			warn(f"Utilize `{self.value!r} in .{self.field.__name__}` directly.", DeprecationWarning)
		elif self.deprecate:
			warn(self.deprecate, DeprecationWarning)
		
		if obj is None:  # Direct class-level access generates a query fragment.
			return getattr(cls, self.field.__name__) == self.value
		
		return self.value in getattr(obj, self.field.__name__)  # TODO: Cast.
	
	def __set__(self, obj, value:bool):
		storage = obj[self.field.__name__]
		
		if deprecate and not isinstance(deprecate, bool):
			self.deprecate: warn(self.deprecate, DeprecationWarning)
		
		if value:
			if self.deprecate is True: warn(f"Utilize `{self.field.__document__.__name__.lower()}.{self.field.__name__}.add({self.value!r})` directly.", DeprecationWarning)
			if self.value not in storage: storage.append(self.value)  # TODO: Cast.
		else:
			if self.deprecate is True: warn(f"Utilize `{self.field.__document__.__name__.lower()}.{self.field.__name__}.discard({self.value!r})` directly.", DeprecationWarning)
			if self.value in storage: storage.remove(self.value)  # TODO: Cast.
	
	def __delete__(self, obj):
		if self.deprecate is True: warn(f"Utilize `{self.field.__document__.__name__.lower()}.{self.field.__name__}.discard({self.value!r})` directly.", DeprecationWarning)
		elif self.deprecate: warn(self.deprecate, DeprecationWarning)
		
		storage = obj[self.field.__name__]
		if self.value in storage: storage.remove(self.value)  # TODO: Cast.


def QueryAttribute(model:Optional[Union[str,Queryable]], field:str):
	if isinstance(model, str):
		model: Queryable = getattr(__import__('marrow.mongo.document').mongo.document, model)
	
	@property
	def inner(self):
		return getattr(model or self, field) == self  # Produce an iterable and combinable query fragment.
	
	return inner

