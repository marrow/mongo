# encoding: utf-8

"""MongoDB filter, projection, and update operation helpers.

These encapsulate the functionality of creating combinable mappings 
"""

from __future__ import unicode_literals

from ..core.util import py2, deepcopy, str, odict, chain, Mapping, MutableMapping, Container, Attribute, SENTINEL


if __debug__:
	_Queryable__simple_safety_check = lambda s, o: (s.__allowed_operators__ and o not in s.__allowed_operators__) or o in s.__disallowed_operators__
	_Queryable__complex_safety_check = lambda s, o: (s.__allowed_operators__ and not s.__allowed_operators__.intersection(o)) or s.__disallowed_operators__.intersection(o)


class Ops(Container):
	operations = Attribute(default=None)
	
	def __init__(self, *args, **kw):
		super(Ops, self).__init__(*args, **kw)
		
		if self.operations is None:
			self.operations = odict()
	
	def __repr__(self):
		return "Ops({})".format(repr(list(self.items())).replace("(u'", "('").replace("', u'", "', '"))
	
	@property
	def as_query(self):
		return self.operations
	
	# Binary Operator Protocols
	
	def __and__(self, other):
		operations = deepcopy(self.operations)
		
		if isinstance(other, Op):
			other = Ops(operations=other.as_query)
		
		for k, v in getattr(other, 'operations', []).items():
			if k not in operations:
				operations[k] = v
			else:
				if not isinstance(operations[k], Mapping):
					operations[k] = odict((('$eq', operations[k]), ))
				
				if not isinstance(v, Mapping):
					v = odict((('$eq', v), ))
				
				operations[k].update(v)
		
		return Ops(operations=operations)
	
	def __or__(self, other):
		operations = deepcopy(self.operations)
		
		if isinstance(other, Op):
			other = Ops(operations=other.as_query)
		
		if len(operations) == 1 and '$or' in operations:
			# Update existing $or.
			operations['$or'].append(other)
			return Ops(operations=operations)
		
		return Ops(operations={'$or': [operations, other]})
	
	# Mapping Protocol
	
	def __getitem__(self, name):
		return self.operations[name]
	
	def __setitem__(self, name, value):
		self.operations[name] = value
	
	def __delitem__(self, name):
		del self.operations[name]
	
	def __iter__(self):
		return iter(self.operations.keys())
	
	def __len__(self):
		return len(self.operations)
	
	if py2:
		def keys(self):
			return self.operations.iterkeys()
		
		def items(self):
			return self.operations.iteritems()
		
		def values(self):
			return self.operations.itervalues()
	
	else:
		def keys(self):
			return self.operations.keys()
		
		def items(self):
			return self.operations.items()
		
		def values(self):
			return self.operations.values()
	
	def __contains__(self, key):
		return key in self.operations
	
	def __eq__(self, other):
		return self.operations == other
	
	def __ne__(self, other):
		return self.operations != other
	
	def get(self, key, default=None):
		return self.operations.get(key, default)
	
	def clear(self):
		self.operations.clear()
	
	def pop(self, name, default=SENTINEL):
		if default is SENTINEL:
			return self.operations.pop(name)
		
		return self.operations.pop(name, default)
	
	def popitem(self):
		return self.operations.popitem()
	
	def update(self, *args, **kw):
		self.operations.update(*args, **kw)
	
	def setdefault(self, key, value=None):
		return self.operations.setdefault(key, value)


MutableMapping.register(Ops)  # Metaclass conflict if we subclass.


class Op(Container):
	field = Attribute(default=None)
	operation = Attribute(default=None)
	value = Attribute(default=SENTINEL)
	
	def __repr__(self):
		return "Op({})".format(repr(self.as_query))
	
	def clone(self, **kw):
		arguments = dict(field=self.field, operation=self.operation, value=self.value)
		arguments.update(kw)
		return self.__class__(**arguments)
	
	# Logical Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#logical
	
	def __or__(self, other):
		return Op(None, 'or', [self, other])
	
	def __and__(self, other):
		if getattr(other, 'field', None) is None or self.field is None:
			return Op(None, 'and', [self, other])
		
		return Ops(odict(chain(self.as_query.items(), other.as_query.items())))
	
	def __invert__(self): # not
		return Op(None, 'not', self)
	
	@property
	def as_query(self):
		value = getattr(self.value, 'as_query', self.value)
		if value is SENTINEL:
			value = None
		
		if isinstance(value, list):
			value = [getattr(i, 'as_query', i) for i in value]
		
		if not self.operation or self.operation == 'eq':
			if not self.field:
				return value
			
			if self.value is SENTINEL:
				return {str(self.field): {'$exists': 1}}
			
			return {str(self.field): value}
		
		if not self.field:
			return {'$' + str(self.operation): value}
		
		return {str(self.field): {'$' + str(self.operation): value}}


