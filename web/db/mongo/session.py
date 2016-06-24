# encoding: utf-8

"""Session handling extension using mongo db storage."""

from web.core.util import lazy

log = __import__('logging').getLogger(__name__)

import string
import random
def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


class Session(object):
	def __init__(self):
		self._id = id_generator()
		self._new = True

	def touch(self):
		self._new = False

class SessionExtension(object):
	"""Manage client sessions using data stored in a database

	This extension stores session data in mongo and handles sessions based on a cookie
	"""

	provides = {'session'}
	needs = {'request', 'db'}


	def __init__(self, **config):
		"""Configure settings

		Such as domain, ttl, cookie name, etc
		"""

		self._sessions = {}
		self._cookie_name = 'user_session'
		self._max_age = 360
		self._http_only = True
		self._path = '/'
		pass

	def get_session(self, context):
		"""Return the session instance

		Check for a session cookie and return the corresponding session if it exists.
		Creates a new Session instance if the cookie doesn't match.
		"""

		if(self._cookie_name in context.request.cookies):
			key = context.request.cookies[self._cookie_name]
			if(key in self._sessions):
				return self._sessions[key]
		return Session()

	def start(self, context):
		context.session = lazy(self.get_session, 'session')

	def after(self, context):
		"""Manage cookie headers

		Determine if a session was created this request and set the cookie header if so
		"""

		if 'session' not in context.__dict__ or context.session._new == False:
			return

		if __debug__:
			log.debug("Created new session, setting cookie")

		context.response.set_cookie(
				httponly = self._http_only,
				max_age = self._max_age,
				name = self._cookie_name,
				path = self._path,
				value = context.session._id,
			)
		context.session.touch()

	def done(self, context):
		"""Save session data after request cycle

		If the session was accessed (whether new or not), store it in the db
		"""

		if 'session' not in context.__dict__:
			return

		if __debug__:
			log.debug('Session accessed, saving data')

		# TODO: Store in db
		self._sessions[context.session._id] = context.session
