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
		
		if not isinstance(child, Document):
			child = self.find_one(child)
		
		child = child.detach()
		
		return child
	
	def attach_to(self, parent):
		"""Attach this document (with any descendants) to the given parent."""
		
		if not isinstance(parent, Document):
			parent = self.find_one(parent)
		
		return parent.attach(self)
	
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
		self = super(HChildren, self).detach()
		
		Doc, collection, query, options = self._prepare_find(children=self.id)
		update = U(Doc, pull__children=self.id)
		result = collection.update_one(query, update, **options)
		
		return self
	
	def attach(self, child):
		child = super(HChildren, self).attach(child)
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		update = U(Doc, push__children=child.id)
		result = collection.update_one(query, update, **options)
		
		return child
	
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
		self = super(HParent, self).detach()
		
		if not self.parent:
			return self
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		result = collection.update_one(query, U(Doc, parent=None))
		
		self.parent = None  # Clean up to save needing to reload the record.
		
		return self
	
	def attach(self, child):
		child = super(HParent, self).attach(child)
		
		Doc, collection, query, options = self._prepare_find(id=child.id)
		result = collection.update_one(query, U(Doc, parent=self.id))
		
		child.parent = self.id  # Clean up to save needing to reload the record.
		
		return child


class HAncestors(HParent):
	"""Record sufficient information to form a heirarchy of documents.
	
	This models the tree with a document per node and nodes containing a concrete list of child references.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-ancestors-array/
	"""
	
	ancestors = Array(Reference(), default=lambda: [], assign=True)
	
	_ancestors = Index('ancestors')
	
	def find_ancestors(self, *args, **kw):
		return self.find_in_sequence('id', reversed(self.ancestors), *args, **kw)
	
	def find_descendants(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, ancestors=self.id, **kw)
		return collection.find(query, **options)
	
	def detach(self):
		self = super(HAncestors, self).detach()
		
		if not self.ancestors:
			return self
		
		Doc, collection, query, options = self._prepare_find(id=self.id)
		query |= Doc.ancestors == self.id
		update = U(Doc, pull_all__ancestors=self.ancestors)
		result = collection.update_many(query, update)
		
		self.ancestors = []  # Clean up to save needing to reload the record.
		
		return self
	
	def attach(self, child):
		child = super(HAncestors, self).attach(child)
		ancestors = self.ancestors + [self.id]
		
		Doc, collection, query, options = self._prepare_find(id=child.id)
		query |= Doc.ancestors == child.id
		update = U(Doc, push_each__ancestors=ancestors, push_position__ancestors=0)
		result = collection.update_many(query, update)
		
		if isinstance(child, Document):
			child.ancestors = ancestors  # Clean up to save needing to reload the record.
		
		return child


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
		result = collection.find_one(query, **options)
		return Doc.from_mongo(result, projected=options.get('projection', None))
	
	def find_ancestors(self, *args, **kw):
		parents = list(unicode(i) for i in self.path.parents if unicode(i) not in (self.path.root, '.'))
		
		if not parents:
			return None  # TODO: Empty QuerySet...
		
		return self.find_in_sequence('path', parents, *args, **kw)
	
	def find_siblings(self, *args, **kw):
		Doc, collection, query, options = self._prepare_find(*args, **kw)
		
		query &= Doc.id != self.id
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
		self = super(HPath, self).detach()
		
		if not self.path.root:
			return self  # Already detached.
		
		Doc = self.__class__
		collection = self.get_collection()
		length = len(unicode(self.path.parent)) + 1
		bulk = collection.initialize_unordered_bulk_op()
		
		bulk.find(Doc.id == self.id).update(U(Doc, path=self.slug))
		
		for descendant in self.find_descendants(projection=('id', 'path')):
			bulk.find(Doc.id == descendant['_id']).update(U(Doc, path=descendant['path'][length:]))
		
		result = bulk.execute()
		
		self.path = self.slug  # Clean up to save needing to reload the record.
		
		return self
	
	def attach(self, child):
		child = super(HPath, self).attach(child)
		
		if not child.path:
			child.path = child.slug
		
		Doc = self.__class__
		collection = self.get_collection()
		bulk = collection.initialize_unordered_bulk_op()
		
		bulk.find(Doc.id == child.id).update(U(Doc, path=self.path / child.path))
		
		for descendant in child.find_descendants(projection=('id', 'path')):
			bulk.find(Doc.id == descendant['_id']).update(U(Doc, path=self.path / descendant['path']))
		
		result = bulk.execute()
		
		child.path = self.path / child.path
		
		return child


