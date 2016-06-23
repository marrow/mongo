# encoding: utf-8

from bson.json_util import loads


log = __import__('logging').getLogger(__name__)


class MongoDBResource(object):
	__dispatch__ = 'resource'
	
	def __init__(self, context, collection=None, record=None):
		self._ctx = context
		self._collection = collection
		self._record = record
	
	def get(self) -> 'json':
		return self._record
	
	def delete(self) -> 'json':
		coll = self._collection
		pk = coll.__pk__
		result = coll.__model__.delete_one({pk: self._record[pk]})
		return dict(ok=bool(result.deleted_count), ack=result.acknowledged)


