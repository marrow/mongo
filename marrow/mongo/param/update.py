# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals

from operator import __neg__

from ...schema.compat import odict
from ..query import Update

DEFAULT_UPDATE = 'set'  # If no prefix is found, this will be the default operation.

# These allow us to easily override the interpretation of any particular operation and introduce new ones.
# The keys represent prefixes, the values may be either a string (which will be prefixed with '$' automatically) or
# a tuple of the same plus a callable to filter the argument's value prior to integration. A third tuple value may
# be provided which will be called to apply the value to the operations being built.
UPDATE_ALIASES = {
		'add': 'inc',  # "Add"; a simple alias.
		'dec': ('inc', __neg__),  # "Decrement"; invert the value and use $inc.
		'sub': ('inc', __neg__),  # "Subtract"; invert the value and use $inc.
		'soi': 'setOnInsert',  # A shortcut for the longer form.
		'set_on_insert': 'setOnInsert',  # Underscore to camel case conversion.
		'current_date': 'currentDate',  # Unserscore to camel case conversion.
		'add_to_set': 'addToSet',  # Unserscore to camel case conversion.
		'pull_all': 'pullAll',  # Unserscore to camel case conversion.
		'push_all': 'pushAll',  # Unserscore to camel case conversion.
	}


def U(Document, __raw__=None, **update):
	"""Generate a MongoDB update document through paramater interpolation.
	
	Arguments passed by name have their name interpreted as an optional operation prefix (defaulting to `set`, e.g.
	`push`), a double-underscore separated field reference (e.g. `foo`, or `foo__bar`, or `foo__S__bar`, or
	`foo__27__bar`)
	
	Because this utility is likely going to be used frequently it has been given a single-character name.
	"""
	
	ops = odict(__raw__ or {})
	
	
	
	Document
	return Ops(update)
