# encoding: utf-8

from __future__ import unicode_literals

from common import FieldExam
from marrow.mongo.core.field.path import _Path
from marrow.mongo.field import Path


class TestPathField(FieldExam):
	__field__ = Path
	
	def test_native_conversion(self, Sample):
		inst = Sample.from_mongo({'field': '/foo'})
		value = inst.field
		assert isinstance(value, _Path)
		assert str(value) == '/foo'
	
	def test_foreign_conversion(self, Sample):
		inst = Sample(_Path('/bar'))
		assert isinstance(inst['field'], str)
		assert inst['field'] == '/bar'
