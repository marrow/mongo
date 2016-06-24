# encoding: utf-8

"""Session handling extension using mongo db storage."""

from web.core.util import lazy

from marrow.mongo.core import Document
from marrow.mongo.field.base import ObjectId, oid

log = __import__('logging').getLogger(__name__)


class Session(Document):
	id = ObjectId('_id', required=True, generated=False, default=None)

class SessionExtension(object):
	"""Manage client sessions using data stored in a database

	This extension stores session data in mongo and handles sessions based on a cookie
	"""

	provides = {'session'}
	needs = {'request', 'db'}


	def __init__(self, Document=Session, collection='session', **config):
		"""Configure settings

		Such as domain, ttl, cookie name, etc
		"""

		self._Document = Document
		self._collection = collection
		self._cookie_name = 'user_session'
		self._http_only = True
		self._max_age = 360
		self._path = '/'
		pass

	def get_session(self, context):
		"""Return the session instance

		Check for a session cookie and return the corresponding session if it exists.
		Creates a new Session instance if the cookie doesn't match.
		"""

		if(self._cookie_name in context.request.cookies):
			key = context.request.cookies[self._cookie_name]
			if __debug__:
				log.debug("Querying for session record.")
				log.debug(key)

			result = context.db.default[self._collection].find_one({"_id": oid(key)})
			if result is not None:
				return self._Document.from_mongo(result)

		return self._Document()

	def start(self, context):
		context.session = lazy(self.get_session, 'session')

	def after(self, context):
		"""Manage cookie headers

		Determine if a session was created this request and set the cookie header if so
		"""

		log.debug('executing after')
		log.debug(context.session.id)
		if 'session' not in context.__dict__ or context.session.id is not None:
			return

		if __debug__:
			log.debug("Created new session, setting cookie")

		context.db.default[self._collection].insert_one(context.session)
		if context.session.id is None:
			return

		id = str(context.session.id)
		context.response.set_cookie(
				httponly = self._http_only,
				max_age = self._max_age,
				name = self._cookie_name,
				path = self._path,
				value = id,
			)

	def done(self, context):
		"""Save session data after request cycle

		If the session was accessed (whether new or not), store it in the db
		"""

		if 'session' not in context.__dict__:
			return

		if __debug__:
			log.debug('Session accessed, saving data')

		# TODO: Store in db
		# self._sessions[context.session._id] = context.session
