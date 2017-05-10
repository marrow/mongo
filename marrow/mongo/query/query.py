# encoding: utf-8
# pylint:disable=too-many-arguments

"""A comparison proxy and Ops factory to help build nested inquiries.

For internal construction only.
"""

from __future__ import unicode_literals

from copy import copy
from collections import Iterable
from functools import reduce
from operator import __and__, __or__, __xor__

from ...schema.compat import py3, str, unicode
from .ops import Filter

if __debug__:
	_simple_safety_check = lambda s, o: (s.__allowed_operators__ and o not in s.__allowed_operators__) \
			or o in s.__disallowed_operators__
	_complex_safety_check = lambda s, o: (s.__allowed_operators__ and not s.__allowed_operators__.intersection(o)) \
			or s.__disallowed_operators__.intersection(o)


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
	"""
	
	__slots__ = ('_document', '_field', '_name', '_combining')
	
	def __init__(self, document, field, path=None, combining=None):
		"""Do not construct instances of Q yourself."""
		
		self._document = document
		self._field = field
		self._name = None if isinstance(field, list) else ((path or '') + unicode(field))
		self._combining = combining
	
	def __repr__(self):
		"""Programmers' representation for Q instances."""
		
		return "Q({self._document.__name__}, '{self}', {self._field!r})".format(self=self)
	
	def __getattr__(self, name):
		"""Access field attributes, or, for complex fields (Array, Embed, Reference, etc.) nested fields."""
		
		if self._combining:  # If we are combining fields, we can not dereference further.
			raise AttributeError()
		
		if not hasattr(self._field, '_kind'):
			return getattr(self._field, name)
		
		kind = self._field
		while getattr(kind, '_kind', None):
			kind = kind._kind(self._document)
		
		if hasattr(kind, '__fields__') and name in kind.__fields__:
				return self.__class__(self._document, kind.__fields__[name], self._name + '.')
		
		try:
			return getattr(kind, name)
		except AttributeError:
			pass
		
		try:  # Pass through to the field itself as a last resort.
			return getattr(self._field, name)
		except AttributeError:
			pass
		
		raise AttributeError()
	
	def __setattr__(self, name, value):
		"""Assign an otherwise unknown attribute on the targeted field instead."""
		
		if name.startswith('_'):
			return super(Q, self).__setattr__(name, value)
		
		if self._combining:
			raise AttributeError()
		
		setattr(self._field, name, value)
	
	def __getitem__(self, name):
		"""Allows for referencing specific array elements by index.
		
		For example, to check that the third tag is `baz`:
		
			Person.tag[3] == "baz"
		"""
		
		from marrow.mongo import Document, Field
		from marrow.mongo.field import Embed
		
		if self._combining:  # If we are combining fields, we can not dereference further.
			raise KeyError()
		
		if self._field.__foreign__ != 'array':  # Pass through if not an array type field.
			return self._field[name]
		
		if not isinstance(name, int) and not name.isdigit():
			raise KeyError("Must specify an index as either a number or string representation of a number: " + name)
		
		field = self._field._kind(self._document)
		
		if isinstance(field, Field):  # Bare simple values.
			field = copy(field)
			field.__name__ = self._name + '.' + unicode(name)
		
		else:  # Embedded documents.
			field = Embed(field, name=self._name + '.' + unicode(name))
		
		return self.__class__(self._document, field)
	
	def __unicode__(self):
		"""Return the name of the field, or combining operation."""
		
		return {__and__: '$and', __or__: '$or', __xor__: '$$xor'}[self._combining] if self._combining else self._name
	
	if py3:
		__str__ = __unicode__
	
	# Operation Building Blocks
	
	def _op(self, operation, other, *allowed):
		"""A basic operation operating on a single value."""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining,
					(q._op(operation, other, *allowed) for q in self._field))  # pylint:disable=protected-access
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {operation} & set(allowed)):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow {op} comparison.".format(self=self, op=operation))
		
		return Filter({self._name: {operation: self._field.transformer.foreign(other, (self._field, self._document))}})
	
	def _iop(self, operation, other, *allowed):
		"""An iterative operation operating on multiple values.
		
		Consumes iterators to construct a concrete list at time of execution.
		"""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining,
					(q._iop(operation, other, *allowed) for q in self._field))  # pylint:disable=protected-access
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {operation} & set(allowed)):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow {op} comparison.".format(
					self=self, op=operation))
		
		other = other if len(other) > 1 else other[0]
		values = [self._field.transformer.foreign(value, (self._field, self._document)) for value in other]
		
		return Filter({self._name: {operation: values}})
	
	# Matching Array Element
	
	@property
	def S(self):
		"""Allow for the projection (and update) of nested values contained within the single match of an array.
		
		Projection operator: https://docs.mongodb.com/manual/reference/operator/projection/positional/#proj._S_
		Array update operator: https://docs.mongodb.com/manual/reference/operator/update/positional/
		"""
		
		if self._combining:
			raise TypeError("Unable to dereference after combining fields.")
		
		instance = self.__class__(self._document, self._field)
		instance._name = self._name + '.' + '$'  # pylint:disable=protected-access
		return instance
	
	# Comparison Query Selectors
	# Documentation: https://docs.mongodb.org/manual/reference/operator/query/#comparison
	
	def __eq__(self, other):
		"""Matches values that are equal to the specified value.
		
			Document.field == "hOI!"
		
		Comparison operator: {$eq: value}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/eq/#op._S_eq
		"""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining, (q.__eq__(other) for q in self._field))
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _simple_safety_check(self._field, '$eq'):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow $eq comparison.".format(self=self))
		
		return Filter({self._name: self._field.transformer.foreign(other, (self._field, self._document))})
	
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
	
	def _combine(self, other, operation):  # pylint:disable=protected-access
		if not isinstance(other, Q):
			raise TypeError("Can not combine with non-Q.")
		
		if self._combining and self._combining is operation:  # pylint:disable=protected-access
			if other._combining and other._combining is operation:  # pylint:disable=protected-access
				return self.__class__(self._document,
						self._field + other._field, None, operation)  # pylint:disable=protected-access
			
			return self.__class__(self._document, self._field + [other], None, operation)
		
		if other._combining and other._combining is operation:  # pylint:disable=protected-access
			return self.__class__(self._document,
					[self] + other._field, None, operation)  # pylint:disable=protected-access
		
		return self.__class__(self._document, [self, other], None, operation)
	
	def __and__(self, other):
		"""Allow the comparison of multiple fields against a single value.
		
		Binary "and" comparison: both fields must match the final expression.
		
			(Document.first & Document.second) == 42
		"""
		
		return self._combine(other, __and__)
	
	def __or__(self, other):
		"""Allow the comparison of multiple fields against a single value.
		
		Binary "or" comparison: either field, or both, match the final expression.
		
			(Document.first | Document.second) == 27
		"""
		
		return self._combine(other, __or__)
	
	def __xor__(self, other):
		"""Allow the comparison of multiple fields against a single value.
		
		Binary "xor" comparison: the first field, or the second field, but not both must match the expression.
		
			(Document.first ^ Document.second) == 55
		"""
		
		return self._combine(other, __xor__)
	
	def __invert__(self):
		"""Return the fully qualified name of the current field reference, for use in custom dictionary construction.
		
		For example, when projecting:
		
			collection.find({}, {~Document.field: 1})
		
		Will be obsolete and possibly re-tasked if and when pymongo is patched to allow string-like (or stringify)
		keys. (That would allow simple `{Document.field: 1}` given we make ourselves hashable.)
		"""
		
		if self._combining:
			raise TypeError("Combined fields have ambiguous field name.")
		
		return self._name
	
	# Evaluation Query Operators
	
	def re(self, *parts):
		"""Matches string values against a regular expression compiled of individual parts.
		
			Document.field.re(r'^', variable_part, r'\.')
		
		Regex operator: {$regex: value}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/regex/
		"""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining, (q.re(*parts) for q in self._field))
		
		return Filter({self._name: {'$regex': ''.join(parts)}})
	
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
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining, (qp.match(q) for qp in self._field))
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {'$elemMatch', '#document'}):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow $elemMatch comparison.".format(self=self))
		
		if hasattr(q, 'as_query'):
			q = q.as_query
		
		return Filter({self._name: {'$elemMatch': q}})
	
	def range(self, gte, lt):
		"""Matches values that are between a minimum and maximum value, semi-inclusive.
		
			Document.field.range(4, 12)
		
		This will find documents with a field whose value is greater than or equal to 4, and less than 12.
		
		Comparison operator: {$gte: gte, $lt: lt}
		"""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			print("Combining", self._combining, self._field)
			return reduce(self._combining, (q.range(gte, lt) for q in self._field))
		
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
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining, (q.size(value) for q in self._field))
		
		# Optimize this away in production; diagnosic aide.
		if __debug__ and _complex_safety_check(self._field, {'$size', '#array'}):  # pragma: no cover
			raise NotImplementedError("{self!r} does not allow $size comparison.".format(self=self))
		
		return Filter({self._name: {'$size': int(value)}})
	
	# Element Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#element
	
	def __neg__(self):
		"""Matches documents that don't have the specified field.
		
			-Document.field
		
		Element operator: {$exists: false}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining, (q.__neg__() for q in self._field))
		
		return Filter({self._name: {'$exists': False}})
	
	def __pos__(self):
		"""Matches documents that have the specified field.
		
			+Document.field
		
		Element operator: {$exists: true}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/exists/#op._S_exists
		"""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining, (q.__pos__() for q in self._field))
		
		return Filter({self._name: {'$exists': True}})
	
	def of_type(self, *kinds):
		"""Selects documents if a field is of the correct type.
		
			Document.field.of_type()
			Document.field.of_type('string')
		
		Element operator: {$type: self.__foreign__}
		Documentation: https://docs.mongodb.org/manual/reference/operator/query/type/#op._S_type
		"""
		
		if self._combining:  # We are a field-compound query fragment, e.g. (Foo.bar & Foo.baz).
			return reduce(self._combining, (q.of_type(*kinds) for q in self._field))
		
		foreign = set(kinds) if kinds else self._field.__foreign__
		
		if not foreign:
			return Filter()
		
		if len(foreign) == 1:  # Simplify if the value is singular.
			foreign, = foreign  # Unpack.
		
		return Filter({self._name: {'$type': foreign}})
	
	# Geospatial Query Selectors
	# https://docs.mongodb.com/manual/reference/operator/query/#geospatial
	
	def near(self, center, sphere=False, min=None, max=None):
		"""Order results by their distance from the given point, optionally with range limits in meters.
		
		Geospatial operator: {$near: {...}}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/near/#op._S_near
		
			{
				$near: {
					$geometry: <center; Point or (long, lat)>,
					$minDistance: <min; distance in meters>,
					$maxDistance: <max; distance in meters>
				}
			}
		
		Geospatial operator: {$nearSphere: {...}}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/nearSphere/#op._S_nearSphere
		
			{
				$nearSphere: {
					$geometry: <center; Point or (long, lat)>,
					$minDistance: <min; distance in meters>,
					$maxDistance: <max; distance in meters>
				}
			}
		"""
		
		from marrow.mongo.geo import Point
		
		near = {'$geometry': Point(*center)}
		
		if min:
			near['$minDistance'] = float(min)
		
		if max:
			near['$maxDistance'] = float(max)
		
		return Filter({self._name: {'$nearSphere' if sphere else '$near': near}})
	
	def within(self, geometry=None, center=None, sphere=None, radius=None, box=None, polygon=None, crs=None):
		"""Select geometries within a bounding GeoJSON geometry.
		
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/geoWithin/#op._S_geoWithin
		
		Geospatial operator: {$geoWithin: {$geometry: ...}}}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/geometry/#op._S_geometry
		
			{
				$geoWithin: { $geometry: <Polygon or MultiPolygon> }
			}
		
		Geospatial operator: {$geoWithin: {$center: ...}}}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/center/#op._S_center
		
			{
				$geoWithin: { $center: [ <center; Point or (long, lat)>, <radius in coord system units> ] }
			}
		
		Geospatial operator: {$geoWithin: {$centerSphere: ...}}}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/centerSphere/#op._S_centerSphere
		
			{
				$geoWithin: { $centerSphere: [ <sphere; Point or (long, lat)>, <radius in radians> ] }
			}
		
		Geospatial operator: {$geoWithin: {$box: ...}}}
		Documentataion: https://docs.mongodb.com/manual/reference/operator/query/box/#op._S_box
		
			{
				$geoWithin: { $box: <box; 2-element GeoJSON object representing, or
						[(bottom left long, long), (upper right long, lat)]> }
			}
		
		Geospatial operator: {$geoWithin: {$polygon: ...}}}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/polygon/#op._S_polygon
		
			{
				$geoWithin: { $polygon: <polygon; Polygon or [(long, lat), ...]> }
			}
		"""
		
		if geometry:
			if crs:
				geometry = dict(geometry)
				geometry['crs'] = {'type': 'name', 'properties': {'name': crs}}
			
			inner = {'$geometry': geometry}
		
		elif center:
			inner = {'$center': [list(center), radius]}
		
		elif sphere:
			inner = {'$centerSphere': [list(sphere), radius]}
		
		elif box:
			inner = {'$box': list(list(i) for i in box)}
		
		elif polygon:
			inner = {'$polygon': list(list(i) for i in polygon)}
		
		else:
			raise TypeError("Requires at least one argument.")
		
		return Filter({self._name: {'$geoWithin': inner}})
	
	def intersects(self, geometry, crs=None):
		"""Select geometries that intersect with a GeoJSON geometry.
		
		Geospatial operator: {$geoIntersects: {...}}
		Documentation: https://docs.mongodb.com/manual/reference/operator/query/geoIntersects/#op._S_geoIntersects
		
			{
				$geoIntersects: { $geometry: <geometry; a GeoJSON object> }
			}
		"""
		
		if crs:
			geometry = dict(geometry)
			geometry['crs'] = {'type': 'name', 'properties': {'name': crs}}
		
		return Filter({self._name: {'$geoIntersects': {'$geometry': geometry}}})
