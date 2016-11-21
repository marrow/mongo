# encoding: utf-8

import sys

from .core import Document, Field, Index, __version__
from .util import Registry

document = sys.modules['marrow.mongo.document'] = Registry('marrow.mongo.document')
field = sys.modules['marrow.mongo.field'] = Registry('marrow.mongo.field')
