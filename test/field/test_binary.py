# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo.field import Binary


class TestBinaryField(FieldExam):
	__field__ = Binary
	
	def test_conversion(self, Sample):
		inst = Sample(b'abc')
		assert isinstance(inst.__data__['field'], bytes)
		assert inst.field == b'abc'
