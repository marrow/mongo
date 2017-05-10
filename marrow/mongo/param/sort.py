# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals

from pymongo import ASCENDING, DESCENDING

from ...package.loader import traverse


def S(Document, *fields):
	"""Generate a MongoDB sort order list using the Django ORM style."""
	
	result = []
	
	for field in fields:
		if isinstance(field, tuple):  # Unpack existing tuple.
			field, direction = field
			result.append((field, direction))
			continue
		
		direction = ASCENDING
		
		if not field.startswith('__'):
			field = field.replace('__', '.')
		
		if field[0] == '-':
			direction = DESCENDING
		
		if field[0] in ('+', '-'):
			field = field[1:]
		
		_field = traverse(Document, field, default=None)
		
		result.append(((~_field) if _field else field, direction))
	
	return result
