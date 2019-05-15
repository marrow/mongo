from datetime import timedelta

import pytest

from marrow.mongo.trait import Published
from marrow.mongo.util import utcnow


class TestPublished:
	class Sample(Published):
		pass
	
	def test_creation_modification_init(self):
		now = utcnow()
		inst = self.Sample()
		
		assert abs(inst.created - now) < timedelta(seconds=1)
		assert inst.modified is None
	
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
	
	def test_query_exact(self):
		now = utcnow()
		
		query = self.Sample.only_published(now)
		
		assert len(query) == 1
		assert '$and' in query
		assert len(query['$and']) == 2
		assert '$or' in query['$and'][0]
		assert '$or' in query['$and'][1]
		assert query['$and'][1]['$or'][2]['published']['$lte'] == query['$and'][0]['$or'][2]['retracted']['$gt'] == now
	
	def test_query_delta(self):
		when = utcnow() + timedelta(days=1)
		
		query = self.Sample.only_published(timedelta(days=1))
		
		assert len(query) == 1
		assert '$and' in query
		assert len(query['$and']) == 2
		assert '$or' in query['$and'][0]
		assert '$or' in query['$and'][1]
		assert query['$and'][1]['$or'][2]['published']['$lte'] == query['$and'][0]['$or'][2]['retracted']['$gt']
		
		v = query['$and'][1]['$or'][2]['published']['$lte']
		assert abs(when - v) < timedelta(minutes=1)
