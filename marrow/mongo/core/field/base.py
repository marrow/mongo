from collections import namedtuple
from inspect import isclass
from weakref import proxy

from ....package.loader import traverse, load
from ....schema import Attribute
from ....schema.transform import BaseTransform
from ....schema.validate import Validator
from ...query import Q
from ...util import adjust_attribute_sequence, SENTINEL
from ...types import Any, Sequence, Optional, Mapping, Iterable, Set, TypeVar


FieldContext = namedtuple('FieldContext', 'field,document')
FieldType = TypeVar("FieldType", bound="Field")


class FieldTransform(BaseTransform):
	def foreign(self, value, context):  # pylint:disable=signature-differs
		field, document = context
		
		if hasattr(field, 'to_foreign'):
			return field.to_foreign(document, field.__name__, value)
		
		return value
	
	def native(self, value, context):  # pylint:disable=signature-differs
		field, document = context
		
		if hasattr(field, 'to_native'):
			return field.to_native(document, field.__name__, value)
		
		return value


@adjust_attribute_sequence(1000, 'transformer', 'validator', 'positional', 'assign', 'repr', 'project', 'read', 'write', 'sort')
class Field(Attribute):
	# Possible values for operators include any literal $-prefixed operator, or one of:
	#  * #rel -- allow/prevent all relative comparison such as $gt, $gte, $lt, etc.
	#  * #array -- allow/prevent all array-related compraison such as $all, $size, etc.
	#  * #document -- allow/prevent all document-related comparison such as $elemMatch.
	#  * #geo -- allow/prevent geographic query operators
	__allowed_operators__: Set[str] = set()
	__disallowed_operators__: Set[str] = set()
	__document__ = None  # The Document subclass the field originates from.
	__foreign__ = {}
	__acl__ = []  # Overall document access control list.
	__annotation__ = Any
	
	# Inherits from Attribute: (name is usually, but not always the first positional parameter)
	# name - The database-side name of the field, stored as __name__, defaulting to the attribute name assigned to.
	# default - No default is provided by default; access will raise AttributeError.
	
	choices: Iterable = Attribute(default=None)  # The permitted set of values; may be static or a dynamic callback.
	required: bool = Attribute(default=False)  # Must have value assigned; None and an empty string are values.
	nullable: bool = Attribute(default=False)  # If True, will store None.  If False, will store non-None default, or not store.
	exclusive: Optional[bool] = Attribute(default=None)  # The set of other fields that must not be set for this field to be settable.
	
	# Local Manipulation
	
	transformer = Attribute(default=FieldTransform())  # A Transformer class to use when loading/saving values.
	validator = Attribute(default=Validator())  # The Validator class to use when validating values.
	assign: bool = Attribute(default=False)  # If truthy attempt to access and store resulting variable when instantiated.
	
	# Predicates
	
	positional: bool = Attribute(default=True)  # If True, will be accepted positionally.
	repr: bool = Attribute(default=True)  # Should this field be included in the programmers' representation?
	project: Optional[bool] = Attribute(default=None)  # Predicate to indicate inclusion in the default projection.
	read: bool = Attribute(default=True)  # Read predicate, either a boolean, callable, or web.security ACL predicate.
	write: bool = Attribute(default=True)  # Write predicate, either a boolean, callable, or web.security ACL predicate.
	sort: bool = Attribute(default=True)  # Sort predicate, either a boolean, callable, or web.security ACL predicate.
	
	def adapt(self, **kw) -> FieldType:
		instance = self.__class__()
		instance.__data__ = self.__data__.copy()
		
		for k, v in kw.items():
			setattr(instance, k, v)
		
		return instance
	
	def __repr__(self) -> str:
		fields = []
		
		for field in self.__attributes__.values():
			name = field.__name__
			
			if name in ['__name__']:
				continue
			
			if name not in self.__data__:
				continue
			
			default = getattr(field, 'default', SENTINEL)
			value = self.__data__[name]
			
			if value != default:
				fields.append((field.__name__, value))
		
		if fields:
			fields = ', '.join(f"{field}={value!r}" for field, value in fields)
			fields = ', ' + fields
		else:
			fields = ''
		
		name = getattr(self, '__name__', '<anonymous>')
		
		return f"{self.__class__.__name__}('{name}'{fields})"
	
	# Security Predicate Handling
	
	def _predicate(self, predicate, context=None) -> bool:
		if callable(predicate):
			if context:
				return predicate(context, self)
			else:
				return predicate(self)
		
		return bool(predicate)
	
	def is_readable(self, context=None) -> bool:
		return self._predicate(self.read, context)
	
	def is_writeable(self, context=None) -> bool:
		return self._predicate(self.write, context)
	
	def is_sortable(self, context=None) -> bool:
		return self._predicate(self.sort, context)
	
	# Marrow Schema Interfaces
	
	def __init__(self, *args, **kw):
		super().__init__(*args, **kw)
		
		if self.nullable:  # If no default is specified, but the field is nullable, set the default to None.
			try:
				self.default
			except AttributeError:
				self.default = None
	
	def __fixup__(self, document):
		"""Called after an instance of our Field class is assigned to a Document."""
		self.__document__ = proxy(document)
	
	# Descriptor Protocol
	
	def __get__(self, obj, cls=None):
		"""Executed when retrieving a Field instance attribute."""
		
		# If this is class attribute (and not instance attribute) access, we return a Queryable interface.
		if obj is None:
			return Q(cls, self)
		
		result = super().__get__(obj, cls)
		
		if result is None:  # Discussion: pass through to the transformer?
			return None
		
		return self.transformer.native(result, FieldContext(self, obj))
	
	def __set__(self, obj, value):
		"""Executed when assigning a value to a Field instance attribute."""
		
		if self.exclusive:
			for other in self.exclusive:
				try:  # Handle this with kid gloves, just in case.
					ovalue = traverse(obj, other, None)
				except LookupError:  # pragma: no cover
					pass
				
				if ovalue is not None:
					raise AttributeError("Can not assign to " + self.__name__ + " if " + other + " has a value.")
		
		if value is not None:
			self.validator.validate(value, FieldContext(self, obj))
			value = self.transformer.foreign(value, FieldContext(self, obj))
		
		super().__set__(obj, value)
	
	def __delete__(self, obj):
		"""Executed via the `del` statement with a Field instance attribute as the argument."""
		
		# Delete the data completely from the warehouse.
		del obj.__data__[self.__name__]
	
	# Other Python Protocols
	
	def __str__(self) -> str:
		return self.__name__


