from datetime import timedelta

from bson import ObjectId as oid

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import ObjectId
from marrow.mongo.util import utcnow


class TestObjectIdField(FieldExam):
	__field__ = ObjectId
	
	def test_id_default(self):
		class Sample(Document):
			id = ObjectId('_id')
		
		assert isinstance(Sample().id, oid)
	
	def test_cast_string(self, Sample):
		inst = Sample('5832223f927cc6c1a10609f7')
		
		assert isinstance(inst.__data__['field'], oid)
		assert str(inst.field) == '5832223f927cc6c1a10609f7'
	
	def test_cast_oid(self, Sample):
		v = oid()
		inst = Sample(v)
		
		assert inst.__data__['field'] is v
	
	def test_cast_datetime(self, Sample):
		v = utcnow()
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], oid)
		assert inst.field.generation_time == v
	
	def test_cast_timedelta(self, Sample):
		v = -timedelta(days=7)
		r = (utcnow() + v)
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], oid)
		assert inst.field.generation_time == r
	
	def test_cast_document(self, Sample):
		v = {'_id': oid()}
		inst = Sample(v)
		assert inst.field == v['_id']
