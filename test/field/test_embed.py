# encoding: utf-8

'''
from __future__ import unicode_literals

from marrow.mongo import Document
from marrow.mongo.field import String, Embed
from marrow.mongo.trait import Derived

from common import FieldExam


class Concrete(Derived, Document):
	__collection__ = 'collection'
	
	foo = String()
	bar = String()


class TestSingularEmbedField(FieldExam):
	__field__ = Embed
	__args__ = (Document, )
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': {'foo': 27, 'bar': 42}})
		assert isinstance(inst.field, Document)
		assert inst.field['foo'] == 27
		assert inst.field['bar'] == 42
	
	def test_foreign_cast(self, Sample):
		inst = Sample(field={})
		assert isinstance(inst.field, Document)
'''