class _HasKind(Field):
	"""A mix-in to provide an easily definable singular or plural set of document types."""
	
	kind = Attribute(default=None)  # A reference to a document class (explicitly, or by string name) or field instance.
	
	def __init__(self, *args, **kw):
		if args:
			kw['kind'], args = args[0], args[1:]
		
		super().__init__(*args, **kw)
	
	@property
	def __annotation__(self):
		kind = self._kind()
		
		if not kind:
			return Any
		
		if hasattr(kind, '__annotation__'):  # A Field...
			return kind.__annotation__
		
		return kind
	
	def __fixup__(self, document):
		super().__fixup__(document)
		
		kind = self.kind
		
		if not kind:
			return
		
		if isinstance(kind, Field):
			kind.__name__ = self.__name__
			kind.__document__ = proxy(document)
			kind.__fixup__(document)  # Chain this down to embedded fields.
	
	def _kind(self, document=None):
		kind = self.kind
		
		if isinstance(kind, str):
			if kind.startswith('.'):
				# This allows the reference to be dynamic.
				kind = traverse(document or self.__document__, kind[1:])
			else:
				kind = load(kind, 'marrow.mongo.document')
		
		return kind


class _CastingKind(Field):
	def to_native(self, obj, name:str, value):  # pylint:disable=unused-argument
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		from marrow.mongo import Document
		from marrow.mongo.trait import Derived
		
		kind = self._kind(obj.__class__)
		
		if isinstance(value, Document):
			if __debug__ and kind and issubclass(kind, Document) and not isinstance(value, kind):
				raise ValueError("Not an instance of " + kind.__name__ + " or a sub-class: " + repr(value))
			
			return value
		
		if isinstance(kind, Field):
			return kind.transformer.native(value, (kind, obj))
		
		return (kind or Derived).from_mongo(value)
	
	def to_foreign(self, obj, name:str, value):  # pylint:disable=unused-argument
		"""Transform to a MongoDB-safe value."""
		
		from marrow.mongo import Document
		
		kind = self._kind(obj if isclass(obj) else obj.__class__)
		
		if isinstance(value, Document):
			if __debug__ and kind and issubclass(kind, Document) and not isinstance(value, kind):
				raise ValueError("Not an instance of " + kind.__name__ + " or a sub-class: " + repr(value))
			
			return value
		
		if isinstance(kind, Field):
			kind.validator.validate(value, FieldContext(kind, obj))
			return kind.transformer.foreign(value, FieldContext(kind, obj))
		
		if kind:
			value = kind(**value)
		
		return value
