# encoding: utf-8
# pragma: no cover

"""Experimental WebCore session handler using MongoDB storage."""

from bson import ObjectId as oid

from marrow.mongo import Index, utcnow
from marrow.mongo.field import TTL, ObjectId
from marrow.mongo.trait import Queryable

log = __import__('logging').getLogger(__name__)


class MongoSessionStorage(Queryable):
	expires = TTL('expires', default=None)  # Override this field to specify an expiry time.
	
	_expires = Index('expires', expire=0)
	
	@property
	def _expired(self):
		return self.expires > utcnow()
	
	def __getattr__(self, name):
		try:
			return self.__dict__['__data__'][name]
		except KeyError:
			pass
		
		raise AttributeError("Session has no attribute: " + name)
	
	def __setattr__(self, name, value):
		if name[0] == '_' or '__data__' not in self.__dict__:
			return super(MongoSessionStorage, self).__setattr__(name, value)
		
		self.__data__[name] = value


class MongoSession(object):
	needs = {'db'}
	
	def __init__(self, Document=MongoSessionStorage, collection=None, database=None):
		""""""
		
		self._collection = collection or getattr(Document, '__collection__', None) or 'sessions'
		self._database = database or getattr(Document, '__database__', None) or 'default'
		
		Document.__collection__ = self._collection
		self._Document = Document
	
	def start(self, context):
		db = context.db[self._database]
		self._Document.bind(db)
	
	def is_valid(self, context, sid):
		"""Identify if the given session ID is currently valid.
		
		Return True if valid, False if explicitly invalid, None if unknown.
		"""
		
		record = self._Document.find_one(sid, project=('expires', ))
		
		if not record:
			return
		
		return not record._expired
	
	def invalidate(self, context, sid):
		"""Immediately expire a session from the backing store."""
		
		result = self._Document.get_collection().delete_one({'_id': sid})
		
		return result.deleted_count == 1
	
	def __get__(self, session, type=None):
		"""Retrieve the session upon first access and cache the result."""
		
		if session is None:
			return self
		
		D = self._Document
		
		result = D.find_one(session._id)  # pylint:disable=protected-access
		
		if not result:
			result = D(str(session._id))  # pylint:disable=protected-access
		
		result = session[self.name] = D.from_mongo(result)  # TODO: Pass the projection through to conversion.
		
		return result
	
	def persist(self, context):
		"""Update or insert the session document into the configured collection"""
		
		D = self._Document
		document = context.session[self.name]
		
		D.get_collection().replace_one(D.id == document.id, document, True)
