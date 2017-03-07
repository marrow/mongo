# encoding: utf-8

from __future__ import unicode_literals

from ... import Document, Index, U
from ...field import ObjectId, String, Path, Array, Alias, Reference, Number
from ...trait import Queryable
from ....schema.compat import unicode


class Heirarchical(Queryable):
	"""Record sufficient information to form a heirarchy of documents."""
	
	def get_parent(self, *args, **kw):
		"""Retrieve the Document instance representing the immediate parent of this document."""
		
		raise NotImplementedError()
	
	def find_ancestors(self, *args, **kw):
		"""Prepare a MongoDB QuerySet searching the ancestors of this document.
		
		Some heirarchical structures are optimized for this type of querying, but not all.
		"""
		
		raise NotImplementedError()
	
	def find_siblings(self, *args, **kw):
		"""Prepare a MongoDB QuerySet searching the siblings of this document.
		
		Specifically excludes this document. Acts naively by default by querying for the parent,
		then children excluding the current document in no particular order.
		"""
		
		Doc, collection, query, options = self._prepare_find(*args, id__ne=self, **kw)
		project = options.pop('projection', None)
		
		parent = self.get_parent(**options)
		
		if project:
			options['projection'] = project
		
		return parent.find_children(query, **options)
	
	def find_children(self, *args, **kw):
		"""Prepare a MongoDB QuerySet searching for immediate children of this document."""
		
		raise NotImplementedError()
	
	def find_descendants(self, *args, **kw):
		"""Prepare a MongoDB QuerySet searching for all descendants of this document."""
		
		raise NotImplementedError()
	
	def detach(self):
		"""Detach this document from its tree, forming the root of a new tree containing this document and its children."""
		
		return self
	
	def attach(self, child):
		"""Attach the given child document (with any descendants) to this document."""
		
		return self
	
	def attach_to(self, parent):
		"""Attach this document (with any descendants) to the given parent."""
		
		if isinstance(parent, Document):
			return parent.attach(child)
		
		return self.find_one(parent).attach(child)
	
	def attach_before(self, sibling):
		"""Attach this document (with any descendants) to the same parent as the target sibling, prior to that sibling."""
		
		return self
	
	def attach_after(self, sibling):
		"""Attach this document (with any descendants) to the same parent as the target sibling, after that sibling."""
		
		return self


class HChildren(Heirarchical):
	"""Record sufficient information to form a heirarchy of documents using the _Child References_ pattern.
	
	The _Child References_ pattern stores each tree node in a document; in addition to the tree node, the
	document stores in an array the identifiers of the node’s children.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-child-references/
	"""
	
	children = Array(Reference(), default=lambda: [], assign=True)
	
	_children = Index('children')
	
	def get_parent(self, *args, **kw):
		return self.find_one(*args, children=self.id, **kw)
	
	def find_siblings(self, *args, **kw):
		parent = self.get_parent(projection=('children', ))
		return parent.find_children(*args, id__ne=self.id, **kw)
	
	def find_children(self, *args, **kw):
		return self.find_in_sequence('id', self.children, *args, **kw)
	
	def detach(self):
		Doc, collection, query, options = self._prepare_find(children=self.id)
		update = U(Doc, pull__children=self.id)
		result = collection.update_one(query, update, **options)
		
		return self
	
	def attach(self, child):
		if not isinstance(child, Document):
			child = self.find_one(child, projection=('id', ))
		
		child.detach()
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		update = U(Doc, push__children=child.id)
		result = collection.update_one(query, update, **options)
		
		return self
	
	def attach_to(self, parent):
		if not isinstance(parent, Document):
			parent = self.find_one(parent, projection=('id', ))
		
		self.detach()
		
		Doc, collection, query, options = self._prepare_find(id=parent.id)
		update = U(Doc, push__children=self.id)
		result = collection.update_one(query, update, **options)
		
		return self
	
	def attach_before(self, sibling):
		self.detach()
		
		if isinstance(sibling, Document):
			sibling = sibling.id
		
		parent = self.find_one(children=sibling, projection=('children', ))
		
		if not parent:
			raise ValueError("Can not attach aside a detached sibling: " + repr(sibling))
		
		index = parent.children.index(sibling)
		
		Doc, collection, query, options = self._prepare_find(id=parent.id)
		update = U(Doc, push_each__children=[self.id], push_position__children=index)
		result = collection.update_one(query, update, **options)
		
		return self
	
	def attach_after(self, sibling):
		self.detach()
		
		if isinstance(sibling, Document):
			sibling = sibling.id
		
		parent = self.find_one(children=sibling, projection=('children', ))
		
		if not parent:
			raise ValueError("Can not attach aside a detached sibling: " + repr(sibling))
		
		index = parent.children.index(sibling) + 1
		
		Doc, collection, query, options = self._prepare_find(id=parent.id)
		update = U(Doc, push_each__children=[self.id], push_position__children=index)
		result = collection.update_one(query, update, **options)
		
		return self


