# encoding: utf-8

from __future__ import unicode_literals

from weakref import proxy

from ....package.loader import traverse, load
from ....schema import Attribute
from ....schema.transform import BaseTransform
from ....schema.validate import Validator
from ....schema.compat import str, unicode, py3
from ...query import Q
from ...util import adjust_attribute_sequence, SENTINEL


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
	__allowed_operators__ = set()
	__disallowed_operators__ = set()
	__document__ = None  # The Document subclass the field originates from.
	__foreign__ = {}
	__acl__ = []  # Overall document access control list.
	
	# Inherits from Attribute: (name is usually, but not always the first positional parameter)
	# name - The database-side name of the field, stored as __name__, defaulting to the attribute name assigned to.
	# default - No default is provided by default; access will raise AttributeError.
	
	choices = Attribute(default=None)  # The permitted set of values; may be static or a dynamic callback.
	required = Attribute(default=False)  # Must have value assigned; None and an empty string are values.
	nullable = Attribute(default=False)  # If True, will store None.  If False, will store non-None default, or not store.
	exclusive = Attribute(default=None)  # The set of other fields that must not be set for this field to be settable.
	
	# Data Lifespan Properties
	
	transformer = Attribute(default=FieldTransform())  # A Transformer class to use when loading/saving values.
	validator = Attribute(default=Validator())  # The Validator class to use when validating values.
	positional = Attribute(default=True)  # If True, will be accepted positionally.
	assign = Attribute(default=False)  # If truthy attempt to access and store resulting variable when instantiated.
	
	# Security Properties
	
	repr = Attribute(default=True)  # Should this field be included in the programmers' representation?
	project = Attribute(default=None)  # Predicate to indicate inclusion in the default projection.
	read = Attribute(default=True)  # Read predicate, either a boolean, callable, or web.security ACL predicate.
	write = Attribute(default=True)  # Write predicate, either a boolean, callable, or web.security ACL predicate.
	sort = Attribute(default=True)  # Sort predicate, either a boolean, callable, or web.security ACL predicate.
	
	def adapt(self, **kw):
		instance = self.__class__()
		instance.__data__ = self.__data__.copy()
		
		for k, v in kw.items():
			setattr(instance, k, v)
		
		return instance
	
	def __repr__(self):
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
			fields = ", ".join("{}={!r}".format(field, value) for field, value in fields)
			fields = ', ' + fields
		else:
			fields = ""
		
		name = getattr(self, '__name__', '<anonymous>')
		
		return "{self.__class__.__name__}('{name}'{fields})".format(
				self = self,
				name = name,
				fields = fields
			)
	
	# Security Predicate Handling
	
	def is_readable(self, context=None):
		if callable(self.read):
			if context:
				return self.read(context, self)
			else:
				return self.read(self)
		
		return bool(self.read)
	
	def is_writeable(self, context=None):
		if callable(self.write):
			if context:
				return self.write(context, self)
			else:
				return self.write(self)
		
		return bool(self.write)

	# Marrow Schema Interfaces
	
	def __init__(self, *args, **kw):
		super(Field, self).__init__(*args, **kw)
		
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
		
		result = super(Field, self).__get__(obj, cls)
		
		if result is None:  # Discussion: pass through to the transformer?
			return None
		
		return self.transformer.native(result, (self, obj))
	
	def __set__(self, obj, value):
		"""Executed when assigning a value to a DataAttribute instance attribute."""
		
		if self.exclusive:
			for other in self.exclusive:
				try:  # Handle this with kid gloves, just in case.
					ovalue = traverse(obj, other, None)
				except LookupError:  # pragma: no cover
					pass
				
				if ovalue is not None:
					raise AttributeError("Can not assign to " + self.__name__ + " if " + other + " has a value.")
		
		if value is not None:
			value = self.transformer.foreign(value, (self, obj))
		
		super(Field, self).__set__(obj, value)
	
	def __delete__(self, obj):
		"""Executed via the `del` statement with a DataAttribute instance attribute as the argument."""
		
		# Delete the data completely from the warehouse.
		del obj.__data__[self.__name__]
	
	# Other Python Protocols
	
	def __unicode__(self):
		return self.__name__
	
	if py3:
		__str__ = __unicode__
		del __unicode__




class _HasKind(Field):
	"""A mix-in to provide an easily definable singular or plural set of document types."""
	
	kind = Attribute(default=None)  # One or more foreign model references, a string, Document subclass, or set of.
	
	def __init__(self, *args, **kw):
		if args:
			kw['kind'], args = args[0], args[1:]
		
		super(_HasKind, self).__init__(*args, **kw)
	
	def __fixup__(self, document):
		super(_HasKind, self).__fixup__(document)
		
		kind = self.kind
		
		if not kind:
			return
		
		if isinstance(kind, Field):
			kind.__name__ = self.__name__
			kind.__document__ = proxy(document)
			kind.__fixup__(document)  # Chain this down to embedded fields.
	
	def _kind(self, document=None):
		kind = self.kind
		
		if isinstance(kind, (str, unicode)):
			if kind.startswith('.'):
				# This allows the reference to be dynamic.
				kind = traverse(document or self.__document__, kind[1:])
				
				if not isinstance(kind, (str, unicode)):
					return kind
			else:
				kind = load(kind, 'marrow.mongo.document')
		
		return kind


class _CastingKind(Field):
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
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
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		"""Transform to a MongoDB-safe value."""
		
		from marrow.mongo import Document
		
		kind = self._kind(obj.__class__)
		
		if isinstance(value, Document):
			if __debug__ and kind and issubclass(kind, Document) and not isinstance(value, kind):
				raise ValueError("Not an instance of " + kind.__name__ + " or a sub-class: " + repr(value))
			
			return value
		
		if isinstance(kind, Field):
			return kind.transformer.foreign(value, (kind, obj))
		
		if kind:
			value = kind(**value)
		
		return value
