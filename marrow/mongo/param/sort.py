"""Parameterized support akin to Django's ORM or MongoEngine."""

from pymongo import ASCENDING, DESCENDING

from ...package.loader import traverse
from ..core.types import check_argument_types, Sort, FieldOrder


def S(Document, *fields:FieldOrder) -> Sort:
	"""Generate a MongoDB sort order list using the Django ORM style."""
	
	assert check_argument_types()
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
