# encoding: utf-8

"""Data model trait mix-in for tracking record publication and retraction."""

from ... import Document, Index, utcnow
from ...field import Date


class Published(Document):
	created = Date(default=utcnow, assign=True, write=False)
	modified = Date(default=utcnow, assign=True, write=False)
	published = Date(default=None)
	retracted = Date(default=None)
	
	_availability = Index('published', 'retracted')
	
	@property
	def is_published(self):
		now = utcnow()
		
		if self.published and self.published < now:
			return False
		
		if self.retracted and self.retracted > now:
			return False
		
		return True