class HParent(Heirarchical):
	"""Record sufficient information to form a heirarchy of documents.
	
	This models the tree with a document per node and nodes containing a concrete list of child references.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-parent-references/
	"""
	
	parent = Reference(default=None, assign=True)
	
	_parent = Index('parent')
	
	def get_parent(self, *args, **kw):
		if not self.parent:  # We can save time.
			return None
		
		return self.find_one(self.parent, *args, **kw)
	
	def find_siblings(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, parent=self.parent, id__ne=self.id, **kw)
		return collection.find(query, **options)
	
	def find_children(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, parent=self, **kw)
		return collection.find(query, **options)
	
	def detach(self):
		if not self.parent:
			return self
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		result = collection.update_one(query, U(Doc, parent=None))
		
		self.parent = None  # Clean up to save needing to reload the record.
		
		return self
	
	def attach(self, child):
		if not isinstance(child, Document):
			child = self.find_one(child, projection=('id', ))
		
		child.detach()
		
		Doc, collection, query, options = self._prepare_find(id=child.id)
		result = collection.update_one(query, U(Doc, parent=self.id))
		
		child.parent = self.id  # Clean up to save needing to reload the record.
		
		return self
	
	def attach_to(self, parent):
		if isinstance(parent, Document):
			parent = parent.id
		
		self.detach()
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		result = collection.update_one(query, U(Doc, parent=parent))
		
		self.parent = parent  # Clean up to save needing to reload the record.
		
		return self


class HAncestors(HParent):
	"""Record sufficient information to form a heirarchy of documents.
	
	This models the tree with a document per node and nodes containing a concrete list of child references.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-ancestors-array/
	"""
	
	ancestors = Array(Reference(), default=lambda: [], assign=True)
	
	_ancestors = Index('ancestors')
	
	def find_ancestors(self, *args, **kw):
		return self.find_in_sequence('id', self.ancestors, *args, **kw)
	
	def find_descendants(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, ancestors=self.id, **kw)
		return collection.find(query, **options)
	
	def detach(self):
		if not self.parent:
			return self
		
		super(HAncestors, self).detach()
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		query |= Doc.ancestors == self.id
		update = U(Doc, pull_all__ancestors=self.ancestors)
		result = self.get_collection().update_many(query, update)
		
		self.ancestors = []  # Clean up to save needing to reload the record.
		
		return self
	
	def attach(self, child):
		if not isinstance(child, Document):
			child = self.find_one(child, projection=('id', 'ancestors'))
		
		super(HAncestors, self).attach(child)
		
		ancestors = self.ancestors + [self.id]
		
		Doc, collection, query, options = self._prepare_find(id=child.id)
		query |= Doc.ancestors == child.id
		update = U(Doc, push_each__ancestors=ancestors, push_position__ancestors=0)
		result = collection.update_many(query, update)
		
		if isinstance(child, Document):
			child.ancestors = ancestors  # Clean up to save needing to reload the record.
		
		return self
	
	def attach_to(self, parent):
		if not isinstance(parent, Document):
			parent = self.find_one(parent, projection=('id', 'ancestors'))
		
		parent.attach(self)
		
		return self


