# encoding: utf-8

from itertools import chain
from re import escape
from pathlib import PurePosixPath

from .base import Heirarchical
from .... import Index, U
from ....field import Path


log = __import__('logging').getLogger(__name__)


class HPath(Heirarchical):
	"""Record sufficient information to form an orderless heirarchy of documents using materialzied paths.
	
	This models the tree with a document per node and nodes containing a concrete list of child references.
	
	When mixing Heirarchical traits, use more efficient parent/child mix-ins later in your subclass definition.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-materialized-paths/
	"""
	
	__pk__ = 'path'  # Pivot short-form queries to query the path, not ID.
	
	path = Path(required=True, repr=False)  # The coalesced path to the document.
	
	_path = Index('path', unique=True)
	
	# Accessor Properties
	
	@property
	def parent(self):
		"""A query fragment to select the parent of this document.
		
		Used by `get_parent` as passed as the first positional argument to `find_one`.
		"""
		
		if __debug__:
			log.debug("Finding parent by materialized path: " + str(self.path), extra={'document': self})
		
		path = self.path
		
		if not path or path == path.parent or str(path.parent) == '.':
			return None  # No path, already root, or top level relative; no parent.
		
		return self.__class__.path == path.parent
	
	@property
	def ancestors(self):
		"""A query fragment selecting for the ancestors of this document, or a generator of parent path references.
		
		Warning: if you change the `__pk__` from `path`, the results will be unordered unless you explicitly sort on
		the `path` field yourself. With a `__pk__` of `path` this will return a generator of references for ordered
		selection by `_find_heirarchical`, otherwise it returns a query fragment filtering by possible paths.
		
		Used by `get_ancestors` with behaviour defined by `_find_heirarchical`.
		"""
		
		if __debug__:
			log.debug("Finding ancestors by materialized path: " + str(self.path), extra={'document': self})
		
		path = self.path
		
		if not path or path == path.parent or str(path.parent) == '.':
			return None  # No path, already root, or top level relative; no parents.
		
		absolute = self.path.is_absolute()
		parents = (parent for parent in self.path.parents if absolute or parent.name)
		
		if self.__pk__ != 'path':  # Warning: requires manual sort on `path` to preserve order!
			return self.__class__.path.any(parents)
		
		return parents  # We can just return the generator directly for consumption by `_find_heirarchical`.
	
	@property
	def siblings(self):
		"""A query fragment selecting for the siblings of this document.
		
		Used by `get_siblings` with behaviour defined by `_find_heirarchical`.
		"""
		
		if __debug__:
			log.debug("Finding siblings by materialized path: " + str(self.path), extra={'document': self})
		
		path = self.path
		
		if not path or path == path.parent or str(path.parent) == '.':
			return None  # No path, already root, or top level relative; no siblings.
		
		return self.__class__.path.re(r'^', escape(str(self.path.parent)), r'\/[^\/]+$')
	
	@property
	def children(self):
		"""A query fragment selecting for the immediate children of this document.
		
		Used by `get_children` with behaviour defined by `_find_heirarchical`.
		"""
		
		if __debug__:
			log.debug("Finding children by materialized path: " + str(self.path), extra={'document': self})
		
		if not self.path:
			return
		
		return self.__class__.path.re(r'^', escape(str(self.path)), r'\/[^\/]+$')
	
	@property
	def descendants(self):
		"""A query fragment selecting for the descendants of this document.
		
		Used by `get_descendants` with behaviour defined by `_find_heirarchical`.
		"""
		
		return self.__class__.path.re(r'^', escape(str(self.path)), r'\/')
	
	# Active Collection Methods
	
	@classmethod
	def get_nearest(cls, path, *args, **kw):
		"""Find and return the deepest Asset matching the given path."""
		
		path = PurePosixPath(path)
		absolute = path.is_absolute()
		parents = (parent for parent in path.parents if absolute or parent.name)
		kw.setdefault('sort', ('-path', ))
		
		return cls.find_one(*args, path__in=chain((path, ), parents), **kw)
	
	@classmethod
	def find_nearest(cls, path, *args, **kw):
		"""Find all nodes up to the deepest node matched by the given path.
		
		Conceptually the reverse of `get_nearest`.
		"""
		
		path = PurePosixPath(path)
		absolute = path.is_absolute()
		parents = (parent for parent in path.parents if absolute or parent.name)
		kw.setdefault('sort', ('-path', ))
		
		for doc in cls.find(*args, path__in=chain((path, ), parents), **kw):
			yield cls.from_mongo(doc)
	
	# Active Document Methods
	
	def detach(self):
		"""Detach this document from its tree, forming the root of a new tree containing this document and its children."""
		
		self = super(HPath, self).detach()
		
		if not self.path.root:
			return self  # Already detached.
		
		Doc = self.__class__
		collection = self.get_collection()
		length = len(str(self.path.parent)) + 1
		bulk = collection.initialize_unordered_bulk_op()
		
		bulk.find(Doc.id == self.id).update(U(Doc, path=self.slug))
		
		for descendant in self.find_descendants(projection=('id', 'path')):
			bulk.find(Doc.id == descendant['_id']).update(U(Doc, path=descendant['path'][length:]))
		
		result = bulk.execute()
		
		self.path = self.slug  # Clean up to save needing to reload the record.
		
		return self
	
	def _attach(self, child, ops, project=()):
		"""Attach the given child document (with any descendants) to this document.
		
		This is not an atomic operation unless the node has no descendents and no other heirarchical mix-ins.
		"""
		
		assert self.path, "Path required for child attachment."
		
		project = {'id', 'path'}.union(project)  # We need the path field, if not present.
		child, invalidated = super(HPath, self)._attach(child, ops, project)
		
		assert child.path, "Child must have addressable path, even if detached."
		assert child.path.name, "Child must not be literal root element."
		
		# Step one, update the child itself. Speed matters on these, so we avoid using parametric helpers where
		# reasonable to do so. Pro tip, re-mapping the back-end name of trait-provided fields is bad news bears.
		# Matters more in the tight loop seen in step two, below.
		
		chop = len(str(child.path)) - len(child.path.name)
		ops.find({'_id': child.id}).update_one({'$set': {'path': str(self.path / child.path.name)}})
		child.path = self.path / child.path.name
		
		# Step two, find descendants of the child and update them. There might not be any, but why waste a round trip?
		
		for offspring in self.get_collection().find(self.descendents, project={'path': 1}):
			path = str(self.path / offspring['path'][chop:])
			ops.find({'_id': offspring['_id']}).update_one({'$set': {'path': path}})
		
		return self
