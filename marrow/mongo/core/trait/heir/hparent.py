# encoding: utf-8

from re import escape
from pymongo.errors import BulkWriteError

from .base import Heirarchical
from .... import Document, Index, U
from ....field import Path


log = __import__('logging').getLogger(__name__)


class HParent(Heirarchical):
	"""Record sufficient information to form an orderless heirarchy of documents using parent association.
	
	This models the tree with a document per node and nodes containing a concrete list of child references.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-parent-references/
	"""
	
	parent = Reference('.', default=None, assign=True)
	
	_parent = Index('parent')
	
	def get_parent(self, *args, **kw):
		"""Retrieve the Document instance representing the immediate parent of this document."""
		
		if not self.parent:  # We can save time.
			return None
		
		return self.find_one(self.parent, *args, **kw)
	
	def find_siblings(self, *args, **kw):
		"""Prepare a MongoDB QuerySet searching the siblings of this document, excluding this document."""
		
		Doc, collection, query, options = self._prepare_find(*args, parent=self.parent, id__ne=self.id, **kw)
		return collection.find(query, **options)
	
	def find_children(self, *args, **kw):
		"""Prepare a MongoDB QuerySet searching for immediate children of this document."""
		
		if __debug__:
			log.debug("Finding children by parent association: " + str(self.id), extra={'parent': self})
		
		Doc, collection, query, options = self._prepare_find(*args, parent=self, **kw)
		return collection.find(query, **options)
	
	def detach(self):
		"""Detach this document from its tree, forming the root of a new tree containing this document and its children."""
		
		self = super(HParent, self).detach()
		
		if not self.parent:
			return self
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		result = collection.update_one(query, U(Doc, parent=None))
		
		self.parent = None  # Clean up to save needing to reload the record.
		
		return self
	
	def attach(self, child):
		"""Attach the given child document (with any descendants) to this document."""
		
		child = super(HParent, self).attach(child)
		
		Doc, collection, query, options = self._prepare_find(id=child.id)
		result = collection.update_one(query, U(Doc, parent=self.id))
		
		child.parent = self.id  # Clean up to save needing to reload the record.
		
		return child
