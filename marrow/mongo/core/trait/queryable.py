# encoding: utf-8

from __future__ import unicode_literals

from collections import Mapping
from functools import reduce
from operator import and_

from ...param import F, P, S
from ...trait import Identified
from ....schema.compat import odict
from ....package.loader import traverse


class Queryable(Identified):
	UNIVERSAL_OPTIONS = {
			'collation',
			'limit',
			'projection',
			'skip',
			'sort',
		}
	
	FIND_OPTIONS = UNIVERSAL_OPTIONS | {
			'allow_partial_results',
			'await',
			'batch_size',
			'cursor_type',
			'max_time_ms',  # translated -> modifiers['$maxTimeMS']
			'modifiers',
			'no_cursor_timeout',
			'oplog_replay',
			'tail',
		}
	
	FIND_MAPPING = {
			'allowPartialResults': 'allow_partial_results',
			'batchSize': 'batch_size',
			'cursorType': 'cursor_type',
			'maxTimeMS': 'max_time_ms',  # See above.
			'maxTimeMs': 'max_time_ms',  # Common typo.
			'noCursorTimeout': 'no_cursor_timeout',
			'oplogReplay': 'oplog_replay',
		}
	
	AGGREGATE_OPTIONS = UNIVERSAL_OPTIONS | {
			'allowDiskUse',
			'batchSize',
			'maxTimeMS',
			'useCursor',
		}
	
	AGGREGATE_MAPPING = {
			'allow_disk_use': 'allowDiskUse',
			'batch_size': 'batchSize',
			'maxTimeMs': 'maxTimeMS',  # Common typo.
			'max_time_ms': 'maxTimeMS',
			'use_cursor': 'useCursor',
		}
	
	@classmethod
	def _prepare_query(cls, mapping, valid, *args, **kw):
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
		query = Filter(document=cls, collection=collection)
		query &= reduce(and_, args)
		options = {}
		
		# Gather any valid options.
		for key in tuple(kw):
			name = mapping.get(key, key)
			
			if name in valid:
				options[name] = kw.pop(key)
		
		# Support parametric projection via the use of iterables of strings in the form 'field' or '-field',
		# with name resolution. See the documentation for P for details.
		if 'projection' in options and not isinstance(options, Mapping):
			options['projection'] = P(cls, *options['projection'])
		
		# Support parametric sorting via the use of iterables of strings. See the documentation for S for details.
		if 'sort' in options:
			options['sort'] = S(cls, *options['sort'])
		
		if kw:  # Remainder are parametric query fragments.
			query &= F(cls, **kw)
		
		return cls, collection, query, options
	
	@classmethod
	def _prepare_find(cls, *args, **kw):
		"""Execute a find and return the resulting queryset using combined plain and parametric query generation.
		
		Additionally, performs argument case normalization, refer to the `_prepare_query` method's docstring.
		"""
		
		cls, collection, query, options = cls._prepare_query(
				cls.FIND_MAPPING,
				cls.FIND_OPTIONS,
				*args,
				**kw
			)
		
		if 'cursor_type' in options and {'tail', 'await'} & set(options):
			raise TypeError("Can not combine cursor_type and tail/await arguments.")
		
		elif options.pop('tail', False):
			options['cursor_type'] = ... if options.pop('await', True) else ...
		
		elif 'await' in options:
			raise TypeError("Await option only applies to tailing cursors.")
		
		modifiers = options.get('modifiers', dict())
		
		if 'max_time_ms' in options:
			modifiers['$maxTimeMS'] = options.pop('max_time_ms')
		
		if modifiers:
			options['modifiers'] = modifiers
		
		return cls, collection, query, options
	
	@classmethod
	def _prepare_aggregate(cls, *args, **kw):
		"""Generate and execute an aggregate query pipline using combined plain and parametric query generation.
		
		Additionally, performs argument case normalization, refer to the `_prepare_query` method's docstring.
		
		This provides a find-like interface for generating aggregate pipelines with a few shortcuts that make
		aggregates behave more like "find, optionally with more steps". Positional arguments that are not Filter
		instances are assumed to be aggregate pipeline stages.
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
		
		if 'skip' in options:
			stages.append({'$skip': options.pop('skip')})
		
		return cls, collection, stages, options
	
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
				{'$addFields': {'__order': {'$indexOfArray': [order, '$' + ~traverse(cls, field)]}}},
				*args,
				**kw
			)
		
		if tuple(collection.database.connection.server_info()['versionArray'][:2]) < (3, 4):
			raise RuntimeError("Queryable.find_in_sequence only works against MongoDB server versions 3.4 or newer.")
		
		return collection.aggregate(stages, **options)