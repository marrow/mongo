# encoding: utf-8

from bson import ObjectId
from pymongo.errors import BulkWriteError
from contextlib import contextmanager

from marrow.package.loader import traverse
from marrow.package.canonical import name as name_
from marrow.schema import Attribute

from .query import Ops

if __debug__:  # In development, we track how long certain operations take and log this at the DEBUG level.
	from time import time


log = __import__('logging').getLogger(__name__)


class Taxonomy(Ops):
	"""A factory for queries relating to, and routines for manipulating taxonomic structure.
	
	This maintains an acyclic directed graph (tree) structure for you using an API inspired by the jQuery DOM
	traversal and manipulation APIs. Some attempt is made to group these methods into logical sections, but there's a
	surprising amount of code in here. Coalesced paths are provided for convienent lookup, but not used for general
	querying beyond the `nearest` lookup. The `parent` reference and `ancestors` list are used for general queries.
	
	The following are fields this Ops specializaion maintains for you:
	
	* `ancestors` - An array of sub-documents storing cached data about all ancestors.
	* `parent` - An ObjectID reference to the immediate parent of the document.
	* `path` - The coalesced path to the document, UNIX-style. No leading slash? It's detached.
	* `index` - The position of the document within its parent.
	
	Documents missing the `ancestors` and `parent` fields, and containing a `path` not beginning ith `/` are in a
	"detached" state. They may have descendants attached to them. The true root node of the graph should have a `name`
	of `/` in order for path coalescing to work correctly.
	"""
	
	CACHE = ('_id', 'name')  # You can override this in your own specialization to record more about ancestors.
	
	collection = Attribute()
	
	# Internal Support
	# The follwoing are principally meant for internal use.
	
	@property
	@contextmanager  # _ordered
	def _ordered(self):
		"""Prepare an ordered bulk operation as a context manager to centralize logging and error handling."""
		
		ops = self.collection.initialize_ordered_bulk_op()
		
		if __debug__:
			log.debug("Preparing ordered bulk operation.")
			start = time()
		
		yield ops
		
		if not ops._BulkOperationBuilder__bulk.ops:  # FRAGILE INTERNAL MAGIC
			if __debug__:
				log.warn("Ordered bulk operation aborted.")
			return
		
		if __debug__:
			duration = (time() - start) * 1000
			log.debug("Ordered bulk operation preparation complete; executing.", extra=dict(duration=duration))
			start = time()
		
		try:
			result = ops.execute()
		except BulkWriteError:
			raise  # TODO: Better exception logging.
		
		if __debug__:
			duration = (time() - start) * 1000
			log.debug("Ordered bulk operation complete.", extra=dict(result, duration=duration))
	
	@property
	@contextmanager  # _unordered
	def _unordered(self):
		"""Prepare an unordered bulk operation as a context manager to centralize logging and error handling"""
		ops = self.collection.initialize_unordered_bulk_op()
		
		if __debug__:
			log.debug("Preparing unordered bulk operation.")
			start = time()
		
		yield ops
		
		if not ops._BulkOperationBuilder__bulk.ops:
			if __debug__:
				log.warn("Unordered bulk operation aborted.")
			return
		
		if __debug__:
			duration = (time() - start) * 1000
			log.debug("Unordered bulk operation preparation complete.", extra=dict(duration=duration))
			start = time()
		
		try:
			result = ops.execute()
		except BulkWriteError:
			raise  # TODO: Better exception logging.
		
		if __debug__:
			duration = (time() - start) * 1000
			log.debug("Unordered bulk operation complete.", extra=dict(result, duration=duration))
	
	def _project(self, fields):
		"""Construct a simplified MongoDB projection based on the provided iterable of field names."""
		
		if fields:
			projection = {'_id': 0}
			projection.update((field, 1) for field in fields)
			return projection
	
	def _target(self, target):
		"""Resolve a target reference.
		
		This will transform a Taxonomy query into one selecting the same elements by ID, wraps bare ObjectId in a
		Taxonomy selecting for it, or, given an unsaved document, will save that document then provide a Taxonomy
		selecting for it.
		"""
		
		if isinstance(target, Taxonomy):  # Documents to attach as selected by Taxonomy.
			return target
		
		elif isinstance(target, ObjectId):  # Document to attach by ID.
			return self.id(target)
		
		elif target.get('_id', None):  # Docuent with existing ID.
			return self.id(target['_id'])
		
		return self.id(self.collection.insert_one(target).inserted_id)
	
	def _move_target(self, target):
		"""Resolve a target reference and ensure it is detached, ready for attachment.
		
		Identical to `_target` in semantics, but returns both a Taxonomy instance and count of affected items.
		"""
		
		if isinstance(target, Taxonomy):  # Documents to attach as selected by Taxonomy.
			target = target.detach()
			return target, target.count()
		
		elif isinstance(target, ObjectId):  # Document to attach by ID.
			return self.id(target).detach(), 1
		
		elif target.get('_id', None):  # Docuent with existing ID.
			return self.id(target['_id']).detach(), 1
		
		return self.id(self.collection.insert_one(target).inserted_id), 1
	
	# Query Terminals
	# These prevent further chaining by immediately executing the query to return a result.
	
	def first(self, *fields, **kw):
		"""Retrieve the first record matched by our current query."""
		
		if 'sort' in kw:
			kw['sort'] = [(i.lstrip('-'), -1 if i[0] == '-' else 1) for i in kw['sort']]
		
		return self.collection.find_one(self.as_query, self._project(fields), **kw)
	
	def all(self, *fields, **kw):
		"""Retrieve a cursor selecting the records matched by our current query."""
		
		if 'sort' in kw:
			kw['sort'] = [(i.lstrip('-'), -1 if i[0] == '-' else 1) for i in kw['sort']]
		
		return self.collection.find(self.as_query, self._project(fields), **kw)
	
	def one(self, *fields, **kw):
		"""Retrive the record matched by our current query, requiring no more than one result."""
		
		if self.count(**kw) > 1:
			raise ValueError("Requested one record, matched multiple.")
		
		return self.first(*fields, **kw)
	
	def count(self, **kw):
		"""Retrieve the count of records matched by our current query."""
		return self.all(**kw).count()
	
	def update(self, update, **kw):
		"""Update the records matched by our current query."""
		return self.collection.update(self.as_query, update, **kw)
	
	def delete(self, **kw):
		"""Delete the records matched by our current query."""
		return self.collection.delete(self.as_query, **kw)
	
	def scalar(self, *fields, **kw):
		"""Retrieve the given field or fields from records matched by our current query.
		
		If only a single field is given, an iterable of just that field is returned. If multiple fields are selected,
		you'll get back an iterable of tuples of those fields in the same order.
		
		Utilizes `marrow.package.loader:traverse`, allowing for deep lookup.
		"""
		
		if len(fields) == 1:  # Special case for single field scalars.
			field = fields[0]
			
			for result in self.all(*fields, **kw):
				yield result.get(field)
			
			return
		
		for result in self.all(*fields, **kw):  # Slightly simpler multi-field scalars.
			yield tuple(traverse(result, field, default=None) for field in fields)
	
	def nearest(self, path, projection=None):
		"""Immediately look up the asset nearest the given path, utilizing any query built so far.
		
		Allows for optional projection. This must immediately issue the query due to the fairly complex query.
		"""
		
		if __debug__:  # Give useful error messages in development.
			if 'collection' not in self.__data__ or not self.collection:
				raise RuntimeError("Called method requiring bound collection without one.")
		
		if hasattr(path, 'split'):  # We accept iterables of individual elements, or a string.
			path = path.split('/')
		else:
			path = list(path)
		
		# Remove leading empty elements.
		while path and not path[0]:
			del path[0]
		
		# Remove trailing empty elements.
		while path and not path[-1]:
			del path[-1]
		
		# Determine the full list of possible paths and prepare the query.
		paths = [('/' + '/'.join(path[:i])) for i in range(len(path) + 1)]
		criteria = (self & {'path': {'$in': paths}}).as_query
		
		if hasattr(projection, 'as_projection'):  # Get the bare projection.
			projection = projection.as_projection
		
		if __debug__:
			log.debug("Searching for asset nearest: /" + '/'.join(path), extra=dict(
					query = criteria,
					projection = projection
				))
		
		# Issue the query against our bound collection.
		return self.collection.find_one(criteria, projection, sort=(('path', -1), ))
	
	# Basic Queries
	# These cover fairly basic attributes of asset documents, for convienence.
	
	def id(self, ref):
		data = self.__data__.copy()
		data['operations'] = {'_id': ref}
		return self.__class__(**data)
	
	def named(self, name):
		"""Filter to assets with a given name, useful primarily when chained with other criteria."""
		return self & {'name': name}
	
	def of_type(self, kind):
		"""Restrict to instances of specific Asset subclasses.
		
		Specify the kind either as a full dot-colon import path (such as is stored in the database) or by passing in
		an actual Asset subclass to filter for.
		
		Unlike an `isinstance()` check, this is explicit and does not include subclasses of the target class.
		
		For example:
		
			context.taxonomy.of_type(Page)
			context.taxonomy.of_type('web.component.page.model:Page')
		"""
		if not isinstance(kind, str):
			kind = name_(kind)
		
		return self & {'_cls': kind}
	
	# Asset Management
	# Basic management operations.
	
	def empty(self):
		"""Delete all descendants of the currently filtered assets.
		
		Because this is removing every single descendant, there is no need to update asset ordering. Allows chaining
		as the parent elements (currently filtered elements) remain.
		
		Because this is an operation against the descendants, not containers, no modification times are updated.
		"""
		
		result = self.collection.delete_many(self.descendants.as_query)
		
		log.warn("Deleted %d document%s.", result.deleted_count, "" if result.deleted_count == 1 else "s")
		
		return self
	
	def detach(self):
		"""Detach selected documents from the taxonomy."""
		
		with self._unordered as bulk:
			for target, ancestors in self.scalar('_id', 'ancestors'):
				if not ancestors: continue  # Skip already detached assets.
				
				target = self.id(target)
				
				# Update this immediate target, removing its path and parent/ancestors.
				bulk.find(target.as_query).update_one({
						'$unset': {'path': 1, 'parent': 1, 'ancestors': 1}
					})
				
				# Update descendants of that target, eliminating the ancestors we've just detached from.
				bulk.find(target.descendants.as_query).update({
						'$unset': {'path': 1},
						'$pullAll': {'ancestors': ancestors}
					})
		
		(self | self.descendants).coalesce()
		
		return self
	
	def coalesce(self):
		"""Recalculate the path and update the modification time for all selected documents."""
		
		with self._unordered as bulk:
			for target, name, ancestors in self.scalar('_id', 'name', 'ancestors'):
				if ancestors:
					path = '/'.join([ancestor['name'].lstrip('/') for ancestor in ancestors] + [name])
				else:
					path = name
				
				bulk.find({'_id': target}).update_one({
						'$currentDate': {'updated': {'$type': 'date'}},
						'$set': {'path': path}
					})
	
	def insert(self, index, target):
		"""Attach the given target as a child of the filtered asset, at the given index.
		
		If the target is an unsaved document (no `_id` defined) it is first saved. If the target is an ObjectId
		instance, minimal relevant details are first loaded. Negative indexes are permitted.
		
		Chaining from this method results in operations affecting the inserted Asset, not the containing one.
		"""
		
		container = self.one('_id', 'name', 'ancestors')
		parents = container.pop('ancestors', []) + [container]
		
		# Identify the largest possible index and calculate the index to attach at.
		
		last = self.children.first('index', sort=('-index', ))
		if last: last = last['index']  # We only care about the actual index.
		else: last = 0  # No existing children.
		
		if index < 0:  # Allow insertion at indices relative to the end.
			index = last - index + 1
		
		index = max(0, min(index, last + 1))  # Limit to the available range.
		
		# Identify the documents we are attaching.
		
		target, nTargets = self._move_target(target)
		targets = target | target.descendants
		
		# Process the attachments.
		
		# These must happen first, since we don't want to accidentally alter the indexes we add later.
		with self._unordered as bulk:
			# Add a gap to the indexes of siblings.
			bulk.find(self.children.gte(index).as_query).update({'$inc': {'index': nTargets}})
			
			# Associate ancestors.
			bulk.find(targets.as_query).update({'$push': {'ancestors': {'$each': parents, '$position': 0}}})
		
		# Associate parent and assign index.
		with self._unordered as bulk:
			for i, child in enumerate(target.scalar('_id')):
				bulk.find({'_id': child}).update_one({'$set': {'parent': container['_id'], 'index': index + i}})
		
		return self
	
	def append(self, child):
		"""Append the given child to the selected parent."""
		return self.insert(2**24, child)
	
	def appendTo(self, parent):
		"""Append the selected documents as children of the given parent."""
		
		ids = list(self.salar('_id'))
		parent = self._target(parent)
		parent.insert(2**24, self)
		
		if len(ids) == 1:
			return self.id(ids[0])
		
		return self.id({'$in': ids})
	
	def prepend(self, child):
		"""Prepend the given child to the selected parent."""
		return self.insert(0, child)
	
	def prependTo(self, parent):
		"""Prepend the selected documents to the given parent."""
		
		ids = list(self.salar('_id'))
		parent = self._target(parent)
		parent.insert(0, self)
		
		if len(ids) == 1:
			return self.id(ids[0])
		
		return self.id({'$in': ids})
	
	def after(self, target):
		"""Insert the target document after the selected document."""
		
		sibling = self.one('_id', 'index', 'parent')
		self.id(sibling['parent']).insert(sibling['index'] + 1, target)
		return self.id(sibling['_id'])
	
	def before(self, target):
		"""Insert the target document before the selected document."""
		
		sibling = self.one('_id', 'index', 'parent')
		self.id(sibling['parent']).insert(sibling['index'], target)
		return self.id(sibling['_id'])
	
	def insertAfter(self, sibling):
		"""Insert the selected documents after the target sibling."""
		
		sibling = self._target(sibling).one('_id', 'index', 'parent')
		self.id(sibling['parent']).insert(sibling['index'] + 1, self)
		return self  # TODO: Need to re-select IDs like prependTo; lazy.
	
	def insertBefore(self, sibling):
		"""Insert the selected documents before the target sibling."""
		
		sibling = self._target(sibling).one('_id', 'index', 'parent')
		self.id(sibling['parent']).insert(sibling['index'], self)
		return self  # TODO: Need to re-select IDs like prependTo; lazy.
	
	# Taxonomy Querying
	# These are properties where possible to make chaining more elegant.
	
	@property  # children
	def children(self):
		"""Select for all children of the currently filtered assets."""
		
		extra = {k: v for k, v in self.__data__.items() if k != 'operations'}
		parents = list(self.scalar('_id'))
		
		if len(parents) == 1:
			return self.__class__({'parent': parents[0]}, **extra)
		
		return self.__class__({'parent': {'$in': parents}}, **extra)
	
	@property  # descendants
	def descendants(self):
		"""Select for all desdcendants of the currently filtered assets."""
		extra = {k: v for k, v in self.__data__.items() if k != 'operations'}
		parents = list(self.scalar('_id'))
		
		if len(parents) == 1:
			return self.__class__({'ancestors._id': parents[0]}, **extra)
		
		return self.__class__({'ancestors._id': {'$in': list(self.scalar('_id'))}}, **extra)
	
	# Sibling queries.
	
	@property  # next
	def next(self):
		"""Select the sibling immediatly following this one."""
		
		child = self.one('index', 'parent')
		sibling = self.id(child['parent']).children.gt(child['index']).first('_id', sort=('index', ))
		
		if not sibling:
			return
		
		return self.id(sibling['_id'])
	
	@property  # nextAll
	def nextAll(self):
		"""Select all siblings following this one."""
		
		child = self.one('index', 'parent')
		return self.id(child['parent']).children.gt(child['index'])
	
	@property  # prev
	def prev(self):
		"""Select the sibling immediately prior to this one."""
		
		child = self.one('index', 'parent')
		sibling = self.id(child['parent']).children.lt(child['index']).first('_id', sort=('-index', ))
		
		if not sibling:
			return
		
		return self.id(sibling['_id'])
	
	@property  # prevAll
	def prevAll(self):
		"""Select all siblings prior to this one."""
		
		child = self.one('index', 'parent')
		return self.id(child['parent']).children.lt(child['index'])
	
	@property  # siblings
	def siblings(self):
		"""Select all siblings of this document."""
		
		child = self.one('index', 'parent')
		return self.id(child['parent']).children.lt(child['index']).gt(child['index'])
	
	# Querying by position.
	
	def eq(self, index):
		return self & {'index': index}
	
	def gt(self, index):
		return self & {'index': {'$gt': index}}
	
	def gte(self, index):
		return self & {'index': {'$gte': index}}
	
	def lt(self, index):
		return self & {'index': {'$lt': index}}
	
	def lte(self, index):
		return self & {'index': {'$lte': index}}
	
	# Complex queries.
	
	def has(self, filter):
		"""Find the element (out of those currently selected) which contains a descendant matching the filter."""
		raise NotImplementedError()
	
	def closest(self, filter):
		"""For each document selected find the closest ancestor matching the given filter."""
		raise NotImplementedError()
	


