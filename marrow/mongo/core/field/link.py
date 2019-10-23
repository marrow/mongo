from typing import Optional, Sequence

from uri import URI

from .string import String
from ....schema import Attribute


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
	
	URI = __annotation__ = URI
	
	absolute: bool = Attribute(default=False)  # Only allow absolute addressing.
	protocols: Optional[Sequence[str]] = Attribute(default=None)  # Only allow the given protocols,
			# e.g. {'http', 'https', 'mailto'}.
	
	def to_foreign(self, obj, name:str, value) -> str:  # pylint:disable=unused-argument
		value = self.URI(value)
		
		if self.protocols and str(value.scheme) not in self.protocols:
			raise ValueError("Link utilizes invaid scheme: " + repr(value.scheme))
		
		if self.absolute and value.relative:
			raise ValueError("Link must be absolute.")
		
		return str(value)
	
	def to_native(self, obj, name:str, value) -> URI:  # pylint:disable=unused-argument
		return self.URI(value)
