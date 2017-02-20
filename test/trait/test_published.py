# encoding: utf-8

from __future__ import unicode_literals

from datetime import timedelta

import pytest

from marrow.mongo.trait import Published
from marrow.mongo.util import utcnow


class TestPublished(object):
	class Sample(Published):
		pass
	
	def test_creation_modification_init(self):
		now = utcnow()
		inst = self.Sample()
		
		assert abs(inst.created - now) < timedelta(seconds=1)
		assert abs(inst.modified - now) < timedelta(seconds=1)
	
	def test_bare_public(self):
		inst = self.Sample()
		
		assert inst.is_published
	
	def test_future_public(self):
		inst = self.Sample(published=utcnow() + timedelta(days=1))
		
		assert not inst.is_published
	
	def test_past_retraction(self):
		inst = self.Sample(retracted=utcnow() - timedelta(days=1))
		
		assert not inst.is_published
	
	def test_within_publication_period(self):
		inst = self.Sample(
				published = utcnow() - timedelta(days=1),
				retracted = utcnow() + timedelta(days=1)
			)
		
		assert inst.is_published
