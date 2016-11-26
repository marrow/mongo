# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals


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
