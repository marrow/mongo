# encoding: utf-8

from copy import deepcopy
from itertools import chain

from marrow.schema import Container, Attribute
from ..query import Queryable
from .util import py2, Container, Attribute
#from marrow.schema.transform import BaseTransform

# from .util import py, str





def adjust_attribute_sequence(amount=10000, *fields):
	def adjust_inner(cls):
		for field in fields:
			getattr(cls, field).__sequence__ += amount  # Move this to the back of the bus.
		return cls
	return adjust_inner



@adjust_attribute_sequence(1000, 'transformer', 'translated', 'generated')
class Field(Attribute, Queryable):
	# Possible values include a literal operator, or one of:
	#  * #rel -- allow/prevent all relative comparison such as $gt, $gte, $lt, etc.
	#  * #array -- allow/prevent all array-related compraison such as $all, $size, etc.
	#  * #document -- allow/prevent all document-related comparison such as $elemMatch.
	__allowed_operators__ = set()
	__disallowed_operators__ = set()
	
	choices = Attribute(default=None)
	required = Attribute(default=False)  # Must have value assigned; None and an empty string are values.
	nullable = Attribute(default=False)  # If True, will store None.  If False, will store non-None default, or not store.
	
	transformer = Attribute(default=None)  # BaseTransform
	validator = Attribute(default=None)  # BaseValidator
	translated = Attribute(default=False)  # If truthy this field should be stored in the per-language subdocument.
	generated = Attribute(default=False)  # If truthy attempt to access and store resulting variable when instantiated.
	
	# Descriptor Protocol
	
	def __get__(self, obj, cls=None):
		"""Executed when retrieving a Field instance attribute."""
		
		# If this is class attribute (and not instance attribute) access, we return ourselves.
		if obj is None:
			return self
		
		# Attempt to retrieve the data from the warehouse.
		try:
			return super(Attribute, self).__get__(obj, cls)
		except AttributeError:
			pass
		
		# Attempt to utilize the defined default value.
		try:
			default = self.default
		except AttributeError:
			pass
		else:
			# Process and optionally store the default value.
			value = default() if isroutine(default) else default
			if self.assign:
				self.__set__(obj, value)
			return value
		
		# If we still don't have a value, this attribute doesn't yet exist.
		raise AttributeError('\'{0}\' object has no attribute \'{1}\''.format(
				obj.__class__.__name__,
				self.__name__
			))
	
	def __set__(self, obj, value):
		"""Executed when assigning a value to a DataAttribute instance attribute."""
		
		# Simply store the value in the warehouse.
		obj.__data__[self.__name__] = value
	
	def __delete__(self, obj):
		"""Executed via the ``del`` statement with a DataAttribute instance attribute as the argument."""
		
		# Delete the data completely from the warehouse.
		del obj.__data__[self.__name__]
	
	# Other Python Protocols
	
	def __str__(self):
		return self.__name__
	
	if py2:
		__unicode__ = __str__
		del __str__
