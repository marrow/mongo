# encoding: utf-8

"""Session handling extension using mongo db storage."""

from web.core.util import lazy

from web.core.context import Context, ContextGroup

log = __import__('logging').getLogger(__name__)


import os, base64
from functools import partial

# Probably want something more secure than this, but I didn't want to add any dependencies
def generate_session_id(num_bytes=16):
	"""Generates random string which is then base64 encoded

	* `num_bytes` -- the number of bytes this random string should consist of
	"""

	return base64.b64encode(os.urandom(num_bytes))

class MemorySessionEngine(object):
	def __init__(self, **config):
		"""Initialize session storage object"""
		self._sessions = {}

	def get_session(self, session_group):
		"""Lazily get the session storage object

		* `instance` -- the SessionGroup instance that this engine instance is an attribute of.
		"""

		# Attempting to access the `instance` itself could result in a recursion loop if this storage engine is the
		# default, as this function will be called again when accessing either no attribute or an invalid attribute on the
		# `SessionGroup`. Instead, information should be grabbed from `instance._ctx`, which is the `RequestContext`.
		context = session_group._ctx
		if(context.session._id not in self._sessions):
			self._sessions[context.session._id] = Context()


		if __debug__:
			log.debug("Accessing memory session")

		return self._sessions[context.session._id]

class SessionExtension(object):
	"""Manage client sessions using storage engines

	This extension stores session data in session storage engines and handles the session cookie
	"""

	__slots__ = ('engines', 'uses', 'needs', 'provides', '_cookie')

	_provides = {'session'}
	_needs = {'request'}

	def __init__(self, **config):
		"""Configure settings and setup slots for the extension

		Current settings consist of the following:
		* `engines` -- either `None`, which will setup a default `MemorySessionEngine`, or a `dict` of
		 	SessionStorageEngines. This setting is used to tell the `SessionExtension` which storage engines to use. This
			setting should contain at least one entry with the key `default`
		* `cookie' -- either `None` or a `dict`. This is used to tell the `SessionExtension` which settings to use
			for the browser cookie. possible options are 'name' - `str`, 'max_age' - `int`, 'http_only' - `True` or `False`,
			and `str` 'path'
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
		"""Parses `**kwargs` from `__init__` into valid settings for use by the extension"""

		config = config or dict()

		if 'engines' not in config: config['engines'] = {'default': MemorySessionEngine()}
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

	def get_session_id(self, session_group):
		"""Lazily get the session id for the current request

		* `session_group` -- the `SessionGroup` that contains the session engines
		"""

		# Use session_group._ctx in order to access the RequestContext
		context = session_group._ctx

		# Check if the browser sent a session cookie
		if(self._cookie['name'] in context.request.cookies):
			print('what')
			id = context.request.cookies[self._cookie['name']]
			# TODO: check if any storage engines have this key, if not generate a new one
			# otherwise use this key
		else:
			id = generate_session_id()
			session_group['_new'] = True

		return id

	def start(self, context):
		"""Setup context attributes that will be used on RequestContext"""

		context.session = ContextGroup(**{name: lazy(value.get_session, name) for name, value in self.engines.items()})
		context.session['_id'] = lazy(self.get_session_id, '_id')

		self._handle_event('start', context, True)

	def prepare(self, context):
		"""Set the _ctx attribute for access in lazy functions and promote the ContextGroup"""
		if __debug__:
			log.debug("Preparing session group")

		# Give lazy wrapped functions a way to access the RequestContext
		context.session['_ctx'] = context
		# Must promote the ContextGroup so that the lazy wrapped function calls operate properly
		context.session = context.session._promote('SessionGroup')

		self._handle_event('prepare', context)


	def after(self, context):
		"""Determine if the session cookie needs to be set"""

		# if the session was accessed at all during this request
		if '_id' not in context.session.__dict__:
			return

		# engines could have made a new storage even if the id is old
		self._handle_event('after', context)

		# if the session id has just been generated this request, we need to set the cookie
		if '_new' not in context.session.__dict__:
			return

		# see WebOb request / response
		context.response.set_cookie(
				httponly = self._cookie['http_only'],
				max_age = self._cookie['max_age'],
				name = self._cookie['name'],
				path = self._cookie['path'],
				value = context.session._id,
			)


	def _handle_event(self, event, override = False, *args, **kw):
		"""Send a signal event to all session engines

		* `event` -- the signal to run on all session engines
		* `override` -- if False then the event will only be run on session engines that have been accessed during this
			request. If True then the event will attempt to run on all session engines, regardless of if they have been
			accessed or not.
		* `*args` -- additional args passed on to session engine callbacks
		* `**kwargs` -- additional kwargs passed on to session engine callbacks
		"""

		# In a typical scenario these callbacks will only happen if the specific session engine was accessed
		for engine in self.engines.values():
			if engine is not None and hasattr(engine, event):
				if override or engine.__name__ in context.session.__dict__:
					getattr(engine, event)(*args, **kw)

	def __getattr__(self, name):
		"""Pass any signals SessionExtension doesn't use on to SessionEngines"""

		# Only allow signals defined in `web.ext.extensions.WebExtensions`
		if name not in ('stop', 'graceful', 'dispatch', 'before', 'done', 'interactive', 'inspect'):
			raise AttributeError()

		return partial(self._handle_event, name)
