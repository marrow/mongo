# encoding: utf-8

from collections import MutableMapping, OrderedDict

from .string import String
from ....schema import Attribute
from ....schema.compat import unicode, py2

try:
	from html import escape
except ImportError:  # Adapt to locations on legacy versions.
	from cgi import escape

try:
	from urllib.parse import urlsplit, quote_plus, unquote_plus, parse_qsl
except ImportError:  # Adapt to locations on legacy versions.
	from urlparse import urlsplit, parse_qsl
	from urllib import quote_plus, unquote_plus

try:
	from pathlib import PurePosixPath as _Path
except ImportError:
	from pathlib2 import PurePosixPath as _Path


class URIString(MutableMapping):
	"""An object representing a URL (absolute or relative) and its components.
	
	Acts as a mutable mapping for manipulation of query string arguments. If the query string is not URL
	"form encoded" attempts at mapping access or manipulation will fail with a ValueError. No effort is made to
	preserve original query string key order. Repeated keys will have lists as values.
	"""
	
	# Skip allocation of a dictionary per instance by pre-defining available slots.
	__slots__ = ('_url', 'scheme', 'user', 'password', 'host', 'port', '_path', '_query', 'fragment')
	__parts__ = {'scheme', 'user', 'password', 'host', 'port', 'path', 'query', 'fragment', 'username', 'hostname'}
	
	# Basic Protocols
	
	def __init__(self, url=None, **parts):
		self._query = {}
		
		if hasattr(url, '__link__'):
			url = url.__link__
		
		if isinstance(url, URIString):
			url = url.url
		
		self.url = url  # If None, this will also handle setting defaults.
		
		if parts:  # If not given a base URL, defines a new URL, otherwise update the given URL.
			for part, value in parts.items():
				if part not in self.__parts__:
					raise TypeError("Unknown URL component: " + part)
				
				setattr(self, part, value)
	
	# String Protocols
	
	def __repr__(self):
		return 'URI({0!s})'.format(self)
	
	def __str__(self):
		"""Return the Unicode text representation of this URL."""
		
		return self.url
	
	def __bytes__(self):
		"""Return the binary string representation of this URL."""
		
		return self.url.encode('utf-8')
	
	if py2:  # Adapt to Python 2 semantics on legacy versions.
		__unicode__ = __str__
		__str__ = __bytes__
	
	def __html__(self):
		return '<a href="{address}">{summary}</a>'.format(
				address = escape(self.url),
				summary = escape(self.host + unicode(self.path)),
			)
	
	# Comparison Protocols
	
	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			other = self.__class__(other)
		
		for part in self.__parts__:
			if not getattr(self, part, None) == getattr(other, part, None):
				return False
		
		return True
	
	def __ne__(self, other):
		return not self == other
	
	# Mapping Protocols
	
	def __getitem__(self, name):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		return self._query[name]
	
	def __setitem__(self, name, value):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		self._url = None  # Invalidate the cached string.
		self._query[name] = unicode(value)
	
	def __delitem__(self, name):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		self._url = None  # Invalidate the cached string.
		del self._query[name]
	
	def __iter__(self):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		return iter(self._query)
	
	def __len__(self):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		return len(self._query)
	
	# Accessor Properties
	
	@property
	def username(self):
		return self.user
	
	@username.setter
	def username(self, value):
		self.user = value
	
	@property
	def hostname(self):
		return self.host
	
	@hostname.setter
	def hostname(self, value):
		self.host = value
	
	@property
	def path(self):
		return self._path
		
	@path.setter
	def path(self, value):
		if value:
			self._path = _Path(value)
		else:
			self._path = None
	
	@property
	def query(self):
		return self._query
	
	@query.setter
	def query(self, value):
		if isinstance(value, unicode):
			self.qs = value
			return
		
		self._query = {k: unicode(v) for k, v in dict(value).items()}
	
	@property
	def url(self):
		if not self._url:
			self._compile()
		
		return self._url
	
	@url.setter
	def url(self, value):
		if value:
			self._url = value
			self._decompile()
			return
		
		self._url = None
		self.scheme = None
		self.user = None
		self.password = None
		self.host = None
		self.port = None
		self._path = None
		self._query = {}
		self.fragment = ''
	
	@property
	def qs(self):
		if not self._query:
			return ""
		
		if isinstance(self._query, unicode):
			return self._query  # Handle "preserved" edge cases.
		
		parts = []
		
		for k, v in self._query.items():
			if isinstance(v, str):
				parts.extend(("&" if parts else "", quote_plus(k), "=", quote_plus(unicode(v))))
				continue
			
			for s in v:
				parts.extend(("&" if parts else "", quote_plus(k), "=", quote_plus(unicode(s))))
		
		return "".join(parts)
	
	@qs.setter
	def qs(self, value):
		query = self._query
		
		if value:
			try:
				value = parse_qsl(unicode(value), strict_parsing=True)
			except ValueError:
				# Better to preserve than to explode; URLs with qs like `?foo` do exist.
				self._query = value  # This will make dictionary manipulation explode.
				return
		
		query.clear()
		
		for k, v in value:
			if k not in query:
				query[k] = v
				continue
			
			if not isinstance(query[k], list):
				query[k] = [query[k]]
			
			query[k].append(v)
	
	@property
	def relative(self):
		if self.scheme not in {None, '', 'http', 'https'}:
			return False
		
		return not (self.scheme and self.host and self._path and self._path.is_absolute())
	
	# Internal Methods
	
	def _compile(self):
		self._url = "".join((
				(self.scheme + "://") if self.scheme else ("//" if self.host else ""),
				quote_plus(self.user) if self.user else "",
				(":" + quote_plus(self.password)) if self.user and self.password else "",
				"@" if self.user else "",
				self.host or "",
				(":" + unicode(self.port)) if self.host and self.port else "",
				unicode(self._path),
				("?" + self.qs) if self._query else "",
				("#" + quote_plus(self.fragment)) if self.fragment else "",
			))
	
	def _decompile(self):
		result = urlsplit(self._url)
		
		for part in self.__parts__:
			if not hasattr(result, part): continue
			setattr(self, part, getattr(result, part))


class Link(String):
	"""A field capable of storing and richly accessing URI links, inclding absolute or relative URL.
	
	Example valid values:
	
		http://user:pass@host:port/path?query#fragment
		mailto:user@example.com
		urn:ISBN0-486-27557-4
		//example.com/protocol/relative
		/host/relative
		local/relative
		#fragment-only
	
	You can prevent relative links from being assignable by setting `absolute`, or restrict the allowed `protocols`
	(schemes) by defining them as a set of schemes, e.g. `{'http', 'https', 'mailto'}`.
	"""
	
	URI = URIString
	
	absolute = Attribute(default=False)  # Only allow absolute addressing.
	protocols = Attribute(default=None)  # Only allow the given protocols, e.g. {'http', 'https', 'mailto'}.
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		value = self.URI(value)
		
		if self.protocols and value.scheme not in self.protocols:
			raise ValueError("Link utilizes invaid scheme: " + value.scheme)
		
		if self.absolute and value.relative:
			raise ValueError("Link must be absolute.")
		
		return value.url
	
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return self.URI(value)
