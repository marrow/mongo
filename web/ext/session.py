# encoding: utf-8

"""Session handling extension using mongo db storage."""

from web.core.util import lazy

from web.core.context import ContextGroup

log = __import__('logging').getLogger(__name__)


import os, base64
from functools import partial

# Probably want something more secure than this, but I didn't want to add any dependencies
def generate_session_id(num_bytes=16):
	"""Generates a n byte session id"""
	return base64.b64encode(os.urandom(num_bytes))

class MemorySessionStorage(object):
	def __init__(self, **config):
		self._sessions = {}

	def get_session(self, context):
		if(context.session.id not in self._sessions):
			self.sessions[context.session.id] = Context()


		log.debug("Accessing memory session")
		log.debug(context.session.id)

		return self.sessions[context.session.id]

class SessionExtension(object):
	"""Manage client sessions using storage engines

	This extension stores session data in session storage engines and handles the session cookie
	"""

	__slots__ = ('engines', 'uses', 'needs', 'provides', '_cookie')

	_provides = {'session'}
	_needs = {'request'}

	def __init__(self, **config):
		"""Configure settings

		Such as domain, ttl, cookie name, etc
		"""

		conf = self._configure(**config)
		self.engines = conf['engines']
		self._cookie = conf['cookie']

		self.uses = set()
		self.needs = set(self._needs)
		self.provides = set(self._provides)

		for name, engine in self.engines.items():
			if engine is None: continue
			engine.__name__ = name  # Inform the engine what its name is.
			self.uses.update(getattr(engine, 'uses', ()))
			self.needs.update(getattr(engine, 'needs', ()))
			self.provides.update(getattr(engine, 'provides', ()))

	def _configure(self, **config):
		config = config or dict()

		if 'engines' not in config: config['engines'] = {'default': MemorySessionStorage()}
		# TODO: Check that there is a default

		if 'cookie' not in config: config['cookie'] = {}

		# Handle cookie defaults
		cookie = config['cookie']
		if 'name' not in cookie:
			cookie['name'] = 'user_session'

		if 'max_age' not in cookie:
			cookie['max_age'] = 360

		if 'http_only' not in cookie:
			cookie['http_only'] = True

		if 'path' not in cookie:
			cookie['path'] = '/'

		#Probably want a way to have any params beyond those listed above go into **kwargs on response.set_cookie
		return config

	def get_session_group(self, context):
		if(self._cookie.name in context.request.cookies):
			key = context.request.cookies[self._cookie.name]
			# TODO: check if any storage engines have this key, if not generate a new one
			# otherwise use this key
			context.session['id'] = key
		else:
			context.session['id'] = generate_session_id()
			context.session['_new'] = True


		log.debug("Accessing session group")

		return context.session._promote("SessionGroup")

	def start(self, context):
		context.session = ContextGroup(**{name: lazy(value.get_session, name) for name, value in self.engines.items()})

	def prepare(self, context):
		log.debug("Preparing session group")
		context.session = lazy(self.get_session_group, 'session')

	def after(self, context):
		if 'id' not in context.session.__dict__:
			return

		if _new in context.session.__dict__:
			return

		context.response.set_cookie(
				httponly = self._cookie.http_only,
				max_age = self._cookie.max_age,
				name = self._cookie.cookie_name,
				path = self._cookie.path,
				secure = self._cookie.secure,
				value = context.session_id,
			)
