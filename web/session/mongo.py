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

	def __init__(self, Document=MongoSessionStorage, collection='session', **config):
		self._Document = Document
		self._collection = collection

	def get_session(self, session_group):
		context = session_group._ctx
		sess_id = session_group._id

		if __debug__:
			log.debug("Searching for session: "+str(sess_id))

		result = context.db.default[self._collection].find_one({"session_id": sess_id})
		if result is not None:
			return self._Document.from_mongo(result)

		doc = self._Document()
		doc.session_id = sess_id
		return doc

	def after(self, context):
		"""Insert the session document if it was created during this request"""
		# This is only called when the mongo session has been accessed, so we can skip those checks

		if context.session[self.__name__].id is not None: return

		if __debug__:
			log.debug("Storing new session document")

		context.db.default[self._collection].insert_one(context.session[self.__name__])

	def done(self, context):
		"""Save the session document if it has been modified during this request"""

		# determine whether or not to save document
		if __debug__:
			log.debug("Updating session document")
