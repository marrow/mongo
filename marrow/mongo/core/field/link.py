# encoding: utf-8

from __future__ import unicode_literals

from uri import URI

from .string import String
from ....schema import Attribute
from ....schema.compat import unicode


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
	
	URI = URI
	
	absolute = Attribute(default=False)  # Only allow absolute addressing.
	protocols = Attribute(default=None)  # Only allow the given protocols, e.g. {'http', 'https', 'mailto'}.
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		value = self.URI(value)
		
		if self.protocols and unicode(value.scheme) not in self.protocols:
			raise ValueError("Link utilizes invaid scheme: " + repr(value.scheme))
		
		if self.absolute and value.relative:
			raise ValueError("Link must be absolute.")
		
		return unicode(value)
	
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return self.URI(value)
