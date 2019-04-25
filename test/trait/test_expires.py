from datetime import timedelta

import pytest

from marrow.mongo.trait import Expires
from marrow.mongo.util import utcnow


class TestExpires(object):
	class Sample(Expires):
		pass
	
	def test_index_presence(self):
		assert '_expires' in self.Sample.__indexes__
	
	def test_empty_repr(self):
		inst = self.Sample()
		assert repr(inst) == 'Sample()'
		assert inst.is_expired is None
	
	def test_integer_assignment(self):
		now = utcnow()
		inst = self.Sample(expires=0)
		assert inst.expires - now < timedelta(seconds=1)
		assert inst.is_expired
	
	def test_timedelta_assignment(self):
		now = utcnow()
		inst = self.Sample(expires=timedelta(days=1))
		assert timedelta(hours=23) < (inst.expires - now) < timedelta(hours=25)
	
	def test_explicit_date(self):
		then = utcnow() - timedelta(days=1)
		inst = self.Sample(expires=then)
		assert inst.expires == then
		assert inst.is_expired
	
	def test_deserialize_expired(self):
		now = utcnow()
		inst = self.Sample.from_mongo({'expires': now})
		assert inst is None
		
		inst = self.Sample.from_mongo({'expires': now + timedelta(hours=1)})
		assert isinstance(inst, self.Sample)
		assert not inst.is_expired
