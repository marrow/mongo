# encoding: utf-8

from __future__ import unicode_literals

import pytest
from bson import DBRef, ObjectId

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Reference, String


class Concrete(Document):
	__collection__ = 'collection'
	
	foo = String()
	bar = String()


class TestConcreteReferenceField(FieldExam):
	__field__ = Reference
	__args__ = (Concrete, )
	__kwargs__ = {'concrete': True}
	
	def test_foreign(self, Sample):
		assert Sample.field._field.__foreign__ == 'dbPointer'
	
	def test_foreign_cast_document(self, Sample):
		val = Concrete()
		val['_id'] = ObjectId('58329b3a927cc647e94153c9')
		inst = Sample(val)
		assert isinstance(inst.field, DBRef)
	
	def test_foreign_cast_document_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample(Concrete())
	
	def test_foreign_cast_reference(self, Sample):
		inst = Sample('58329b3a927cc647e94153c9')
		assert isinstance(inst.field, DBRef)

class TestConcreteAbstractReference(FieldExam):
	__field__ = Reference
	__kwargs__ = {'concrete': True}
	
	def test_unknown_abstract(self, Sample):
		with pytest.raises(ValueError):
			Sample('xyzzy')
