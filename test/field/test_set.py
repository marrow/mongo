# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo.field import Integer, Set


class TestSetField(FieldExam):
	__field__ = Set
	__args__ = (Integer(), )
	
	def test_cast(self, Sample):
		inst = Sample.from_mongo({'field': [1, 2, 3]})
		assert isinstance(inst.field, set)
	
	def test_cast_dup(self, Sample):
		inst = Sample.from_mongo({'field': [1, 2, 2, 3]})
		assert isinstance(inst.field, set)
		assert inst.field == {1, 2, 3}
