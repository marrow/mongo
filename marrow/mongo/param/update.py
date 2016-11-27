# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals

from operator import __neg__

from ...schema.compat import unicode
from ..query import Update
from .common import _bit, _current_date, _process_arguments

DEFAULT_UPDATE = 'set'  # If no prefix is found, this will be the default operation.

# These allow us to easily override the interpretation of any particular operation and introduce new ones.
# The keys represent prefixes, the values may be either a string (which will be prefixed with '$' automatically) or
# a tuple of the same plus a callable to filter the argument's value prior to integration. A third tuple value may
# be provided which will be called to apply the value to the operations being built.
UPDATE_ALIASES = {
		'add': 'inc',  # "Add"; a simple alias.
		'add_to_set': 'addToSet',  # Unserscore to camel case conversion.
		'bit_and': ('bit', _bit('and')),  # Parameterized bitwise update.
		'bit_or': ('bit', _bit('or')),  # Parameterized bitwise update.
		'bit_xor': ('bit', _bit('xor')),  # Parameterized bitwise update.
		'currentDate': ('currentDate', _current_date),  # Typecast to more expanded values.
		'current_date': ('currentDate', _current_date),  # Unserscore to camel case conversion.
		'dec': ('inc', __neg__),  # "Decrement"; invert the value and use $inc.
		'now': ('currentDate', _current_date),  # A shortcut for the longer form.
		'pull_all': 'pullAll',  # Unserscore to camel case conversion.
		'push_all': 'pushAll',  # Unserscore to camel case conversion.
		'rename': ('rename', unicode),  # Typecast to unicode.
		'set_on_insert': 'setOnInsert',  # Underscore to camel case conversion.
		'soi': 'setOnInsert',  # A shortcut for the longer form.
		'sub': ('inc', __neg__),  # "Subtract"; invert the value and use $inc.
	}

# Update with passthrough values.
UPDATE_ALIASES.update({i: i for i in {'bit', 'inc', 'max', 'min', 'mul', 'pull', 'pullALl', 'push', 'pushAll',
		'rename', 'set', 'setOnInsert', 'unset'}})

# These should not utilize field to_foreign typecasting.
UPDATE_PASSTHROUGH = {'rename', 'unset', 'pull', 'push', 'bit', 'currentDate'}


def U(Document, __raw__=None, **update):
	"""Generate a MongoDB update document through paramater interpolation.
	
	Arguments passed by name have their name interpreted as an optional operation prefix (defaulting to `set`, e.g.
	`push`), a double-underscore separated field reference (e.g. `foo`, or `foo__bar`, or `foo__S__bar`, or
	`foo__27__bar`)
	
	Because this utility is likely going to be used frequently it has been given a single-character name.
	"""
	
	ops = Update(__raw__)
	args = _process_arguments(Document, UPDATE_ALIASES, {}, update, UPDATE_PASSTHROUGH)
	
	for operation, _, field, value in args:
		if not operation:
			operation = DEFAULT_UPDATE
		
		if isinstance(operation, tuple):
			operation, cast = operation
			value = cast(value)
		
		ops &= Update({'$' + operation: {~field: value}})
	
	return ops
