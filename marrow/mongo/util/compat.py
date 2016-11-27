# encoding: utf-8

"""Compatibility helpers to bridge the differences between Python 2 and Python 3.

Similar in purpose to [`six`](https://warehouse.python.org/project/six/). Not generally intended to be used by
third-party software, these are subject to change at any time. Only symbols exported via `__all__` are safe to use.
"""

# ## Imports

from __future__ import unicode_literals

import sys

# ## Module Exports

__all__ = ['py3', 'pypy', 'unicode', 'str']


# ## Version Detection

py3 = sys.version_info > (3, )
pypy = hasattr(sys, 'pypy_version_info')


# ## Builtins Compatibility

# Use of the `items` shortcut here must be very, very careful to only apply it to actual bare dictionaries.

if py3:
	unicode = str
	str = bytes
	items = dict.items
else:
	unicode = unicode
	str = str
	items = dict.iteritems
