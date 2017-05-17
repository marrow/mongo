# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals

from ...package.loader import traverse
from ...schema.compat import unicode


def P(Document, *fields, **kw):
	"""Generate a MongoDB projection dictionary using the Django ORM style."""
	
	__always__ = kw.pop('__always__', set())
	projected = set()
	omitted = set()
	
	for field in fields:
		if field[0] in ('-', '!'):
			omitted.add(field[1:])
		elif field[0] == '+':
			projected.add(field[1:])
		else:
			projected.add(field)
	
	if not projected:  # We only have exclusions from the default projection.
		names = set(getattr(Document, '__projection__', Document.__fields__) or Document.__fields__)
		projected = {name for name in (names - omitted)}
	
	projected |= __always__
	
	if not projected:
		projected = {'_id'}
	
	return {unicode(traverse(Document, name, name)): True for name in projected}
