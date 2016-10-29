# encoding: utf-8

from weakref import proxy

from marrow.schema import Attribute
from marrow.schema.transform import BaseTransform
from marrow.schema.validate import Validator

from ..query import Queryable
from ..util import adjust_attribute_sequence
from ..util.compat import py3


class FieldTransform(BaseTransform):
	def foreign(self, value, context):
		field, document = context
		
		if hasattr(field, 'to_foreign'):
			return field.to_foreign(document, self.__name__, value)
		
		return value
	
	def native(self, value, context):
		field, document = context
		
		if hasattr(field, 'to_native'):
			return field.to_native(document, self.__name__, value)
		
		return value


@adjust_attribute_sequence(1000, 'transformer', 'validator', 'translated', 'assign', 'project', 'read', 'write')
class Field(Attribute, Queryable):
	# Possible values include a literal operator, or one of:
	#  * #rel -- allow/prevent all relative comparison such as $gt, $gte, $lt, etc.
	#  * #array -- allow/prevent all array-related compraison such as $all, $size, etc.
	#  * #document -- allow/prevent all document-related comparison such as $elemMatch.
	__allowed_operators__ = set()
	__disallowed_operators__ = set()
	__document__ = None  # If we're assigned to a Document, this gets populated with a weak reference proxy.
	
	# Inherits from Attribute: (name is usually, but not always the first positional parameter)
	# name - The database-side name of the field, stored as __name__, defaulting to the attribute name assigned to.
	# default - No default is provided by default; access will raise AttributeError.
	
	choices = Attribute(default=None)  # The permitted set of values; may be static or a dynamic callback.
	required = Attribute(default=False)  # Must have value assigned; None and an empty string are values.
	nullable = Attribute(default=False)  # If True, will store None.  If False, will store non-None default, or not store.
	exclusive = Attribute(default=None)  # The set of other fields that must not be set for this field to be settable.
	
	transformer = Attribute(default=FieldTransform())  # A Transformer class to use when loading/saving values.
	validator = Attribute(default=Validator())  # The Validator class to use when validating values.
	translated = Attribute(default=False)  # If truthy this field should be stored in the per-language subdocument.
	assign = Attribute(default=False)  # If truthy attempt to access and store resulting variable when instantiated.
	
	project = Attribute(default=None)  # Predicate to indicate inclusion in the default projection.
	read = Attribute(default=True)  # Read predicate, either  a boolean or a callable returning a boolean.
	write = Attribute(default=True)  # Write predicate, either a boolean or callable returning a boolean.
	
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
		
		# If this is class attribute (and not instance attribute) access, we return ourselves.
		if obj is None:
			return self
		
		# TODO: Translated field proxy?
		
		result = super(Field, self).__get__(obj, cls)
		
		if result is None:  # Discussion: pass through to the transformer?
			return None
		
		return self.transformer.native(result, (self, obj))
	
	def __set__(self, obj, value):
		"""Executed when assigning a value to a DataAttribute instance attribute."""
		
		if self.exclusive:
			for other in self.exclusive:
				try:
					if getattr(obj, other, None) is not None:
						raise AttributeError("Can not assign to " + self.__name__ + " if " + other + " has a value.")
				except AttributeError:
					pass
		
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
