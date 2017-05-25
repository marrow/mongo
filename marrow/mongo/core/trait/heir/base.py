# encoding: utf-8

from contextlib import contextmanager

from .... import Document
from ....trait import Queryable


log = __import__('logging').getLogger(__name__)


class Heirarchical(Queryable):
	"""Record sufficient information to form a heirarchy of documents.
	
	Inteded for use via subclassing; not directly usable. This contains API prototypes and mixin methods similar in
	function to an abstract base class. For the most part subclasses should be able to "get away with" overriding
	appropriate accessor properties with real fields, or by providing alternate properties returning query fragments.
	
	A subclass should not, except under extreme circumstances, override the actual `find_` and `attach` methods.
	"""
	
	# Accessor Properties
	
	@property
	def parent(self):
		"""The primary key identity of, or query fragment to select the parent of this document.
		
		The result of a `ReferenceField('.')` is sufficient to satisfy this, if redefined as one.
		
		Used by `get_parent` as passed as the first positional argument to `find_one`.
		"""
		
		raise NotImplementedError()
	
	@property
	def ancestors(self):
		"""A query fragment or iterable of primary key identifiers to select the ancestors of this document.
		
		The result of an `Array(ReferenceField('.'))` is sufficient to satisfy this, if redefined as one.
		
		Used by `get_ancestors` with behaviour defined by `_find_heirarchical`.
		"""
		
		raise NotImplementedError()
	
	@property
	def siblings(self):
		"""A query fragment or iterable of primary key identifiers to select the siblings of this document.
		
		Used by `get_siblings` with behaviour defined by `_find_heirarchical`.
		"""
		
		raise NotImplementedError()
	
	@property
	def children(self):
		"""A query fragment or iterable of primary key identifiers to select the children of this document.
		
		The result of an `Array(ReferenceField('.'))` is sufficient to satisfy this, if redefined as one.
		
		Used by `get_children` with behaviour defined by `_find_heirarchical`.
		"""
		
		raise NotImplementedError()
	
	@property
	def descendants(self):
		"""A query fragment or iterable of primary key identifiers to select the descendants of this document.
		
		Used by `get_descendants` with behaviour defined by `_find_heirarchical`.
		"""
		
		raise NotImplementedError()
	
	# Internal Use Methods
	
	def _find_heirarchical(self, accessor, *args, **kw):
		try:
			query = getattr(self, accessor)
			
			if not isinstance(query, Filter):
				query = list(query)
		
		except TypeError:
			query = None
		
		if not query:
			return None
		
		if isinstance(query, list):
			iterator = self.find_in_sequence(self.__pk__, query, *args, **kw)
		
		else:
			iterator = self.find(query, *args, **kw)
		
		return (self.from_mongo(record) for record in iterator)
	
	@contextmanager
	def _heir_update(self):
		ops = self.get_collection().initialize_ordered_bulk_op()
		
		yield ops
		
		try:
			ops.execute()
		except:
			__import__('pprint').pprint(e.details)
			raise
	
	# Active Collection Methods
	
	def get_parent(self, *args, **kw):
		"""Retrieve the Document instance representing the immediate parent of this document."""
		
		parent = self.parent
		
		if parent is None:
			return None
		
		return self.find_one(parent, *args, **kw)
	
	def find_ancestors(self, *args, **kw):
		"""Retrieve the Document instances representing the ancestors of this document."""
		
		return self._find_heirarchical('ancestors', *args, **kw)
	
	def find_siblings(self, *args, **kw):
		"""Retrieve the Document instances representing siblings of this document, excluding this document."""
		
		return self._find_heirarchical('siblings', *args, id__ne=self.id, **kw)
	
	def find_children(self, *args, **kw):
		"""Find the immediate children of this document."""
		
		return self._find_heirarchical('children', *args, **kw)
	
	def find_descendants(self, *args, **kw):
		"""Prepare a MongoDB QuerySet searching for all descendants of this document."""
		
		return self._find_heirarchical('descendants', *args, **kw)
	
	# Active Document Methods
	
	def detach(self):
		"""Detach this document from its tree, forming the root of a new tree containing this document and its children."""
		
		return self
	
	def _attach(self, child, ops, project=None):
		if not isinstance(child, Document):
			child = Doc.find_one(child, project=project)
		
		return child
	
	def attach(self, child, **kw):
		"""Attach the given child document (with any descendants) to this document."""
		
		with self._heir_update(**kw) as ops:
			self._attach(child, ops)
		
		return self
	
	def attach_to(self, parent):
		"""Attach this document (with any descendants) to the given parent."""
		
		if not isinstance(parent, Document):
			parent = self.find_one(parent)
		
		return parent.attach(self)
	
	def attach_before(self, sibling):
		"""Attach this document (with any descendants) to the same parent as the target sibling, prior to that sibling."""
		
		if not isinstance(sibling, Document):
			sibling = self.find_one(sibling, project=('parent', ))
		
		self.attach_to(sibling.parent)
		
		return self.reload()
	
	def attach_after(self, sibling):
		"""Attach this document (with any descendants) to the same parent as the target sibling, after that sibling."""
		
		if not isinstance(sibling, Document):
			sibling = self.find_one(sibling, project=('parent', ))
		
		self.attach_to(sibling.parent)
		
		return self.reload()
