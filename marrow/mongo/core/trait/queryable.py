from collections import Mapping
from functools import reduce
from operator import and_
from typing import Union, Set

from pymongo.cursor import Cursor, CursorType
from pymongo.collection import Collection as PyMongoCollection

from ..types import Optional, Set, Mapping, Tuple
from ... import Document, F, Filter, P, S
from ...trait import Collection
from ...util import odict
from ....package.loader import traverse


class QueryableFilter(Filter):
	"""Additional behaviour for queryable filters.
	
	This provides a simplified query syntax, free of nearly all boilerplate (repeated mandatory code).
	
	Additional semantics include:
	
	* Filters generated from Queryable collections may be iterated to issue the query and produce a PyMongo Cursor.
	
		for record in User.age > 27:
			print(record)
	
	* Filters may be combined as before (using binary "&" and "|" operators), however this has been extended to support
	  sets of additional criteria, and additional operators: addition and subtraction.  Where addition performs an "or"
	  to include additional results, a subtraction performs an "and" of the inverse of the set contents, excluding
	  results.
	
	The last offers a few powerful additions:
	
	* Examine the "contents" of a "room" record (an `@property` returning a `QueryableFilter`) and return only the
	  siblings of the current record:
	
		siblings = self.room.contents - {self}
	"""
	
	def __getitem__(self, item:Union[str,int,slice]):
		"""Retrieve the value of the given string key, or apply skip/limit options."""
		
		if isinstance(item, str):
			return super().__getitem__(item)
		
		return None
	
	def __iter__(self) -> Cursor:
		if hasattr(self.document, 'find') and getattr(self.document, '__bound__', None):
			return self.document.find(self)
		
		elif self.collection:
			return self.collection.find(self)
		
		raise TypeError("Can not iterate an unbound Filter instance.")


