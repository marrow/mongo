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
	
	def copy(self):
		return self.operations.copy()
	
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


class Q(object):
	"""A comparison proxy and Ops factory to help build nested inquiries."""
	
	def __init__(self, document, field, path=None):
		self._document = document
		self._field = field
		self._name = (path or '') + unicode(field)
	
	def __getattr__(self, name):
		if not hasattr(self._field, 'kinds'):
			raise AttributeError()
		
		for kind in self._field.kinds:
			if name in kind.__fields__:
				return self.__class__(self._document, kind.__fields__[name], self._name + '.')
		
		raise AttributeError()
	
	def __hash__(self):
		return hash(self._name)
	
	def __unicode__(self):
		return self._name
	
	if py3:
		__str__ = __unicode__
	
	# Operation Building Blocks
	
	def _op(self, operation, other, *allowed):
		if __debug__ and _complex_safety_check(self._field, {operation} & set(allowed)):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow {op} comparison.".format(
					self=self, op=operation))
		
		return Ops({self._name: {operation: self.transformer.foreign(other, (self._field, self._document))}})
	
	def _iop(self, operation, other, *allowed):
		if __debug__ and _complex_safety_check(self._field, {operation} & set(allowed)):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow {op} comparison.".format(
					self=self, op=operation))
		
		other = other if len(other) > 1 else other[0]
		
		return Ops({self._name: {operation: [self.transformer.foreign(value, (self._field, self._document)) for value in other]}})
	
	# Matching Array Element
	
	@property
	def S(self):
		instance = self.__class__(self._document, self._field)
		instance._name = self._name + '.' + '$'
		return instance
	
	# Comparison Query Selectors
	# Documentation: https://docs.mongodb.org/manual/reference/operator/query/#comparison
	
	def __eq__(self, other):
		"""Matches values that are equal to the specified value.
		
			Document.field == "hOI!"
		
		Comparison operator: {$eq: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/eq/#op._S_eq
		"""
		
		if __debug__ and _simple_safety_check(self._field, '$eq'):  # Optimize this away in production; diagnosic aide.
			raise NotImplementedError("{self.__class__.__name__} does not allow $eq comparison.".format(self=self))
		
		return Ops({self._name: self._field.transformer.foreign(other, (self._field, self._document))})
	
	def __gt__(self, other):
		"""Matches values that are greater than a specified value.
		
			Document.field > 65
		
		Comparison operator: {$gt: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/gt/#op._S_gt
		"""
		
		return self._op('$gt', other, '#rel')
	
	def __ge__(self, other):
		"""Matches values that are greater than or equal to a specified value.
		
			Document.field >= 21
		
		Comparison operator: {$gte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/gte/#op._S_gte
		"""
		
		return self._op('$ge', other, '#rel')
	
	def __lt__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field < 18
		
		Comparison operator: {$lt: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lt/#op._S_lt
		"""
		
		return self._op('$lt', other, '#rel')
	
	def __le__(self, other):
		"""Matches values that are less than or equal to a specified value.
		
			Document.field <= 27
		
		Comparison operator: {$lte: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/lte/#op._S_lte
		"""
		
		return self._op('$lte', other, '#rel')
	
	def __ne__(self, other):
		"""Matches all values that are not equal to a specified value.
		
			Document.field != 42
		
		Comparison operator: {$ne: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/ne/#op._S_ne
		"""
		
		return self._op('$ne', other, '$eq')
	
	def any(self, *args):
		"""Matches any of the values specified in an array.
		
			Document.field.any([1, 2, 3, 5, 8, 13])
		
		Individual elements may be passed positionally instead, for convienence.
		
		Comparison operator: {$in: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/in/#op._S_in
		"""
		
		return self._iop('$in', args, '$eq')
	
	def none(self, *args):
		"""Matches none of the values specified in an array.
		
			Document.field.none([2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
		
		Comparison operator: {$nin: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/nin/#op._S_nin
		"""
		
		return self._iop('$nin', args, '$eq')
	
	# Logical Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#logical
	
	def __or__(self, other):
		"""Allow the comparison of multiple fields against a single value.
		
		Binary "or" comparison: either field, or both, match the final expression.
		
			(Document.first & Document.second) == 27
		"""
		
		raise NotImplementedError()
	
	def __and__(self, other):  # TODO: Decide what to do when the developer does this.
		"""Allow the comparison of multiple fields against a single value.
		
		Binary "and" comparison: both fields must match the final expression.
		
			(Document.first | Document.second) == 42
		"""
		
		raise NotImplementedError()
	
	def __xor__(self, other):
		"""Allow the comparison of multiple fields against a single value.
		
		Binary "xor" comparison: the first field, or the second field, but not both must match the expression.
		
			(Document.first ^ Document.second) == 55
		"""
		
		raise NotImplementedError()
	
	def __invert__(self):
		"""Return the fully qualified name of the current field reference, for use in custom dictionary construction.
		
		For example, when projecting:
		
			collection.find({}, {~Document.field: 1})
		"""
		return self._name
	
	# Evaluation Query Operators
	def re(self, *parts):
		"""Matches string values against a regular expression compiled of individual parts.
		
			Document.field.re(r'^', variable_part, r'\.')
		
		Regex operator: {$regex: value}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/regex/
		"""
		
		raise NotImplementedError()
	
	# Array Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#array
	
	def all(self, *args):
		"""Matches arrays that contain all elements specified in the query.
		
			Document.field.all(['hocuspocus', 'xyzzy', 'abracadabra'])
		
		Array operator: {$all: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/all/#op._S_all
		"""
		
		return self._iop('$all', args, '#array')
	
	def match(self, q):
		"""Selects documents if element in the array field matches all the specified conditions.
		
			Document.field.match(...)
		
		Array operator: {$elemMatch: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/elemMatch/#op._S_elemMatch
		"""
		if __debug__ and _complex_safety_check(self._field, {'$elemMatch', '#document'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $elemMatch comparison.".format(self=self))
		
		if hasattr(q, 'as_query'):
			q = q.as_query
		
		return Ops({self._name: {'$elemMatch': q}})
	
	def range(self, gte, lt):
		"""Matches values that are between a minimum and maximum value, semi-inclusive.
		
			Document.field.range(4, 12)
		
		This will find documents with a field whose value is greater than or equal to 4, and less than 12.
		
		Comparison operator: {$gte: gte, $lt: lt}
		"""
		if __debug__ and _simple_safety_check(self._field, '#range'):  # Optimize this away in production; diagnosic aide.
			raise NotImplementedError("{self.__class__.__name__} does not allow range comparison.".format(self=self))
		
		return (self >= gte) & (self < lt)
	
	def size(self, value):
		"""Selects documents if the array field is a specified size.
		
			Document.field.size(5)
		
		Array operator: {$size: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/size/#op._S_size
		"""
		if __debug__ and _complex_safety_check(self._field, {'$size', '#array'}):  # Optimize this away in production.
			raise NotImplementedError("{self.__class__.__name__} does not allow $size comparison.".format(self=self))
		
		return Ops({self._name: {'$size': int(value)}})
	
	# Element Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#element
	
	def __neg__(self):
		"""Matches documents that don't have the specified field.
		
			-Document.field
		
		Element operator: {$exists: false}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		
		return Ops({self._name: {'$exists': False}})
	
	def __pos__(self):
		"""Matches documents that have the specified field.
		
			+Document.field
		
		Element operator: {$exists: true}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		
		return Ops({self._name: {'$exists': True}})
	
	def of_type(self, *kinds):
		"""Selects documents if a field is of the correct type.
		
			Document.field.of_type()
			Document.field.of_type('string')
		
		Element operator: {$type: self.__foreign__}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/type/#op._S_type
		"""
		
		foreign = set(kinds) if kinds else self._field.__foreign__
		
		return Ops({self._name: {'$type': foreign}})
