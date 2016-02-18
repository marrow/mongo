# encoding: utf-8

from copy import deepcopy
from itertools import chain

from marrow.schema import Container, Attribute
#from marrow.schema.transform import BaseTransform

# from .util import py, str


if __debug__:
	__simple_safety_check = lambda s, o: (s.__allowed_operators__ and o not in s.__allowed_operators__) or o in self.__disallowed_operators__
	__complex_safety_check = lambda s, o: (s.__allowed_operators__ and not s.__allowed_operators__.intersection(o)) or self.__disallowed_operators__.intersection(o)


def adjust_attribute_sequence(amount=10000, *fields):
	def adjust_inner(cls):
		for field in fields:
			getattr(cls, field).__sequence__ += amount  # Move this to the back of the bus.
		return cls
	return adjust_inner



@adjust_attribute_sequence(1000, 'transformer', 'translated', 'generated')
class Field(Attribute):
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
	validator = Attribute(default=None)
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
	
	# Comparison Query Selectors
	# Documentation: https://docs.mongodb.org/manual/reference/operator/query/#comparison
	
	def __eq__(self, other):
		"""Matches values that are equal to the specified value.
		
			Document.field == "hOI!"
		
		Comparison operator: {$eq: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/eq/#op._S_eq
		"""
		if __debug__ and __simple_safety_check(self, '$eq'):  # Optimize this away in production; diagnosic aide.
			raise NotImplementedError("{self.__class__.__name__} does not allow $eq comparison.".format(self=self))
			
		return Op(self, 'eq', self.transformer.foreign(other, self))
	
	def __gt__(self, other):
		"""Matches values that are greater than a specified value.
		
			Document.field > 65
		
		Comparison operator: {$gt: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/gt/#op._S_gt
		"""
		if __debug__ and __complex_safety_check(self, {'$gt', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $eq comparison.".format(self=self))
		
		return Op(self, 'gt', self.transformer.foreign(other, self))
	
	def __ge__(self, other):
		"""Matches values that are greater than or equal to a specified value.
		
			Document.field >= 21
		
		Comparison operator: {$gte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/gte/#op._S_gte
		"""
		return Op(self, 'gte', self.transformer.foreign(other, self))
	
	def __lt__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field < 18
		
		Comparison operator: {$lt: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lt/#op._S_lt
		"""
		return Op(self, 'lt', self.transformer.foreign(other, self))
	
	def __le__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field <= 27
		
		Comparison operator: {$lte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lte/#op._S_lte
		"""
		return Op(self, 'lte', self.transformer.foreign(other, self))
	
	def __ne__(self, other):
		"""Matches all values that are not equal to a specified value.
		
			Document.field != 42
		
		Comparison operator: {$ne: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/ne/#op._S_ne
		"""
		return Op(self, 'ne', self.transformer.foreign(other, self))
	
	def any(self, *args):
		"""Matches any of the values specified in an array.
		
			Document.field.any([1, 2, 3, 5, 8, 13])
		
		Individual elements may be passed positionally instead, for convienence.
		
		Comparison operator: {$in: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/in/#op._S_in
		"""
		other = args if len(args) > 1 else args[0]
		
		return Op(self, 'in', [self.transformer.foreign(value, self) for i, value in enumerate(other)])
	
	def none(self, other):
		"""Matches none of the values specified in an array.
		
			Document.field.none([2, 3, 5, 7, 11, 13, 17 19, 23, 29])
		
		Comparison operator: {$nin: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/nin/#op._S_nin
		"""
		return Op(self, 'nin', [self.transformer.foreign(value, self) for i, value in enumerate(other)])
	
	# Logical Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#logical
	
	def __or__(self, other):
		return Ops()
	
	def __and__(self, other):
		return Ops()
	
	def __invert__(self): # not
		return Op()
	
	# Array Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#array
	
	def all(self, other):
		"""Matches arrays that contain all elements specified in the query.
		
			Document.field.all(['hocuspocus', 'xyzzy', 'abracadabra'])
		
		Array operator: {$all: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/all/#op._S_all
		"""
		if __debug__ and __complex_safety_check(self, {'$all', '#array'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $all comparison.".format(self=self))
		
		return Op(self, 'in', [self.transformer.foreign(value, self) for i, value in enumerate(other)])
	
	def match(self, q):
		"""Selects documents if element in the array field matches all the specified conditions.
		
			Document.field.match(...)
		
		Array operator: {$elemMatch: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/elemMatch/#op._S_elemMatch
		"""
		if __debug__ and __complex_safety_check(self, {'$elemMatch', '#document'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $eq comparison.".format(self=self))
		
		if hasattr(q, 'as_query'):
			q = q.as_query
		
		return Op(self, 'elemMatch', q)
	
	def size(self, value):
		"""Selects documents if the array field is a specified size.
		
			Document.field.size(5)
		
		Array operator: {$size: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/size/#op._S_size
		"""
		if __debug__ and __complex_safety_check(self, {'$size', '#array'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $size comparison.".format(self=self))
		
		return Op(self, 'size', int(value))
	
	# Element Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#element
	
	def __neg__(self):
		"""Matches documents that don't have the specified field.
		
			-Document.field
		
		Element operator: {$exists: false}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		return Op(self, 'exists', 0)
	
	def __pos__(self):
		"""Matches documents that have the specified field.
		
			+Document.field
		
		Element operator: {$exists: true}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		return Op(self, 'exists', 1)
	
	def of_type(self, *args):
		"""Selects documents if a field is of the correct type.
		
			Document.field.of_type()
			Document.field.of_type('string')
		
		Element operator: {$type: self.__foreign__}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/type/#op._S_type
		"""
		
		candidates = set()
		
		if not args:
			if isinstance(self.__foreign__, (list, tuple)):
				candidates.update(self.__foreign__)
			else:
				candidates.add(self.__foreign__)
		else:
			candidates.update(getattr(i, '__foreign__', i) for i in args)
		
		# TODO
		
		if not isinstance(args[0], (list, tuple)):
			return Op(self, 'type', args[0])