class Queryable(object):
	"""A convienent mix-in which adds the ability to generate Op instances during comparison.
	
	Assumes the following are populated:
	
	 * `self.transformer.foreign` -- a function to convert Python values into MongoDB ones.
	 * `self.__str__` -- calling `str()` (or `unicode()` in Python 2) across `self` should return a field name.
	 * `self.__allowed_operators__` -- a set of allowed operators
	 * `self.__disallowed_operators__` -- a blacklist set of operators
	"""
	
	__allowed_operators__ = set()
	__disallowed_operators__ = set()
	
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
			raise NotImplementedError("{self.__class__.__name__} does not allow $gt comparison.".format(self=self))
		
		return Op(self, 'gt', self.transformer.foreign(other, self))
	
	def __ge__(self, other):
		"""Matches values that are greater than or equal to a specified value.
		
			Document.field >= 21
		
		Comparison operator: {$gte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/gte/#op._S_gte
		"""
		if __debug__ and __complex_safety_check(self, {'$gte', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $gte comparison.".format(self=self))
		
		return Op(self, 'gte', self.transformer.foreign(other, self))
	
	def __lt__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field < 18
		
		Comparison operator: {$lt: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lt/#op._S_lt
		"""
		if __debug__ and __complex_safety_check(self, {'$lt', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $lt comparison.".format(self=self))
		
		return Op(self, 'lt', self.transformer.foreign(other, self))
	
	def __le__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field <= 27
		
		Comparison operator: {$lte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lte/#op._S_lte
		"""
		if __debug__ and __complex_safety_check(self, {'$lte', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $lte comparison.".format(self=self))
		
		return Op(self, 'lte', self.transformer.foreign(other, self))
	
	def __ne__(self, other):
		"""Matches all values that are not equal to a specified value.
		
			Document.field != 42
		
		Comparison operator: {$ne: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/ne/#op._S_ne
		"""
		if __debug__ and __complex_safety_check(self, {'$ne', '$eq'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $ne comparison.".format(self=self))
		
		return Op(self, 'ne', self.transformer.foreign(other, self))
	
	def any(self, *args):
		"""Matches any of the values specified in an array.
		
			Document.field.any([1, 2, 3, 5, 8, 13])
		
		Individual elements may be passed positionally instead, for convienence.
		
		Comparison operator: {$in: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/in/#op._S_in
		"""
		if __debug__ and __complex_safety_check(self, {'$in', '$eq'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $in comparison.".format(self=self))
		
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
		raise NotImplementedError()
	
	def __and__(self, other):
		raise NotImplementedError()
	
	def __invert__(self):
		raise NotImplementedError()
	
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
		
		return Op(self, 'all', [self.transformer.foreign(value, self) for i, value in enumerate(other)])
	
	def match(self, q):
		"""Selects documents if element in the array field matches all the specified conditions.
		
			Document.field.match(...)
		
		Array operator: {$elemMatch: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/elemMatch/#op._S_elemMatch
		"""
		if __debug__ and __complex_safety_check(self, {'$elemMatch', '#document'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $elemMatch comparison.".format(self=self))
		
		if hasattr(q, 'as_query'):
			q = q.as_query
		
		return Op(self, 'elemMatch', q)
	
	def range(self, gte, lt):
		"""Matches values that are between a minimum and maximum value, semi-inclusive.
		
			Document.field.range(4, 12)
		
		This will find documents with a field whose value is greater than or equal to 4, and less than 12.
		
		Comparison operator: {$gte: gte, $lt: lt}
		"""
		if __debug__ and __simple_safety_check(self, '#range'):  # Optimize this away in production; diagnosic aide.
			raise NotImplementedError("{self.__class__.__name__} does not allow range comparison.".format(self=self))
		
		return Ops((self >= gte).as_query) & Ops((self < lt).as_query)
	
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
		
		if args:
			return Op(self, 'type', args[0])
		
		return Op(self, 'type', self.__foreign__)
