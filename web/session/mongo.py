# encoding: utf-8

"""Session handling extension using mongo db storage."""

from web.core.util import lazy

from marrow.mongo.core import Document
from marrow.mongo.field.base import ObjectId, String, Binary

log = __import__('logging').getLogger(__name__)


class MongoSessionStorage(Document):
	id = ObjectId('_id', required=True, generated=False, default=None)
	session_id = String()


class MongoSession(object):
	needs = {'mongodb'}
	
	def __init__(self, Document=MongoSessionStorage, collection='session', expire=None, **config):
		self._Document = Document
		self._collection = collection
		self._expire = expire
	
	def is_valid(self, context, sid):
		return context.db.default[self._collection].find_one({"session_id": sid}) is not None
	
	def invalidate(self, context, sid):
		# not sure what the return value should be yet
		return context.db.default[self._collection].delete_one({"session_id": sid}) == 1
	
	def load(self, context, sid):
		context = session_group._ctx
		
		if __debug__:
			log.debug("Searching for session: "+str(sid))
		
		result = context.db.default[self._collection].find_one({"session_id": sid})
		if result is not None:
			return self._Document.from_mongo(result)
		
		doc = self._Document()
		doc.session_id = sid
		return doc
	
	def persist(self, context, sid, session):
		"""Update or insert the session document into the configured collection"""
		
		if __debug__:
			log.debug("Persisting session document")
		
		if(session.id is None)
			context.db.default[self._collection].insert_one(context.session[self.__name__])
			return
		
		# TODO: Update existing record
