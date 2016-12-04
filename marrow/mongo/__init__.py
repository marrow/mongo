# encoding: utf-8

from __future__ import unicode_literals

import sys

from .core import Document, Field, Index, __version__  # noqa
from .query import Q, Ops, Filter, Update
from .param import F, P, S, U
from .util import Registry

document = sys.modules['marrow.mongo.document'] = Registry('marrow.mongo.document')
field = sys.modules['marrow.mongo.field'] = Registry('marrow.mongo.field')

__all__ = [
	'Document',
	'F',
	'Field',
	'Filter',
	'Index',
	'Ops',
	'P',
	'Q',
	'S',
	'U',
	'Update',
	'document',
	'field',
]
