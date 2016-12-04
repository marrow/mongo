# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals

import operator

from ..query import Filter
from .common import _deferred_method, _operator_choice, _process_arguments

DEFAULT_FILTER = operator.eq

FILTER_PREFIX_MAP = {
		'not': operator.invert,
	}

FILTER_OPERATION_MAP = {
		'lt': operator.lt,
		'le': operator.le,
		'lte': operator.le,  # Alias of 'le'
		'eq': operator.eq,
		'ne': operator.ne,
		'ge': operator.ge,
		'gte': operator.ge,  # Alias of 'ge'
		'gt': operator.gt,
		
		'any': _deferred_method('any'),
		'in': _deferred_method('any'),  # Alias of 'any'
		'all': _deferred_method('all'),
		'none': _deferred_method('none'),
		'nin': _deferred_method('none'),  # Alias of 'none'
		
		'size': _deferred_method('size'),
		'match': _deferred_method('match'),
		'range': _deferred_method('range', ('gte', 'lt')),
		'exists': _operator_choice(bool, {True: operator.pos, False: operator.neg}),
		
		# String-Specific
		're': _deferred_method('re'),
		'exact': _deferred_method('exact'),
		'iexact': _deferred_method('exact', insensitive=True),
		'contains': _deferred_method('contains'),
		'icontains': _deferred_method('contains', insensitive=True),
		'startswith': _deferred_method('startswith'),
		'istartswith': _deferred_method('startswith', insensitive=True),
		'endswith': _deferred_method('endswith'),
		'iendswith': _deferred_method('endswith', insensitive=True),
		
		# Geographic
		'near': _deferred_method('near'),
		'within': _deferred_method('within'),
		'geo_within': _deferred_method('within'),  # Alias
		'within_box': _deferred_method('within', 'box'),
		'geo_within_box': _deferred_method('within', 'box'),  # Alias
		'within_polygon': _deferred_method('within', 'polygon'),
		'geo_within_polygon': _deferred_method('within', 'polygon'),  # Alias
		'within_center': _deferred_method('within', ('center', 'radius')),
		'geo_within_center': _deferred_method('within', ('center', 'radius')),  # Alias
		'within_sphere': _deferred_method('within', ('sphere', 'radius')),
		'geo_within_sphere': _deferred_method('within', ('sphere', 'radius')),  # Alias
		'intersects': _deferred_method('intersects'),
		'geo_intersects': _deferred_method('intersects'),  # Alias
	}


def F(Document, __raw__=None, **filters):
	"""Generate a MongoDB filter document through parameter interpolation.
	
	Arguments passed by name have their name interpreted as an optional prefix (currently only `not`), a double-
	underscore
	
	Because this utility is likely going to be used frequently it has been given a single-character name.
	"""
	
	ops = Filter(__raw__)
	args = _process_arguments(Document, FILTER_PREFIX_MAP, FILTER_OPERATION_MAP, filters)
	
	for prefix, suffix, field, value in args:
		if suffix:
			op = suffix(field, value)
		else:
			op = DEFAULT_FILTER(field, value)
		
		if prefix:
			op = prefix(op)
		
		ops &= op
	
	return ops
