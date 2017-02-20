# encoding: utf-8

"""Data model trait mix-in for tracking record publication and retraction."""

from datetime import timedelta

from ... import Document, Index, utcnow
from ...field import Date
from ...util import utcnow


class Published(Document):
	created = Date(default=utcnow, assign=True, write=False)
	modified = Date(default=None, write=False)
	published = Date(default=None)
	retracted = Date(default=None)
	
	_availability = Index('published', 'retracted')
	
	@classmethod
	def only_published(cls, at=None):
		"""Produce a query fragment suitable for selecting documents public.
		
		Now (no arguments), at a specific time (datetime argument), or relative to now (timedelta).
		"""
		
		if isinstance(at, timedelta):
			at = utcnow() + at
		else:
			at = at or utcnow()
		
		pub, ret = cls.published, cls.retracted
		
		publication = (-pub) | (pub == None) | (pub <= at)
		retraction = (-ret) | (ret == None) | (ret > at)
		
		return publication & retraction
	
	@property
	def is_published(self):
		now = utcnow()
		
		if self.published and self.published > now:
			return False
		
		if self.retracted and self.retracted < now:
			return False
		
		return True
