# encoding: utf-8

'''
from __future__ import unicode_literals

import pytest

from marrow.mongo import Document
from marrow.mongo.field import Reference
from marrow.mongo.trait import Derived

from common import FieldExam


class Concrete(Derived, Document):
	__collection__ = 'collection'
	
	foo = String()
	bar = String()


class TestReferenceField(FieldExam):
	__field__ = Reference
	__args__ = (Document, )
	
	def test_foreign(self, Sample):
		assert Sample.field._field.__foreign__ == 'objectId'
	
	def test_foreign_cast_document_fail(self, Sample):
		inst = Sample()
		doc = Document()
		
		with pytest.raises(ValueError):
			inst.field = doc
	
	def test_foreign_cast_document(self, Sample):
		inst = Sample()
		doc = Document()
		doc['_id'] = 27
		inst.field = doc
		assert inst['field'] == 27
'''
