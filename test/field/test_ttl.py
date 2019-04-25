from datetime import datetime, timedelta

import pytest

from common import FieldExam
from marrow.mongo.field import TTL
from marrow.mongo.util import utcnow


class TestTTLField(FieldExam):
	__field__ = TTL
	
	def test_cast_timedelta(self, Sample):
		v = timedelta(days=7)
		r = (utcnow() + v)
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], datetime)
		assert inst.field == r
	
	def test_cast_datetime(self, Sample):
		v = utcnow()
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], datetime)
		assert inst.field is v
	
	def test_cast_integer(self, Sample):
		v = timedelta(days=7)
		r = (utcnow() + v)
		inst = Sample(7)
		
		assert isinstance(inst.__data__['field'], datetime)
		assert inst.field == r
	
	def test_cast_failure(self, Sample):
		with pytest.raises(ValueError):
			Sample('xyzzy')
