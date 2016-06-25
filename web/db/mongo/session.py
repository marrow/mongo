# encoding: utf-8

"""Session handling extension using mongo db storage."""

from web.core.util import lazy

from marrow.mongo.core import Document
from marrow.mongo.field.base import ObjectId, oid

log = __import__('logging').getLogger(__name__)


class MongoSession(Document):
	id = ObjectId('_id', required=True, generated=False, default=None)

class MongoSessionEngine(object):
	def __init__(self, Document=MongoSession, collection='session', **config):
		self._Document = Document
		self._collection = collection

	def get_session(self, context):
		key = context.session.id
		if __debug__:
			log.debug("Querying for session record.")
			log.debug(key)

		result = context.db.default[self._collection].find_one({"_id": oid(key)})
		if result is not None:
			return self._Document.from_mongo(result)

		return self._Document()

	def after(self, context):
		"""Insert the session document if it was created during this request"""
		# This is only called when the mongo session has been accessed, so we can skip those checks

		if context.session.mongo.id is not None: return

		if __debug__:
			log.debug("Storing new session document")

		context.db.default[self._collection].insert_one(context.session.mongo)

	def done(self, context):
		"""Save the session document if it has been modified during this request"""

		# determine whether or not to save document
		if __debug__:
			log.debug("Updating session document")
