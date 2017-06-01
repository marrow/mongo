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
	from urllib.parse import urljoin, urlsplit, quote_plus, unquote_plus, parse_qsl
except ImportError:  # Adapt to locations on legacy versions.
	from urlparse import urljoin, urlsplit, parse_qsl
	from urllib import quote_plus, unquote_plus

try:
	from pathlib import PurePosixPath as _Path
except ImportError:
	from pathlib2 import PurePosixPath as _Path


class URIString(MutableMapping):
	"""An object representing a URI (absolute or relative) and its components.
	
	Acts as a mutable mapping for manipulation of query string arguments. If the query string is not URL
	"form encoded" attempts at mapping access or manipulation will fail with a ValueError. No effort is made to
	preserve original query string key order. Repeated keys will have lists as values.
	"""
	
	# Skip allocation of a dictionary per instance by pre-defining available slots.
	__slots__ = ('_uri', 'scheme', 'user', 'password', 'host', 'port', '_path', '_query', 'fragment')
	__parts__ = {'scheme', 'user', 'password', 'host', 'port', 'path', 'query', 'fragment', 'username', 'hostname'}
	
	# Basic Protocols
	
	def __init__(self, _uri=None, **parts):
		"""Initialize a new URI from a passed in string or named parts.
		
		If both a base URI and parts are supplied than the parts will override those present in the URI.
		"""
		
		self._query = {}
		
		if hasattr(_uri, '__link__'):  # We utilize a custom object protocol to retrieve links to things.
			_uri = _uri.__link__
			
			# To allow for simpler cases, this attribute does not need to be callable.
			if callable(_uri): _uri = _uri()
		
		self.url = _uri  # If None, this will also handle setting defaults.
		
		if parts:  # If not given a base URI, defines a new URI, otherwise update the given URI.
			for part, value in parts.items():
				if part not in self.__parts__:
					raise TypeError("Unknown URI component: " + part)
				
				setattr(self, part, value)
	
	# String Protocols
	
	def __repr__(self):
		"""Return a "safe" programmers' representation that omits passwords."""
		
		return "URI('{0}')".format(self._compile(True))
	
	def __str__(self):
		"""Return the Unicode text representation of this URI, including passwords."""
		
		return self.url
	
	def __bytes__(self):
		"""Return the binary string representation of this URI, including passwords."""
		
		return self.url.encode('utf-8')
	
	if py2:  # Adapt to Python 2 semantics on legacy versions.
		__unicode__ = __str__
		__str__ = __bytes__
	
	def __html__(self):
		"""Return an HTML representation of this link.
		
		A link to http://example.com/foo/bar will result in:
		
			<a href="http://example.com/foo/bar">example.com/foo/bar</a>
		"""
		
		return '<a href="{address}">{summary}</a>'.format(
				address = escape(self.url),
				summary = escape(self.host + unicode(self.path)),
			)
	
	# Comparison Protocols
	
	def __eq__(self, other):
		"""Compare this URI against another value."""
		
		if not isinstance(other, self.__class__):
			other = self.__class__(other)
		
		# Because things like query string argument order may differ, but still be equivalent...
		for part in self.__parts__:
			if not getattr(self, part, None) == getattr(other, part, None):
				return False
		
		return True
	
	def __ne__(self, other):
		"""Inverse comparison support."""
		
		return not self == other
	
	# Mapping Protocols
	
	def __getitem__(self, name):
		"""Shortcut for retrieval of a query string argument."""
		
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		return self._query[name]
	
	def __setitem__(self, name, value):
		"""Shortcut for (re)assignment of query string arguments."""
		
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		self._uri = None  # Invalidate the cached string.
		self._query[name] = unicode(value)
	
	def __delitem__(self, name):
		"""Shortcut for removal of a query string argument."""
		
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		self._uri = None  # Invalidate the cached string.
		del self._query[name]
	
	def __iter__(self):
		"""Retrieve the query string argument names."""
		
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		return iter(self._query)
	
	def __bool__(self):
		"""Truthyness comparison."""
		
		return bool(self._uri)
	
	if py2:
		__nonzero__ = __bool__
	
	def __len__(self):
		"""Determine the number of query string arguments."""
		
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		return len(self._query)
	
	# Accessor Properties
	
	@property
	def username(self):
		"""Alias for compatibility with urlsplit results."""
		
		return self.user
	
	@username.setter
	def username(self, value):
		"""Alias for compatibility with urlsplit results."""
		
		self.user = value
	
	@property
	def hostname(self):
		"""Alias for compatibility with urlsplit results."""
		
		return self.host
	
	@hostname.setter
	def hostname(self, value):
		"""Alias for compatibility with urlsplit results."""
		
		self.host = value
	
	@property
	def path(self):
		"""The path referenced by this URI."""
		
		return self._path
		
	@path.setter
	def path(self, value):
		"""Cast path assignments to our native path representation."""
		
		if value:
			self._path = _Path(value)
		else:
			self._path = None
	
	@property
	def query(self):
		"""Retrieve the "query string arguments" for this URI."""
		
		return self._query
	
	@query.setter
	def query(self, value):
		"""Assign query string arguments to this URI."""
		
		if isinstance(value, unicode):
			self.qs = value
			return
		
		self._query = {k: unicode(v) for k, v in dict(value).items()}
	
	@property
	def url(self):
		"""Retrieve the "compiled" URL."""
		
		if not self._uri:
			self._uri = self._compile()
		
		return self._uri
	
	@url.setter
	def url(self, value):
		"""Assign and replace the entire URI with a new URL."""
		
		if value:
			self._decompile(unicode(value))
			return
		
		self._uri = None
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
		"""Retrieve the query string as a string, not a mapping, while preserving unprocessable values."""
		
		if not self._query:
			return ""
		
		if isinstance(self._query, unicode):
			return self._query  # Handle "preserved" edge cases.
		
		parts = []
		
		for k, v in self._query.items():
			if isinstance(v, unicode):
				parts.extend(("&" if parts else "", quote_plus(k), "=", quote_plus(unicode(v))))
				continue
			
			for s in v:
				parts.extend(("&" if parts else "", quote_plus(k), "=", quote_plus(unicode(s))))
		
		return "".join(parts)
	
	@qs.setter
	def qs(self, value):
		"""Assign a new query string as a string, not a mapping, while preserving unprocessable values."""
		
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
		"""Identify if this URI is relative to some "current context".
		
		For example, if the protocol is missing, it's protocol-relative. If the host is missing, it's host-relative, etc.
		"""
		
		if self.scheme not in {None, '', 'http', 'https'}:
			return False
		
		return not (self.scheme and self.host and self._path and self._path.is_absolute())
	
	def resolve(self, uri=None, **parts):
		"""Attempt to resolve a new URI given an updated URI or URIString, partial or complete."""
		
		if uri:
			result = URIString(urljoin(unicode(self), unicode(uri)))
		else:
			result = URIString(self)
		
		for part, value in parts.items():
			if part not in self.__parts__:
				raise TypeError("Unknown URI component: " + part)
			
			setattr(result, part, value)
		
		return result
	
	# Internal Methods
	
	def _compile(self, safe=False):
		"""Compile the parts of a URI down into a string representation."""
		
		return "".join((
				(self.scheme + "://") if self.scheme else ("//" if self.host else ""),
				quote_plus(self.user) if self.user else "",
				(":" + ("" if safe else quote_plus(self.password))) if self.user and self.password else "",
				"@" if self.user else "",
				self.host or "",
				(":" + unicode(self.port)) if self.host and self.port else "",
				unicode(self._path),
				("?" + self.qs) if self._query else "",
				("#" + quote_plus(self.fragment)) if self.fragment else "",
			))
	
	def _decompile(self, value):
		"""Store the original and process parts from a URI string."""
		
		self._uri = value
		result = urlsplit(value)
		
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
