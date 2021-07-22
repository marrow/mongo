from typing import Any, Mapping

from ... import Document, F, Field, Filter, P, S
from .queryable import Queryable


# Type hinting helpers.

FieldCache = Mapping[Field, Field]
Operation = Dict[str: Any]  # An operation in the form {'$op': value}
PendingOperations = Dict[Field, Operation]  # Pending operations in the form {'field': {'$op': value}}


class _ActiveField(Field):
	"""A Field mix-in providing basic set/unset tracking useful for implementing the Active Record pattern."""
	
	def __set__(self, obj:Document, value:Any):  # TODO: Active type of Document.
		"""Direct assignment of a value is an authoritative operation which always takes precedence."""
		
		super().__set__(obj, value)  # Pass up the hierarchy so we utilize the final value suitable for backing store.
		
		obj._pending[self.__name__] = {'$set': obj.__data__[self.__name__]}  # Record the change for commit on save.
	
	def __delete__(self, obj:Document):
		"""Record an $unset modification if a field is deleted, or a $set if there is an assignable default."""
		
		super().__delete__(obj)  # Pass up the hierarchy to let the field actually perform the deletion.
		
		if self.assign:
			value = self.default() if callable(self.default) else self.default
			obj.__data__[self.__name__] = value  # TODO: Move to base Field implementation.
			obj._pending[self.__name__] = {'$set': value}
		
		elif self.__name__ in obj.__data__:  # There is only work to perform if the field has a value.
			# We don't need to worry about merging; you can't combine this operation as any prior value is lost.
			obj._pending[self.__name__] = {'$unset': True}


class CachedMixinFactory(dict):
	"""A fancy dictionary implementation that automatically constructs (and caches) new "active" field subclasses.
	
	This relies on two important properties of Python: classes are constructable at runtime, and the class of an
	object instance is itself mutable, that is, the type of an instance can be changed. In the case of the Active
	trait, we need all fields assigned to documents using that trait to be "hot-swapped" for ones which are extended
	to track alterations.
	"""
	def __missing__(self, cls):  # TODO: Enum[Field, type(Field)]
		if isinstance(cls, Field): cls = cls.__class__  # Permit retrieval from instances.
		if not issubclass(cls, Field) or issubclass(cls, _ActiveField): return cls
		
		# This will create a new derivative subclass of the field's class, mixing in _ActiveField from above.
		new_class = cls.__class__('Active' + cls.__name__, (cls, _ActiveField), {})
		
		self[cls] = new_class  # We assign this to avoid constructing new derivative subclasses on each access.
		return new_class


class Active(Queryable):
	"""Where Queryable implements "active collection" behaviours, this trait implements "active record" ones.
	
	Operations which alter the document are gathered in a _pending mapping of fields to the operation and value to
	apply. This mapping is not intended for direct use with PyMongo, instead, invoke the instance's `.save()` method
	or retrieve the body of the update operation by pulling the `.changes` attribute.
	
	The `.update()` method will update the local representation and enqueue those updates within the object for
	execution during `.save()` invocation. This is a notable deviation from the behaviour of other MongoDB DAO layers.
	"""
	
	# Class (global) mapping of Field subclass to variant with _Active mixed-in.
	__field_cache: FieldCache = CachedMixinFactory()
	
	_pending: PendingOperations  # A mapping of field-level operations to apply when saved.
	
	def __init__(self, *args, **kw):
		"""Construct the mapping of pending operations."""
		
		super().__init__(*args, **kw)
		
		self._pending = {}
	
	def __attributed__(self):
		"""Automatically mix active behaviours into field instances used during declarative construction."""
		
		for name, field in self.__attributes__:
			field.__class__ = self.__field_cache[field]
	
	@property
	def changes(self):
		operations = {}
		
		for field, (operation, value) in self._pending.items():
			operations.setdefault(operation, {})
			operations[operation][field] = value
		
		return operations
