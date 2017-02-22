# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Array


class TestSingularArrayField(FieldExam):
	__field__ = Array
	__args__ = (Document, )
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': [{'foo': 27, 'bar': 42}]})
		assert isinstance(inst.field[0], Document)
		assert inst.field[0]['foo'] == 27
		assert inst.field[0]['bar'] == 42
