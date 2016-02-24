# encoding: utf-8

from __future__ import unicode_literals

"""Convienent utilities."""

# ## Imports

# These are confirmed as being required.  Notes made to usage in this library for each import.

# : marrow.mongo.core.query
from collections import Mapping, MutableMapping
from itertools import chain
from copy import deepcopy

# : marrow.mongo.core.query
from marrow.schema import Container, Attribute
from marrow.schema.compat import py2, odict, unicode as str

# : marrow.mongo.core.query
SENTINEL = object()  # Singleton value to detect unassigned values.


# : marrow.mongo.core.document
# : marrow.mongo.core.field
def adjust_attribute_sequence(amount=10000, *fields):
	"""Move marrow.schema fields around to control positional instantiation order."""
	
	def adjust_inner(cls):
		for field in fields:
			getattr(cls, field).__sequence__ += amount  # Move this to the back of the bus.
		return cls
	
	return adjust_inner


# Unconfirmed, legacy from cinje clone.

import sys

from codecs import iterencode
from inspect import isfunction, isclass
from operator import methodcaller
from collections import deque, namedtuple, Sized, Iterable
from pkg_resources import iter_entry_points
from xml.sax.saxutils import quoteattr

try:  # pragma: no cover
	from html.parser import HTMLParser
except ImportError:  # pragma: no cover
	from HTMLParser import HTMLParser


from marrow.schema.compat import native, str as bytes


# ## Python Cross-Compatibility
# 
# These allow us to detect relevant version differences for code generation, and overcome some of the minor
# differences in labels between Python 2 and Python 3 compatible runtimes.
# 
# The differences, in practice, are minor, and are easily overcome through a small block of version-dependant
# code.  Handily, even built-in labels are not sacrosanct; they can be easily assigned to and re-mapped.
# 

try:  # Python 2
	from types import StringTypes as stringy
	
	try:
		from cStringIO import StringIO
	except:  # pragma: no cover
		from StringIO import StringIO  # This never really happens.  Still, nice to be defensive.
	
	py = 2
	reduce = reduce

except:  # Python 3
	from io import StringIO
	
	stringy = str
	py = 3

# There are some additional complications for the Pypy runtime.

try:
	from sys import pypy_version_info
	pypy = True
except ImportError:
	pypy = False



