from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import PluginReference


class TestExplicitPluginReferenceField(FieldExam):
	__field__ = PluginReference
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': 'marrow.mongo:Document'})
		assert inst.field is Document
	
	def test_foreign_cast(self, Sample):
		inst = Sample(Document)
		assert inst['field'] == 'marrow.mongo.core.document:Document'
