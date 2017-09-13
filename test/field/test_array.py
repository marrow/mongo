# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Array, Integer


class TestSingularArrayField(FieldExam):
	__field__ = Array
	__args__ = (Document, )
	__kwargs__ = {'assign': True}
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': [{'foo': 27, 'bar': 42}]})
		assert isinstance(inst.field[0], Document)
		assert inst.field[0]['foo'] == 27
		assert inst.field[0]['bar'] == 42
	
	def test_default_value(self, Sample):
		inst = Sample()
		inst.field.append(Document.from_mongo({'rng': 7}))
		assert isinstance(inst.field[0], Document)
		assert inst.field[0]['rng'] == 7


class TestArrayIssue43(FieldExam):
	__field__ = Array
	__args__ = (Integer(), )
	__kwargs__ = {'assign': True}
	
	def test_issue_43(self, Sample):
		filter = Sample.field != 1
		
		assert dict(filter) == {'field': {'$ne': 1}}
