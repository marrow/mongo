import pytest

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import PluginReference


class TestNamespacedPluginReferenceField(FieldExam):
	__field__ = PluginReference
	__args__ = ('marrow.mongo.document', )
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': 'Document'})
		assert inst.field is Document
	
	def test_foreign_object(self, Sample):
		inst = Sample(Document)
		assert inst['field'] == 'Document'
		assert inst.field is Document
	
	def test_foreign_string(self, Sample):
		inst = Sample('Document')
		assert inst['field'] == 'Document'
		assert inst.field is Document
	
	def test_foreign_fail_bad_reference(self, Sample):
		with pytest.raises(ValueError):
			Sample('UnknownDocumentTypeForRealsXYZZY')
	
	def test_foreign_fail_explicit(self, Sample):
		with pytest.raises(ValueError):
			Sample('marrow.mongo:Field')
	
	def test_foreign_fail_object(self, Sample):
		with pytest.raises(ValueError):
			Sample(object)


class TestNamespaceMappedPluginReferenceField(FieldExam):
	__field__ = PluginReference
	__args__ = ('marrow.mongo.document', )
	__kwargs__ = {'mapping': {'Bob': 'Document'}}
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': 'Bob'})
		assert inst.field is Document
