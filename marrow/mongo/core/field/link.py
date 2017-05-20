# encoding: utf-8

from collections import MutableMapping, OrderedDict
from pathlib import PurePosixPath

from .base import String
from ..compat import str, py2

try:
	from html import escape
	from urllib.parse import urlsplit, quote_plus, unquote_plus, parse_qsl
except ImportError:  # Adapt to Python 2 locations on legacy versions.
	from cgi import escape
	from urllib import urlsplit, quote_plus, unquote_plus, parse_qsl


class URLString(MutableMapping):
	"""An object representing a URL (absolute or relative) and its components.
	
	Acts as a mutable mapping for manipulation of query string arguments. If the query string is not URL
	"form encoded" attempts at mapping access or manipulation will fail with a ValueError. No effort is made to
	preserve original query string key order. Repeated keys will have lists as values.
	"""
	
	# Skip allocation of a dictionary per instance by pre-defining available slots.
	__slots__ = ('_url', 'scheme', 'user', 'password', 'host', 'port', '_path', '_query', 'fragment')
	__parts__ = {'scheme', 'user', 'password', 'host', 'port', 'path', 'query', 'fragment', 'hostname'}
	
	# Basic Protocols
	
	def __init__(self, url=None, **parts):
		if isinstance(url, URLString):
			url = url.url
		
		self._url = url  # If None, this will also handle setting defaults.
		
		if parts:  # If not given a base URL, defines a new URL, otherwise update the given URL.
			for part, value in parts.items():
				if part not in parts:
					raise TypeError("Unknown URL component: " + part)
				
				setattr(self, part, value)
	
	# String Protocols
	
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
				summary = escape(self.host + str(self.path)),
			)
	
	# Comparison Protocols
	
	def __eq__(self, other):
		return self.url == str(other)
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	# Mapping Protocols
	
	def __getitem__(self, name):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		return self._query[name]
	
	def __setitem__(self, name, value):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
		self._query[name] = value
	
	def __delitem__(self, name):
		if not isinstance(self._query, dict):
			raise ValueError("Query string is not manipulatable.")
		
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
			self._path = PurePosixPath(value)
		else:
			self._path = None
	
	@property
	def query(self):
		return self._query
	
	@query.setter
	def query(self, value):
		if isinstance(value, str):
			self.qs = value
			return
		
		self._query = dict(value)
	
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
		self.fragment = None
	
	@property
	def qs(self):
		if not self._query:
			return ""
		
		if isinstance(self._query, str):
			return self._query  # Handle "preserved" edge cases.
		
		parts = []
		
		for k, v in self._query.items():
			if isinstance(v, str):
				parts.extend(("&" if parts else "", quote_plus(k), "=", quote_plus(str(v))))
				continue
			
			for s in v:
				parts.extend(("&" if parts else "", quote_plus(k), "=", quote_plus(str(s))))
		
		return "".join(parts)
	
	@qs.setter
	def qs(self, value):
		query = self._query
		
		try:
			value = parse_qsl(str(value), strict_parsing=True)
		except ValueError:
			# Better to preserve than to explode; URLs with qs like `?foo` do exist.
			self.query = value  # This will make dictionary manipulation explode.
			return
		
		query.clear()
		
		for k, v in value:
			if k not in query:
				query[k] = v
				continue
			
			if not isinstance(query[k], list):
				query[k] = [query[k]]
			
			query[k].append(v)
	
	# Internal Methods
	
	def _compile(self):
		self._url = "".join((
				(self.scheme + "://") if self.scheme else ("//" if self.host else ""),
				quote_plus(self.user) if self.user else "",
				(":" + quote_plus(self.password)) if self.user and self.password else "",
				"@" if self.user else "",
				self.host or "",
				(":" + str(self.port)) if self.host and self.port else "",
				str(self._path),
				("?" + self.qs) if self._query else "",
				("#" + quote_plus(self.fragment)) if self.fragment else "",
			))
	
	def _decompile(self):
		result = urlsplit(self._url)
		
		for part in self.__parts__:
			if not hasattr(result, part): continue
			setattr(self, part, getattr(result, part))


class Link(String):
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return URLString(value).url
	
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return URLString(value)
