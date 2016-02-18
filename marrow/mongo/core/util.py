# encoding: utf-8

from __future__ import unicode_literals

"""Convienent utilities."""

# ## Imports

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
	
	bytes = str
	str = unicode
	py = 2
	reduce = reduce

except:  # Python 3
	from io import StringIO
	
	stringy = str
	bytes = bytes
	str = str
	py = 3

# There are some additional complications for the Pypy runtime.

try:
	from sys import pypy_version_info
	pypy = True
except ImportError:
	pypy = False