class HPath(Heirarchical):
	"""Record sufficient information to form a heirarchy of documents.
	
	This models the tree with a document per node and nodes containing a concrete list of child references.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-materialized-paths/
	"""
	
	slug = String(required=True)  # A short, lower-case identifier.
	path = Path(required=True)  # The coalesced path to the document.
	
	_path = Index('path', unique=True)
	
	def get_parent(self, *args, **kw):
		path = self.path.parent
		
		if unicode(path) in (path.root, '.'):
			return None  # No parent, already at root.
		
		Doc, collection, query, options = self._prepare_find(*args, path=path, **kw)
		result = coll.find_one(query, **options)
		return Doc.from_mongo(result, projected=options.get('projection', None))
	
	def find_ancestors(self, *args, **kw):
		parents = list(reversed(self.path.parents))
		
		if not parents:
			return None  # TODO: Empty QuerySet...
		
		return self.find_in_sequence('path', parents, *args, **kw)
	
	def find_siblings(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, **kw)
		
		query &= Doc.path.re(r'^', unicode(self.path.parent), r'\/[^\/]+$')
		
		return collection.find(query, **options)
	
	def find_children(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, **kw)
		
		query &= Doc.path.re(r'^', unicode(self.path), r'\/[^\/]+$')
		
		return collection.find(query, **options)
	
	def find_descendants(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, **kw)
		
		query &= Doc.path.re(r'^', unicode(self.path), r'\/')
		
		return collection.find(query, **options)
	
	def detach(self):
		Doc = self.__class__
		length = len(unicode(self.path.parent))
		collection = self.get_collection()
		
		if self.path.parent == '.':
			return False  # Already detached.
		
		for descendant in self.find_descendants(projection=('path', )):
			collection.update_one(
					Doc.path == descendant['path'],
					{'$set': {~Doc.path: descendant.path[length:]}},
				)
		
		result = collection.update_one(
				Doc.id == self.id,
				{'$set': {~Doc.path: self.slug}},
			)
		
		self.path = self.slug  # Clean up to save needing to reload the record.
		
		return bool(result.modified_count)
	
	def attach(self, child):
		pass
	
	def attach_to(self, parent):
		pass
	
	def attach_before(self, sibling):
		pass
	
	def attach_after(self, sibling):
		pass


class HNested(Heirarchical):
	"""Record sufficient information to form a heirarchy of documents.
	
	This models the tree using nested sets, a counter of the edges around the tree.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-nested-sets/
	"""
	
	left = Number(default=None)
	right = Number(default=None)
	
	_nested_set = Index('left', 'right')
	
	def get_parent(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(
				*args,
				left__lt = self.left,
				right__gt = self.right,
				sort = ('-left', ),
				**kw
			)
		
		result = collection.find_one(query, **options)
		return Doc.from_mongo(result, projected=options.get('projection', None))
	
	def find_ancestors(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(
				*args,
				left__lt = self.left,
				right__gt = self.right,
				**kw
			)
		
		options.setdefault('sort', [(~Doc.left, 1)])
		return collection.find(query, **options)
	
	def find_descendants(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(
				*args,
				left__gt = self.left,
				right__lt = self.right,
				**kw
			)
		
		options.setdefault('sort', [(~Doc.left, 1)])
		return collection.find(query, **options)
	
	def __get_rim_distance(self):
		Doc, collection, query, options = self._prepare_find(
				sort = ('-right', ),
				projection = ('-id', 'right'),
			)
		
		rim = collection.find_one(query, **options)
		
		if not rim:
			return None
		
		return Doc, collection, rim['right'] + 1 - self.left
	
	def detach(self):
		if not self.left or not self.find_ancestors().count():
			return False  # Not attached.
		
		Doc, collection, distance = self.__get_rim_distance()
		
		if distance is None:
			return False
		
		detaching = (Doc.left >= self.left) & (Doc.right <= self.right)
		left_updates = Doc.left > self.right
		right_updates = Doc.right > self.right
		
		# TODO: Bulk operation.
		collection.update_many(detaching, {'$add': {~Doc.left: distance, ~Doc.right: distance}})
		collection.update_many(left_updates, {'$add': {~Doc.left: -distance}})
		collection.update_many(right_updates, {'$add': {~Doc.right: -distance}})
		
		return True
	
	def attach(self, child):
		pass
	
	def attach_to(self, parent):
		pass
	
	def attach_before(self, sibling):
		pass
	
	def attach_after(self, sibling):
		pass


class Taxonomy(HAncestors, HPath):
	pass
