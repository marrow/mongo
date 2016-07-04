# encoding: utf-8

from .release import version as __version__

from .field import Field
from .index import Index
from .document import Document

from .registry import Registry


__all__ = ['__version__', 'Field', 'Index', 'Document']

_field_registry = Registry('marrow.mongo:field')
_document_registry = Registry('marrow.mongo:document')

