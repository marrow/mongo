# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals

from ..query import Ops

DEFAULT_UPDATE = 'set'

UPDATE_PREFIX_MAP = {
	}

UPDATE_SUFFIX_MAP = {
	}


def U(Document, **update):
	"""Generate a MongoDB update document using the Django ORM style.
	
	Because this utility is likely going to be used frequently it has been given a single-character name.
	"""
	
	return Ops()
