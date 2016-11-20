# encoding: utf-8

"""A comparison proxy and Ops factory to help build nested inquiries.

For internal construction only.
"""

from __future__ import unicode_literals

import re
from copy import deepcopy
from collections import Mapping, MutableMapping
from pytz import utc
from bson.codec_options import CodecOptions
from marrow.schema.compat import odict

from ..util.compat import py3, unicode
from .ops import Ops


if __debug__:
	_simple_safety_check = lambda s, o: (s.__allowed_operators__ and o not in s.__allowed_operators__) or o in s.__disallowed_operators__
	_complex_safety_check = lambda s, o: (s.__allowed_operators__ and not s.__allowed_operators__.intersection(o)) or s.__disallowed_operators__.intersection(o)


class Q(object):
	"""A comparison proxy and Ops factory to help build nested inquiries. For internal construction only.
	
	Bound instances of Q are returned when accessing the fields of a Document subclass through class attribute access.
	
	For example, given a document like:
	
		class Person(Document):
			id = ObjectId('_id')
	
	When referencing `Person.id` you will get back:
	
		Q(Person, '_id', ObjectId('_id', assign=True))
	
	If you reference a nested field (embed or array of embeds) via something like `Foo.bar.baz` you would get back a Q
	like the following:
	
		Q(Foo, 'bar.baz', String('baz'))
	
	Due to the presence of several methods on this proxy, it becomes impossible to reference nested fields with any of
	the following names:
	
	* S
	* all
	* any
	* match
	* none
	* of_type
	* range
	* re
	* size
	
	A possible workaround is making Q callable (__call__) and pulling the final element off to determine method to call.
	"""
	
	def __init__(self, document, field, path=None):
		"""Do not construct instances of Q yourself.""" 
		self._document = document
		self._field = field
		self._name = (path or '') + unicode(field)
	
	def __repr__(self):
		return "Q({self._document.__name__}, '{self}', {self._field!r})".format(self=self)
	
	def __getattr__(self, name):
		if not hasattr(self._field, 'kinds'):
			return getattr(self._field, name)
		
		for kind in self._field.kinds:
			if hasattr(kind, '__fields__'):
				if name in kind.__fields__:
					return self.__class__(self._document, kind.__fields__[name], self._name + '.')
				
			try:
				return getattr(kind, name)
			except AttributeError:
				pass
		
		raise AttributeError()
	
	def __unicode__(self):
		return self._name
	
	if py3:
		__str__ = __unicode__
	
	# Operation Building Blocks
	
	def _op(self, operation, other, *allowed):
		"""A basic operation operating on a single value."""
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {operation} & set(allowed)):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow {op} comparison.".format(self=self, op=operation))
		
		return Ops({self._name: {operation: self._field.transformer.foreign(other, (self._field, self._document))}})
	
	def _iop(self, operation, other, *allowed):
		"""An iterative operation operating on multiple values.
		
		Consumes iterators to construct a concrete list at time of execution.
		"""
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {operation} & set(allowed)):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow {op} comparison.".format(
					self=self, op=operation))
		
		other = other if len(other) > 1 else other[0]
		values = [self._field.transformer.foreign(value, (self._field, self._document)) for value in other]
		
		return Ops({self._name: {operation: values}})
	
	# Matching Array Element
	
	@property
	def S(self):
		"""Allow for the projection (and update) of nested values contained within the single match of an array.
		
		Projection operator: https://docs.mongodb.com/manual/reference/operator/projection/positional/#proj._S_
		Array update operator: https://docs.mongodb.com/manual/reference/operator/update/positional/
		"""
		
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
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _simple_safety_check(self._field, '$eq'):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow $eq comparison.".format(self=self))
		
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
		
		return self._op('$gte', other, '#rel')
	
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
	
	# Multiple Field Participation
	
	def __and__(self, other):
		"""Allow the comparison of multiple fields against a single value. (Not implemented yet.)
		
		Binary "and" comparison: both fields must match the final expression.
		
			(Document.first & Document.second) == 42
		"""
		
		raise NotImplementedError()  # pragma: no cover
	
	def __or__(self, other):
		"""Allow the comparison of multiple fields against a single value. (Not implemented yet.)
		
		Binary "or" comparison: either field, or both, match the final expression.
		
			(Document.first | Document.second) == 27
		"""
		
		raise NotImplementedError()  # pragma: no cover
	
	def __xor__(self, other):
		"""Allow the comparison of multiple fields against a single value. (Not implemented yet.)
		
		Binary "xor" comparison: the first field, or the second field, but not both must match the expression.
		
			(Document.first ^ Document.second) == 55
		"""
		
		raise NotImplementedError()  # pragma: no cover
	
	def __invert__(self):
		"""Return the fully qualified name of the current field reference, for use in custom dictionary construction.
		
		For example, when projecting:
		
			collection.find({}, {~Document.field: 1})
		
		Will be obsolete and possibly re-tasked if and when pymongo is patched to allow string-like (or stringify)
		keys. (That would allow simple `{Document.field: 1}` given we make ourselves hashable.)
		"""
		
		return self._name
	
	# Evaluation Query Operators
	
	def re(self, *parts):
		"""Matches string values against a regular expression compiled of individual parts.
		
			Document.field.re(r'^', variable_part, r'\.')
		
		Regex operator: {$regex: value}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/regex/
		"""
		
		return Ops({self._name: {'$re': ''.join(parts)}})
	
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
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {'$elemMatch', '#document'}):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow $elemMatch comparison.".format(self=self))
		
		if hasattr(q, 'as_query'):
			q = q.as_query
		
		return Ops({self._name: {'$elemMatch': q}})
	
	def range(self, gte, lt):
		"""Matches values that are between a minimum and maximum value, semi-inclusive.
		
			Document.field.range(4, 12)
		
		This will find documents with a field whose value is greater than or equal to 4, and less than 12.
		
		Comparison operator: {$gte: gte, $lt: lt}
		"""
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _simple_safety_check(self._field, '$eq'):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow range comparison.".format(self=self))
		
		return (self >= gte) & (self < lt)
	
	def size(self, value):
		"""Selects documents if the array field is a specified size.
		
			Document.field.size(5)
		
		Array operator: {$size: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/size/#op._S_size
		"""
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {'$size', '#array'}):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow $size comparison.".format(self=self))
		
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
		
		if not foreign:
			return Ops()
		
		if len(foreign) == 1:  # Simplify if the value is singular.
			foreign, = foreign  # Unpack.
		
		return Ops({self._name: {'$type': foreign}})
