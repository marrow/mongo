# pragma: no cover

"""Experimental WebCore session handler using MongoDB storage."""

from typing import Union

from bson import ObjectId as oid

from marrow.mongo import Index, utcnow
from marrow.mongo.field import TTL, ObjectId
from marrow.mongo.trait import Queryable


class MongoSessionStorage(Queryable):
	id = Queryable.id.adapt(positional=False)
	expires = TTL('expires', default=None, positional=False)  # Override this field to specify an expiry time.
	
	_expires = Index('expires', expire=0)
	
	@property
	def expired(self) -> bool:
		return self.expires > utcnow()
	
	def __getattr__(self, name:str):
		try:
			return self.__dict__['__data__'][name]
		except KeyError:
			pass
		
		raise AttributeError("Session has no attribute: " + name)
	
	def __setattr__(self, name:str, value):
		if name[0] == '_' or '__data__' not in self.__dict__:
			return super(MongoSessionStorage, self).__setattr__(name, value)
		
		self.__data__[name] = value
	
	def __delattr__(self, name:str):
		if name[0] == '_' or '__data__' not in self.__dict__:
			return super().__delattr__(name)
		
		try:
			del self.__data__[name]
		except KeyError:
			pass
		
		raise AttributeError()


class MongoSession:
	needs = {'db'}
	
	_collection: str
	_database: str
	_Document: Queryable
	
	def __init__(self, Document:Queryable=MongoSessionStorage, collection:str=None, database:str=None):
		""""""
		
		self._collection = collection or getattr(Document, '__collection__', None) or 'sessions'
		self._database = database or getattr(Document, '__database__', None) or 'default'
		
		Document.__collection__ = self._collection
		self._Document = Document
	
	def start(self, context):
		db = context.db[self._database]
		self._Document.bind(db)
	
	def is_valid(self, context, sid:Union[str,oid]) -> bool:
		"""Identify if the given session ID is currently valid.
		
		Return True if valid, False if explicitly invalid, None if unknown.
		"""
		
		record = self._Document.find_one(sid, project=('expires', ))
		
		if not record:
			return
		
		return not record._expired
	
	def invalidate(self, context, sid:oid) -> bool:
		"""Immediately expire a session from the backing store."""
		
		result = self._Document.get_collection().delete_one(D.id == sid)
		
		return result.deleted_count == 1
	
	def __get__(self, session:MongoSessionStorage, type=None):
		"""Retrieve the session upon first access and cache the result."""
		
		if session is None:
			return self
		
		D = self._Document
		
		result = D.find_one(session.id)  # pylint:disable=protected-access
		
		# XXX
		if not result:
			result = D(str(session.id))  # pylint:disable=protected-access
		
		session[self.name] = result
		
		return result
	
	def persist(self, context):
		"""Update or insert the session document into the configured collection"""
		
		D = self._Document
		document = context.session[self.name]
		
		D.get_collection().replace_one(D.id == document, document, True)