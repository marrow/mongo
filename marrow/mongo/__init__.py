import sys

from .core import Document, Field, Index, __version__  # noqa
from .query import Q, Ops, Filter, Update
from .param import F, P, S, U
from .util import Registry, utcnow

document = sys.modules['marrow.mongo.document'] = Registry('marrow.mongo.document')
field = sys.modules['marrow.mongo.field'] = Registry('marrow.mongo.field')
trait = sys.modules['marrow.mongo.trait'] = Registry('marrow.mongo.trait')


__all__ = [
	'Document', 'Field', 'Index',  # Basic / core base classes.
	'Q', 'Ops', 'Filter', 'Update',  # Filter qurey document, update document, and inline query operations.
	'F', 'P', 'S', 'U',  # Parametric hepers.
	'utcnow',  # Utility helper, e.g. to use as a default.
	'document', 'field', 'trait',  # Entry point (plugin) registries / namespace modules.
]
