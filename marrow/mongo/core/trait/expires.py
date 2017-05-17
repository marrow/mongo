# encoding: utf-8

from ... import Document, Index, utcnow
from ...field import TTL


class Expires(Document):
	"""Record auto-expiry field with supporting TTL index and properties."""
	
	# ## Expiry Field Definition
	
	expires = TTL(default=None, write=False)  # The exact time the record should be considered "expired".
	
	# ## TTL Index Definition
	
	_expires = Index('expires', expire=0, sparse=True)
	
	# ## Accessor Properties
	
	@property
	def is_expired(self):
		"""Determine if this document has already expired.
		
		We need this because MongoDB TTL indexes are culled once per minute on an as-able basis, meaning records might
		be available for up to 60 seconds after their expiry time normally and that if there are many records to cull,
		may be present even longer.
		"""
		if not self.expires:
			return None  # None is falsy, preserving the "no, it's not expired" interpretation, but still flagging.
		
		return self.expires <= utcnow()
	
	# ## Cooperative Behaviours
	
	@classmethod
	def from_mongo(cls, data, expired=False, **kw):
		"""In the event a value that has technically already expired is loaded, swap it for None."""
		
		value = super(Expires, cls).from_mongo(data, **kw)
		
		if not expired and value.is_expired:
			return None
		
		return value
