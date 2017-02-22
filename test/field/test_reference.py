# encoding: utf-8

from __future__ import unicode_literals

import pytest

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Reference, String
from marrow.mongo.trait import Derived


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
	
	def test_oid_failure(self, Sample):
		inst = Sample(field='z' * 24)
		assert inst['field'] == 'z' * 24
