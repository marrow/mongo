import pytest

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Reference, String
from marrow.mongo.trait import Collection


class Concrete(Collection):
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


class TestConcreteReferenceField(FieldExam):
	__field__ = Reference
	__args__ = (Document, )
	__kwargs__ = {'concrete': True}
	
	def test_concrete_reference(self, Sample):
		inst = Sample(field=Concrete(foo="a", bar="b"))
		
		assert inst.__data__['field'].collection == 'collection'
