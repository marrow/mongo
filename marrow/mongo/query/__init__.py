# encoding: utf-8

"""MongoDB filter, projection, and update operation helpers.

These encapsulate the functionality of creating combinable mappings 
"""

from __future__ import unicode_literals

from copy import deepcopy
from collections import Mapping, MutableMapping
from pytz import utc
from bson.codec_options import CodecOptions
from marrow.schema.compat import odict

from ..util import SENTINEL
from ..util.compat import py3, unicode


if __debug__:
	_simple_safety_check = lambda s, o: (s.__allowed_operators__ and o not in s.__allowed_operators__) or o in s.__disallowed_operators__
	_complex_safety_check = lambda s, o: (s.__allowed_operators__ and not s.__allowed_operators__.intersection(o)) or s.__disallowed_operators__.intersection(o)


class Ops(object):
	__slots__ = ('operations', 'collection', 'document')
	
	def __init__(self, operations=None, collection=None, document=None):
		self.operations = operations or odict()
		self.collection = collection
		self.document = document
	
	def bind(self, collection):
		self.collection = collection.with_options(CodecOptions(document_class=odict, tz_aware=True, tzinfo=utc))
		return self
	
	def __repr__(self, extra=None):
		return "{}({}{}{}{})".format(
				self.__class__.__name__,
				self.operations,
				", collection={}".format() if self.collection else "",
				", document={}".format() if self.document else "",
				extra or ""
			)
	
	@property
	def as_query(self):
		return self.operations
	
	# Binary Operator Protocols
	
	def __and__(self, other):
		operations = deepcopy(self.operations)
		other = self.__class__(
				operations = other.as_query if hasattr(other, 'as_query') else other,
				collection = self.collection,
				document = self.document
			)
		
		for k, v in getattr(other, 'operations', {}).items():
			if k not in operations:
				operations[k] = v
			else:
				if not isinstance(operations[k], Mapping):
					operations[k] = odict((('$eq', operations[k]), ))
				
				if not isinstance(v, Mapping):
					v = odict((('$eq', v), ))
				
				operations[k].update(v)
		
		return self.__class__(operations=operations, collection=self.collection, document=self.document)
	
	def __or__(self, other):
		operations = deepcopy(self.operations)
		
		other = other.as_query if hasattr(other, 'as_query') else other
		
		if len(operations) == 1 and '$or' in operations:
			# Update existing $or.
			operations['$or'].append(other)
			return self.__class__(
					operations = operations,
					collection = self.collection,
					document = self.document
				)
		
		return self.__class__(
				operations = {'$or': [operations, other]},
				collection = self.collection,
				document = self.document
			)
	
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
	
	if py3:
		def keys(self):
			return self.operations.keys()
		
		def items(self):
			return self.operations.items()
		
		def values(self):
			return self.operations.values()
	
	else:
		def keys(self):
			return self.operations.iterkeys()
		
		def items(self):
			return self.operations.iteritems()
		
		def values(self):
			return self.operations.itervalues()
	
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
		if __debug__ and _simple_safety_check(self, '$eq'):  # Optimize this away in production; diagnosic aide.
			raise NotImplementedError("{self.__class__.__name__} does not allow $eq comparison.".format(self=self))
		
		return Ops({unicode(self): self.transformer.foreign(other, self)})
	
	def __gt__(self, other):
		"""Matches values that are greater than a specified value.
		
			Document.field > 65
		
		Comparison operator: {$gt: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/gt/#op._S_gt
		"""
		if __debug__ and _complex_safety_check(self, {'$gt', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $gt comparison.".format(self=self))
		
		return Ops({unicode(self): {'$gt': self.transformer.foreign(other, self)}})
	
	def __ge__(self, other):
		"""Matches values that are greater than or equal to a specified value.
		
			Document.field >= 21
		
		Comparison operator: {$gte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/gte/#op._S_gte
		"""
		if __debug__ and _complex_safety_check(self, {'$gte', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $gte comparison.".format(self=self))
		
		return Ops({unicode(self): {'$gte': self.transformer.foreign(other, self)}})
	
	def __lt__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field < 18
		
		Comparison operator: {$lt: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lt/#op._S_lt
		"""
		if __debug__ and _complex_safety_check(self, {'$lt', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $lt comparison.".format(self=self))
		
		return Ops({unicode(self): {'$lt': self.transformer.foreign(other, self)}})
	
	def __le__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field <= 27
		
		Comparison operator: {$lte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lte/#op._S_lte
		"""
		if __debug__ and _complex_safety_check(self, {'$lte', '#rel'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $lte comparison.".format(self=self))
		
		return Ops({unicode(self): {'$lte': self.transformer.foreign(other, self)}})
	
	def __ne__(self, other):
		"""Matches all values that are not equal to a specified value.
		
			Document.field != 42
		
		Comparison operator: {$ne: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/ne/#op._S_ne
		"""
		if __debug__ and _complex_safety_check(self, {'$ne', '$eq'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $ne comparison.".format(self=self))
		
		return Ops({unicode(self): {'$ne': self.transformer.foreign(other, self)}})
	
	def any(self, *args):
		"""Matches any of the values specified in an array.
		
			Document.field.any([1, 2, 3, 5, 8, 13])
		
		Individual elements may be passed positionally instead, for convienence.
		
		Comparison operator: {$in: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/in/#op._S_in
		"""
		if __debug__ and _complex_safety_check(self, {'$in', '$eq'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $in comparison.".format(self=self))
		
		other = args if len(args) > 1 else args[0]
		
		return Ops({unicode(self): {'$in': (self.transformer.foreign(value, self) for value in other)}})
	
	def none(self, other):
		"""Matches none of the values specified in an array.
		
			Document.field.none([2, 3, 5, 7, 11, 13, 17 19, 23, 29])
		
		Comparison operator: {$nin: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/nin/#op._S_nin
		"""
		return Ops({unicode(self): {'$nin': (self.transformer.foreign(value, self) for value in other)}})
	
	# Logical Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#logical
	
	def __or__(self, other):  # TODO: Decide what to do when the developer does this.
		raise NotImplementedError()
	
	def __and__(self, other):  # TODO: Decide what to do when the developer does this.
		raise NotImplementedError()
	
	def __invert__(self):  # TODO: Decide what to do when the developer does this.
		raise NotImplementedError()
	
	# Array Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#array
	
	def all(self, other):
		"""Matches arrays that contain all elements specified in the query.
		
			Document.field.all(['hocuspocus', 'xyzzy', 'abracadabra'])
		
		Array operator: {$all: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/all/#op._S_all
		"""
		if __debug__ and _complex_safety_check(self, {'$all', '#array'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $all comparison.".format(self=self))
		
		return Ops({unicode(self): {'$all': (self.transformer.foreign(value, self) for value in other)}})
	
	def match(self, q):
		"""Selects documents if element in the array field matches all the specified conditions.
		
			Document.field.match(...)
		
		Array operator: {$elemMatch: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/elemMatch/#op._S_elemMatch
		"""
		if __debug__ and _complex_safety_check(self, {'$elemMatch', '#document'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $elemMatch comparison.".format(self=self))
		
		if hasattr(q, 'as_query'):
			q = q.as_query
		
		return Ops({unicode(self): {'$elemMatch': q}})
	
	def range(self, gte, lt):
		"""Matches values that are between a minimum and maximum value, semi-inclusive.
		
			Document.field.range(4, 12)
		
		This will find documents with a field whose value is greater than or equal to 4, and less than 12.
		
		Comparison operator: {$gte: gte, $lt: lt}
		"""
		if __debug__ and _simple_safety_check(self, '#range'):  # Optimize this away in production; diagnosic aide.
			raise NotImplementedError("{self.__class__.__name__} does not allow range comparison.".format(self=self))
		
		return (self >= gte) & (self < lt)
	
	def size(self, value):
		"""Selects documents if the array field is a specified size.
		
			Document.field.size(5)
		
		Array operator: {$size: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/size/#op._S_size
		"""
		if __debug__ and _complex_safety_check(self, {'$size', '#array'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $size comparison.".format(self=self))
		
		return Ops({unicode(self): {'$size': int(value)}})
	
	# Element Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#element
	
	def __neg__(self):
		"""Matches documents that don't have the specified field.
		
			-Document.field
		
		Element operator: {$exists: false}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		return Ops({unicode(self): {'$exists': False}})
	
	def __pos__(self):
		"""Matches documents that have the specified field.
		
			+Document.field
		
		Element operator: {$exists: true}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		return Ops({unicode(self): {'$exists': True}})
	
	def of_type(self, *kinds):
		"""Selects documents if a field is of the correct type.
		
			Document.field.of_type()
			Document.field.of_type('string')
		
		Element operator: {$type: self.__foreign__}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/type/#op._S_type
		"""
		
		foreign = set(kinds) if kinds else self.__foreign__
		
		return Ops({unicode(self): {'$type': foreign}})