class HNested(Heirarchical):
	"""Record sufficient information to form a heirarchy of documents.
	
	This models the tree using nested sets, a counter of the edges around the tree.
	
	Ref: https://docs.mongodb.com/manual/tutorial/model-tree-structures-with-nested-sets/
	"""
	
	left = Number(default=None)
	right = Number(default=None)
	
	_nested_set = Index('left', 'right')
	
	def get_parent(self, *args, **kw):
		kw['sort'] = ('-left', )  # We require this sort order to fetch the correct record.
		
		return self.find_one(*args, left__lt=self.left, right__gt=self.right, **kw)
	
	def find_ancestors(self, *args, **kw):
		kw.setdefault('sort', ('left', ))  # This sort is optional, to preserve ancestor order.
		
		# As a special note: see how this avoids the use of the fancy ordered aggregate query?
		# A result of this will be that this tree structure is more backwards compatible.
		return self.find(*args, left__lt=self.left, right__gt=self.right, **kw)
	
	def find_descendants(self, *args, **kw):
		kw.setdefault('sort', ('left', ))
		
		return self.find(*args, left__gt=self.left, right__lt=self.right, **kw)
	
	def __get_rim_distance(self):
		Doc, collection, query, options = self._prepare_find(
				sort = ('-right', ),
				projection = ('-id', 'right'),
			)
		
		rim = collection.find_one(query, **options)
		
		if not rim:
			return Doc, collection, None
		
		return Doc, collection, rim['right'] + 1 - self.left
	
	def detach(self):
		self = super(HNested, self).detach()
		
		if not self.left or not self.find_ancestors().count():
			return self  # Not attached.
		
		Doc, collection, distance = self.__get_rim_distance()
		
		if distance is None:
			return self
		
		gap = 1 + self.right - self.left
		detaching = (Doc.left >= self.left) & (Doc.right <= self.right)
		left_updates = Doc.left > self.right
		right_updates = Doc.right > self.right
		
		bulk = collection.initialize_ordered_bulk_op()
		
		bulk.find(detaching).update(U(Doc, inc__left=distance, inc__right=distance))
		bulk.find(left_updates).update(U(Doc, dec__left=gap))
		bulk.find(right_updates).update(U(Doc, dec__right=gap))
		
		result = bulk.execute()
		
		return self.reload('left', 'right')
	
	def attach(self, child):
		if not self.left and not self.right:
			raise ValueError("Can only attach to a node already present in the graph.")
		
		child = super(HNested, self).attach(child)
		self.reload('left', 'right')  # In case things were detached.
		child.reload('left', 'right')
		
		Doc = self.__class__
		collection = self.get_collection()
		bulk = collection.initialize_ordered_bulk_op()
		
		# Step 1: Determine the size gap to create, and create it.
		
		gap = (1 + child.right - child.left) if child.left and child.right else 2
		
		bulk.find(Doc.left >= self.right).update(U(Doc, inc__left=gap))
		bulk.find(Doc.right >= self.right).update(U(Doc, inc__right=gap))
		
		self.right += gap  # Update our internal value.
		
		# Step 2: Move the child into position.
		
		if child.left and child.right:
			if child.left >= self.right: child.left += gap
			if child.right >= self.right: child.right += gap
			
			distance = (self.right - 2) - child.left
			attaching = (Doc.left >= child.left) & (Doc.right <= child.right)
			bulk.find(attaching).update(U(Doc, inc__left=distance, inc__right=distance))
			
			# Step 2b: Close any gap left behind in the structure.
			bulk.find(Doc.left > child.right).update(U(Doc, dec__left=gap))
			bulk.find(Doc.right > child.right).update(U(Doc, dec__right=gap))
		
		else:
			bulk.find(Doc.id == child.id).update(U(Doc, left=self.right - 2, right=self.right - 1))
		
		result = bulk.execute()
		
		self.reload('left', 'right')
		return child.reload('left', 'right')
	
	def attach_before(self, sibling):
		pass
	
	def attach_after(self, sibling):
		pass


class Taxonomy(HAncestors, HPath):
	pass
