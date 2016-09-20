# encoding: utf-8

"""

# Small test script for paste into ipython:

from pymongo import *
from marrow.mongo.core.document import Document
from marrow.mongo.field.base import Field
from marrow.mongo.query.djangoish import F

class Bar(Document):
	name = Field()
	value = Field()

class Foo(Document):
	name = Field()
	age = Field()
	
	attribute = Bar


q1 = F(Foo, age__gt=30)  # {'age': {'$gt': 30}}
q2 = (Foo.age > 30)  # {'age': {'$gt': 30}}
q3 = F(Foo, not__age__gt=30)  # {'age': {'$not': {'$gt': 30}}}
q4 = F(Foo, attribute__name__exists=False)  # {'attribute.name': {'$exists': 1}}

db = MongoClient().test
coll = db.foo
coll.drop()

coll.insert_one(Foo("Alice", 27))
coll.insert_one(Foo("Bob", 42))

print(list(coll.find(q1)))
print(list(coll.find(q2.as_query)))
print(list(coll.find(q3)))
print(list(coll.find(q4)))

"""


from __future__ import unicode_literals

import operator

from collections import deque
from pymongo import ASCENDING, DESCENDING

from ..util.compat import unicode
from . import Ops


def _deferred_method(name, _named=None, **kw):
	def _deferred_method_inner(self, other):
		if _named:
			if isinstance(_named, tuple):
				assert len(_named) == len(other), "Incorrect number of arguments."
				values = iter(other)
				for i in _named:
					kw[i] = next(values)
			else:
				kw[_named] = other
			return getattr(self, name)(**kw)
		return getattr(self, name)(other, **kw)
	return _deferred_method_inner


def _operator_choice(conversion, lookup, **kw):
	def _operator_choice_inner(self, other):
		return lookup[conversion(other)](self, **kw)
	return _operator_choice_inner


DEFAULT_FILTER = operator.eq
DEFAULT_UPDATE = 'set'

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
		# 'mod': ,
		
		# String-Specific
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


UPDATE_PREFIX_MAP = {
		
	}

UPDATE_SUFFIX_MAP = {
		
	}



def _process_arguments(Document, prefixes, suffixes, arguments):
	for name, value in arguments.items():
		# TODO: Rearrange this a bit to allow for automatic detection of method-based querying.
		# That'd need the Field instance to expose safe operations, but save much of the above hard-coding.
		nname, _, suffix = name.rpartition('__')
		if suffix in suffixes:
			name = nname
		else:
			suffix = None
		
		prefix, _, nname = name.partition('__')
		if prefix in prefixes:
			name = nname
		else:
			prefix = None
		
		# TODO: Eventually, nested dereferencing will track parent container name.
		# Currently it does not, so we need to.
		
		path = ''
		current = Document
		parts = deque(name.split('__'))
		
		while parts:
			if path:  # TODO: As per above note, this _should_ go after retrieval and str(current) instead.
				path += '.' + unicode(parts[0])
			else:
				path = unicode(parts[0])
			current = getattr(current, parts.popleft())
		
		yield prefixes.get(prefix, None), suffixes.get(suffix, None), path, current, value



def F(Document, __raw__=None, **filters):
	"""Generate a MongoDB filter document using the Django ORM style.
	
	Because this utility is likely going to be used frequently it has been given a single-character name.
	"""
	
	ops = Ops(__raw__)
	
	for prefix, suffix, path, field, value in _process_arguments(Document, FILTER_PREFIX_MAP, FILTER_OPERATION_MAP, filters):
		if suffix:
			op = suffix(field, value)
		else:
			op = DEFAULT_FILTER(field, value)
		
		if prefix:
			op.field = None
			op = prefix(op)
		
		op.field = path
		
		ops &= op
	
	return ops


def S(Document, *fields):
	"""Generate a MongoDB sort order list using the Django ORM style."""
	
	result = []
	
	for field in fields:
		if isinstance(field, tuple):  # Unpack existing tuple.
			field, direction = field
			result.append((field, direction))
			continue
		
		direction = ASCENDING
		field = field.replace('__', '.')
		
		if field[0] == '-':
			direction = DESCENDING
		
		if field[0] in ('+', '-'):
			field = field[1:]
		
		result.append((field, direction))
	
	return result


def P(Document, *fields, __always__=None):
	"""Generate a MongoDB projection dictionary using the Django ORM style."""
	
	__always__ = __always__ if __always__ else set()
	projected = set()
	omitted = set()
	
	for field in fields:
		if field[0] in ('-', '!'):
			omitted.add(field[1:])
		elif field[0] == '+':
			projected.add(field[1:])
		else:
			projected.add(field)
	
	if not projected:
		names = Document.__projection__.keys() if Document.__projection__ else Document.__fields__.keys()
		projected = {name for name in (names - omitted)}
	
	projected |= __always__
	
	return {name: True for name in projected}


def U(Document, **update):
	"""Generate a MongoDB update document using the Django ORM style.
	
	Because this utility is likely going to be used frequently it has been given a single-character name.
	"""
	
	return Ops()
