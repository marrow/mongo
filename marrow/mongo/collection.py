# encoding: utf-8

"""Note: Only tested on Python 3!"""

from __future__ import unicode_literals

from bson import ObjectId
from bson.json_util import loads
from pymongo import ASCENDING, DESCENDING

from .query.djangoish import F
from .resource import MongoDBResource


log = __import__('logging').getLogger(__name__)


def sort_order(input):
	"""Translate a Djanglish ordering into what MongoDB expects."""
	
	if not isinstance(input, (list, tuple)):
		input = (i.strip().replace('__', '.') for i in input.split(','))
	
	if not input:
		return None
	
	return [(i.lstrip('-'), DESCENDING if i[0] == '-' else ASCENDING) for i in input]


class MongoDBCollection(object):
	"""A web-accessible MongoDB collection.
	
	This represents a REST "collection of resources" backed by MongoDB "collection", supporting standard collection
	actions such as record retrieval and querying.

	This requires that the WebCore AnnotationExtension be enabled, and that there exists some handler for
	`("json", ...)` return values. Notably the serializer will need to support MongoDB types, such as the json_util
	package provided by pymongo itself.
	"""
	
	__dispatch__ = 'resource'
	__resource__ = MongoDBResource
	__model__ = None
	__pk__ = '_id'
	
	def __init__(self, context, collection=None, record=None):
		self._ctx = context
		self._collection = collection
		self._record = record
	
	def __getitem__(self, identifier):
		"""Retrieve a model instance from the database.
		
		This conforms to the web.dispatch.resource Collection protocol.
		"""
		identifier = identifier.strip()
		
		if self.__pk__ == '_id' and len(identifier) == 24:
			# Attempt to automatically cast ObjectIds.
			try:
				identifier = ObjectId(identifier)
			except:
				pass  # Continue as-is with the original value.
		
		query = {'_id': identifier}
		query = self._filter(query)
		record = self.__model__.find_one(query)
		
		if not record:
			raise KeyError()
		
		if self.__model__.model:  # Wrap the record in the appropraite marrow.mongo Document class, if given.
			record = self.__class__.__model__.model.from_mongo(record)
		
		return record
	
	def _filter(self, query, **kw):
		"""Populate and return a MongoDB filter document (query) for use in listings.
		
		You would generally override this in your subclass to implement basic query filtering, security, etc. Because
		this query is used to populate the listing (GET), it is also applied to attempts to fetch contained resources.
		
		Keyword arguments are those passed as query string parameters to the GET. No arguments can be given in the
		fetch-a-record case.
		
		This is a cooperative process, remember to call `super()`!
		"""
		return query
	
	def _process(self, document):
		"""Allow for mutation of the outgoing document.
		
		Used during search result processing, it might be a better idea to put your own code in a custom
		`Document.as_rest` override for most processing; this is intended primarily for manipulation that requires
		the request context.
		
		This is a cooperative process, remember to call `super()`!
		"""
		return document
	
	def get(self, q=None, sort: sort_order = [('_id', DESCENDING)], more=None, **kw) -> 'json':
		"""Search a collection for records.
		
		Optional arguments include:
		
		* `q` - An optional full text search.
		* `sort` - An optional comma-separated list of fields in Djanglish format. Prefix with a `-` to reverse.
		* `more` - The point to continue loading records from.
		* Additional keyword arguments are translated into a Djanglish query by the default _filter implementation.
		
		Extensive support for HTTP and querying features:
		
		Request support for cache control headers such as If-Modified-Since.
		If-Modified-Since
		"""
		exclude = set()
		query = F(self.__class__.__model__.model, **kw) if self.__class__.__model__.model else kw
		
		if more:
			exclude.add('_id')
			query[self.__pk__] = {'$gt': ObjectId(more)}
		
		self._filter(query, **kw)
		
		results = self.__model__.find(query)
		total = results.count()
		results = list(results[:25])
		resp = self._ctx.response
		
		def adulterate(result):
			# Since we're using REST, identify resources by their URI.
			result['$uri'] = self._ctx.request.relative_url(str(result['_id']))
			del result['_id']
			
			return result
		
		response = {
				'ok': True,
				'$count': total,
				'$sort': ((f if d == ASCENDING else ('-' + f)) for f, d in sort),
			}
		
		
		
		if query:
			response['$query'] = query
		
		if set(query.keys()) - exclude:
			response['hidden'] = self.__model__.count() - total
		
		if total > 25:  # Allow continuation $gt the last value.
			response['$more'] = self._ctx.request.path_url + "?more=" + str(results[-1]['_id']),
		
		if __debug__:
			log.info("Collection search requested.", extra=response)
		
		response['results'] = [adulterate(i) for i in results]
		
		return response
	
	def post(self) -> 'json':  # WARNING: Hideously insecure, do not use.  ;P
		data = loads(self._ctx.request.body.decode('utf-8'))
		result = self.__model__.insert_one(data)
		return dict(ok=True, ack=result.acknowledged, _id=result.inserted_id)