class Queryable(Collection):
	"""Extend active collection behaviours to include querying.
	
	A Queryable collection has additional metadata:
	
	``
	"""
	
	UNIVERSAL_OPTIONS: Set[str] = {
			'collation',
			'limit',
			'projection',
			'skip',
			'sort',
		}
	
	FIND_OPTIONS : Set[str] = UNIVERSAL_OPTIONS | {
			'allow_partial_results',
			'batch_size',
			'cursor_type',
			'max_time_ms',  # translated -> modifiers['$maxTimeMS']
			'modifiers',
			'no_cursor_timeout',
			'oplog_replay',
			'tail',
			'wait',
		}
	
	FIND_MAPPING : Mapping[str,str] = {
			'allowPartialResults': 'allow_partial_results',
			'batchSize': 'batch_size',
			'cursorType': 'cursor_type',
			'maxTimeMS': 'max_time_ms',  # See above.
			'maxTimeMs': 'max_time_ms',  # Common typo.
			'noCursorTimeout': 'no_cursor_timeout',
			'oplogReplay': 'oplog_replay',
		}
	
	AGGREGATE_OPTIONS: Set[str] = UNIVERSAL_OPTIONS | {
			'allowDiskUse',
			'batchSize',
			'maxTimeMS',
			'useCursor',
		}
	
	AGGREGATE_MAPPING: Mapping[str,str] = {
			'allow_disk_use': 'allowDiskUse',
			'batch_size': 'batchSize',
			'maxTimeMs': 'maxTimeMS',  # Common typo.
			'max_time_ms': 'maxTimeMS',
			'use_cursor': 'useCursor',
		}
	
	# _Filter = QueryableFilter
	
	@classmethod
	def _prepare_query(cls, mapping:Mapping[str,str], valid, *args, **kw) -> Tuple[Collection, PyMongoCollection, Filter, dict]:
		"""Process arguments to query methods. For internal use only.
		
		Positional arguments are treated as query components, combined using boolean AND reduction.
		
		Keyword arguments are processed depending on the passed in mapping and set of valid options, with non-
		option arguments treated as parametric query components, also ANDed with any positionally passed query
		components.
		
		Parametric querying with explicit `__eq` against these "reserved words" is possible to work around their
		reserved-ness.
		
		Querying options for find and aggregate may differ in use of under_score or camelCase formatting; this
		helper removes the distinction and allows either.
		"""
		
		collection = cls.get_collection(kw.pop('source', None))
		query = getattr(cls, '_Filter', Filter)(document=cls, collection=collection)
		options = {}
		
		if args:
			query &= reduce(and_, args)
		
		# Gather any valid options.
		for key in tuple(kw):
			name = mapping.get(key, key)
			
			if name in valid:
				options[name] = kw.pop(key)
		
		# Support parametric projection via the use of iterables of strings in the form 'field' or '-field',
		# with name resolution. See the documentation for P for details.
		if 'projection' in options and not isinstance(options['projection'], Mapping):
			options['projection'] = P(cls, *options['projection'])
		
		# Support parametric sorting via the use of iterables of strings. See the documentation for S for details.
		if 'sort' in options:
			options['sort'] = S(cls, *options['sort'])
		
		if kw:  # Remainder are parametric query fragments.
			query &= F(cls, **kw)
		
		return cls, collection, query, options
	
	@classmethod
	def _prepare_find(cls, *args, **kw) -> Tuple[Collection, PyMongoCollection, Filter, dict]:
		"""Execute a find and return the resulting queryset using combined plain and parametric query generation.
		
		Additionally, performs argument case normalization, refer to the `_prepare_query` method's docstring.
		"""
		
		cls, collection, query, options = cls._prepare_query(
				cls.FIND_MAPPING,
				cls.FIND_OPTIONS,
				*args,
				**kw
			)
		
		if 'cursor_type' in options and {'tail', 'wait'} & set(options):
			raise TypeError("Can not combine cursor_type and tail/wait arguments.")
		
		elif options.pop('tail', False):
			options['cursor_type'] = CursorType.TAILABLE_AWAIT if options.pop('wait', True) else CursorType.TAILABLE
		
		elif 'wait' in options:
			raise TypeError("Wait option only applies to tailing cursors.")
		
		modifiers = options.get('modifiers', dict())
		
		if 'max_time_ms' in options:
			modifiers['$maxTimeMS'] = options.pop('max_time_ms')
		
		if modifiers:
			options['modifiers'] = modifiers
		
		return cls, collection, query, options
	
	@classmethod
	def _prepare_aggregate(cls, *args, **kw) -> Tuple[Collection, PyMongoCollection, list, dict]:
		"""Generate and execute an aggregate query pipline using combined plain and parametric query generation.
		
		Additionally, performs argument case normalization, refer to the `_prepare_query` method's docstring.
		
		This provides a find-like interface for generating aggregate pipelines with a few shortcuts that make
		aggregates behave more like "find, optionally with more steps". Positional arguments that are not Filter
		instances are assumed to be aggregate pipeline stages.
		
		https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.aggregate
		"""
		
		stages = []
		stage_args = []
		fragments = []
		
		for arg in args:  # Split the positional arguments into filter fragments and projection stages.
			(fragments if isinstance(arg, Filter) else stage_args).append(arg)
		
		cls, collection, query, options = cls._prepare_query(
				cls.AGGREGATE_MAPPING,
				cls.AGGREGATE_OPTIONS,
				*fragments,
				**kw
			)
		
		if query:
			stages.append({'$match': query})
		
		stages.extend(stage_args)
		
		if 'sort' in options:  # Convert the find-like option to a stage with the correct semantics.
			stages.append({'$sort': odict(options.pop('sort'))})
		
		if 'skip' in options:  # Note: Sort + limit memory optimization invalidated when skipping.
			stages.append({'$skip': options.pop('skip')})
		
		if 'limit' in options:
			stages.append({'$limit': options.pop('limit')})
		
		if 'projection' in options:
			stages.append({'$project': options.pop('projection')})
		
		return cls, collection, stages, options
	
	@classmethod
	def find(cls, *args, **kw) -> Cursor:
		"""Query the collection this class is bound to.
		
		Additional arguments are processed according to `_prepare_find` prior to passing to PyMongo, where positional
		parameters are interpreted as query fragments, parametric keyword arguments combined, and other keyword
		arguments passed along with minor transformation.
		
		https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find
		"""
		
		Doc, collection, query, options = cls._prepare_find(*args, **kw)
		return collection.find(query, **options)
	
	@classmethod
	def find_one(cls, *args, **kw) -> Optional[Document]:
		"""Get a single document from the collection this class is bound to.
		
		Additional arguments are processed according to `_prepare_find` prior to passing to PyMongo, where positional
		parameters are interpreted as query fragments, parametric keyword arguments combined, and other keyword
		arguments passed along with minor transformation.
		
		Automatically calls `from_mongo` over the retrieved data to return an instance of the model.
		
		For simple "by ID" lookups, instead of calling `Model.find_one(identifier)` use the short-hand notation that
		treats your model as a Python-native collection as of Python 3.7: (most familiar as used in type annotation)
		
			Model[identifier]
		
		https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find_one
		https://www.python.org/dev/peps/pep-0560/#class-getitem
		"""
		
		if len(args) == 1 and not isinstance(args[0], Filter):
			args = (getattr(cls, cls.__pk__) == args[0], )
		
		Doc, collection, query, options = cls._prepare_find(*args, **kw)
		result = Doc.from_mongo(collection.find_one(query, **options))
		
		return result
	
	# Alias this to conform to Python-native "Collection" API: https://www.python.org/dev/peps/pep-0560/#class-getitem
	def __class_getitem__(cls, identifier):
		"""Support use of a Queryable Document Collection as a class-level collection organized by primary key.
		
		It is important to remember that no query configuration can be provided for these types of lookups; defaults
		will always be utilized. It is equivalent to cls.find_one(identifier), with certain kinds of data exceptions
		transformed into a KeyError.
		
		Ref: https://www.python.org/dev/peps/pep-0560/#class-getitem
		"""
		
		try:
			return cls.find_one(identifier)
		except (AttributeError, TypeError, ValueError):
			raise KeyError()
	
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_delete
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_replace
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find_one_and_update
	
	@classmethod
	def find_in_sequence(cls, field, order, *args, **kw):
		"""Return a QuerySet iterating the results of a query in a defined order. Technically an aggregate.
		
		To be successful one must be running MongoDB 3.4 or later. Document order will not be represented otherwise.
		
		Based on the technique described here: http://s.webcore.io/2O3i0N2E3h0r
		See also: https://jira.mongodb.org/browse/SERVER-7528
		"""
		
		field = traverse(cls, field)
		order = list(order)  # We need to coalesce the value to prepare for multiple uses.
		kw['sort'] = {'__order': 1}
		kw.setdefault('projection', {'__order': 0})
		
		cls, collection, stages, options = cls._prepare_aggregate(
				field.any(order),
				{'$addFields': {'__order': {'$indexOfArray': [order, '$' + ~field]}}},
				*args,
				**kw
			)
		
		if __debug__:  # noqa
			# This "foot shot avoidance" check requires a server round-trip, potentially, so we only do this in dev.
			if tuple(collection.database.client.server_info()['versionArray'][:2]) < (3, 4):  # pragma: no cover
				raise RuntimeError("Queryable.find_in_sequence only works against MongoDB server versions 3.4 or newer.")
		
		return collection.aggregate(stages, **options)
	
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.count
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.distinct
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.group
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.map_reduce
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.inline_map_reduce
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.parallel_scan
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.initialize_unordered_bulk_op
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.initialize_ordered_bulk_op
	
	def reload(self, *fields, **kw):
		"""Reload the entire document from the database, or refresh specific named top-level fields."""
		
		Doc, collection, query, options = self._prepare_find(id=self.id, projection=fields, **kw)
		result = collection.find_one(query, **options)
		
		if fields:  # Refresh only the requested data.
			for k in result:  # TODO: Better merge algorithm.
				if k == ~Doc.id: continue
				self.__data__[k] = result[k]
		else:
			self.__data__ = result
		
		return self
	
	
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.insert_many
	
	#def replace(self, *args, **kw):
	#	"""Replace a single document matching the filter with this document, passing additional arguments to PyMongo.
	#	
	#	**Warning:** Be careful if the current document has only been partially projected, as the omitted fields will
	#	either be dropped or have their default values saved where `assign` is `True`.
	#	
	#	https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.replace_one
	#	"""
	#	pass
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.replace_one
	
	# update
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.update_one
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.update_many
	
	# delete
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.delete_one
	# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.delete_many
