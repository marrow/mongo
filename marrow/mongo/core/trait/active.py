from inspect import isclass
from typing import Any, Mapping

from ... import Document, F, Field, Filter, P, S
from ..query import Update
from .queryable import Queryable


SENTINEL = object()


class _ActiveField(Field):
	"""A Field mix-in providing basic set/unset tracking useful for implementing the Active Record pattern.
	
	This assumes a host object having a `_pending` attribute that is a mapping of field names to pending operations.
	"""
	
	def __set__(self, obj:Document, value:Any) -> None:
		"""Direct assignment of a value is an authoritative operation which always takes precedence."""
		
		before = obj.__data__.get(self.__name__, SENTINEL)
		super().__set__(obj, value)  # Pass up the hierarchy so we utilize the final value suitable for backing store.
		
		if before != obj.__data__.get(self.__name__, SENTINEL):  # Only if the stored value has changed do we...
			self._queue_operation(obj)  # ...record the change for commit on save.
			# Note, SENTINEL == SENTINEL so a value missing before and after is not a change.
	
	def __delete__(self, obj:Document) -> None:
		"""Record an $unset modification if a field is deleted, or a $set if there is an assignable default."""
		
		super().__delete__(obj)  # Pass up the hierarchy to let the field actually perform the deletion or assignment.
		self._queue_operation(obj)  # Record the change for commit on save.
	
	def _queue_operation(self, obj:Document) -> None:
		if self.__name__ in obj.__data__:  # Field was assigned a value.
			obj._pending[self.__name__] = {'$set': obj.__data__[self.__name__]}
		else:  # Field was physically removed from the backing store.
			obj._pending[self.__name__] = {'$unset': True}  # E.g. assign None when nullable=False, or deletion.


# Type hinting helpers.
FieldCache = Mapping[Field, _ActiveField]
Operation = Mapping[str, Any]  # An operation in the form {'$op': value} -- should be BasicType, not Any.
PendingOperations = Mapping[str, Operation]  # Pending operations in the form {'field': {'$op': value}}


class CachedMixinFactory(dict):
	"""A fancy dictionary implementation that automatically constructs (and caches) new "active" field subclasses.
	
	This relies on two important properties of Python: classes are constructable at runtime, and the class of an
	object instance is itself mutable, that is, the type of an instance can be changed. In the case of the Active
	trait, we need all fields assigned to documents using that trait to be "hot-swapped" for ones which are extended
	to track alterations. Additionally, the fields themselves can be extended to expose update operations.
	"""
	def __missing__(self, cls:Field) -> _ActiveField:
		if isinstance(cls, Field): cls = cls.__class__  # Permit retrieval from instances.
		if isclass(cls):
			if not issubclass(cls, Field):
				raise ValueError("Must map Field instances or classes.")
			if issubclass(cls, _ActiveField): return cls
		
		# This will create a new derivative subclass of the field's class, mixing in _ActiveField from above.
		new_class = cls.__class__('Active' + cls.__name__, (cls, _ActiveField), {})
		
		self[cls] = new_class  # We assign this to avoid constructing new derivative subclasses on each access.
		return new_class


class Active(Queryable):
	"""Where Queryable implements "active collection" behaviours, this trait implements "active record" ones.
	
	Operations which alter the document are gathered in a _pending mapping of fields to the operation and value to
	apply. This mapping is not intended for direct use with PyMongo, instead, invoke the instance's `.save()` method
	or retrieve the body of the update operation by pulling the `._changes` attribute.
	
	The `.update()` method will update the local representation and enqueue those updates within the object for
	execution during `.save()` invocation. This is a notable deviation from the behaviour of other MongoDB DAO layers:
	you will still need to `.save()` the instance to persist the changes in MongoDB.
	"""
	
	# Class (global) mapping of Field subclass to subclass variants with _Active mixed-in.
	# These are automatically constructed on an as-needed basis the first time a derivative is requested.
	__field_cache: FieldCache = CachedMixinFactory()
	
	_pending: PendingOperations  # A mapping of field-level operations to apply when saved.
	
	def __init__(self, *args, **kw):
		"""Prepare an Active instance by constructing a mapping of pending operations, pass arguments through."""
		
		super().__init__(*args, **kw)
		
		self._pending = {}
	
	@classmethod
	def __attributed__(self):
		"""Automatically mix active behaviours into field instances used during declarative construction."""
		
		super().__attributed__()
		
		for name, field in self.__attributes__.items():
			field.__class__ = self.__field_cache[field]
	
	@property
	def is_dirty(self):
		return bool(self._pending)
	
	@property
	def as_update_document(self):
		"""Pivot the per-field operations to operations containing their field references as MongoDB prefers.
		
		Multiple operations can not be performed against a single field anyway: internal storage of field:operation
		prevents confusion that may arise if it seems we might allow:
		
			db.example.update({}, {'$set': {"age": 17}, '$inc': {"age": 1}})
		
		If attempted, the above results in the following error message:
		
			Updating the path 'age' would create a conflict at 'age'
		"""
		
		operations = {}
		
		for field, (operation, value) in self._pending.items():
			operations.setdefault(operation, {})
			operations[operation][field] = value
		
		return Update(operations)
	
	def save(self, **kw):
		if self._pending:
			return self.update_one(self.as_update_document, **kw)
		
		return self.replace_one(True, **kw)
