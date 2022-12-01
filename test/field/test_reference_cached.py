from collections import OrderedDict as odict

import pytest
from bson import ObjectId as oid

from common import FieldExam
from marrow.mongo import Document
from marrow.mongo.field import Reference, String
from marrow.mongo.trait import Derived


class Concrete(Derived, Document):
	__collection__ = 'collection'
	
	foo = String()
	bar = String()


class TestCachingReferenceField(FieldExam):
	__field__ = Reference
	__args__ = (Concrete,)
	__kwargs__ = dict(cache=('foo',))
	
	def test_foreign(self, Sample):
		assert Sample.field._field.__foreign__ == 'object'
	
	def test_foreign_cast_document(self, Sample):
		val = Concrete()
		val['_id'] = oid('58329b3a927cc647e94153c9')
		val.foo = 'foo'
		val.bar = 'bar'
		
		inst = Sample(field=val)
		
		assert isinstance(inst.field, odict)
		assert inst.field['_id'] == val['_id']
		assert inst.field['_cls'] == 'test_reference_cached:Concrete'
		assert inst.field['foo'] == val['foo']
	
	def test_foreign_cast_dict(self, Sample):
		val = {'_id': oid('58329b3a927cc647e94153c9'), 'foo': 'foo', 'bar': 'bar'}
		
		inst = Sample(field=val)
		
		assert isinstance(inst.field, odict)
		assert inst.field['_id'] == val['_id']
		assert '_cls' not in inst.field
		assert inst.field['foo'] == val['foo']
	
	def test_foreign_cast_oid(self, Sample):
		val = oid('58329b3a927cc647e94153c9')
		
		inst = Sample(field=val)
		
		assert isinstance(inst.field, odict)
		assert inst.field['_id'] == val
		assert '_cls' not in inst.field
		assert 'foo' not in inst.field
	
	def test_foreign_cast_string_oid(self, Sample):
		val = '58329b3a927cc647e94153c9'
		
		inst = Sample(field=val)
		
		assert isinstance(inst.field, odict)
		assert inst.field['_id'] == oid(val)
		assert '_cls' not in inst.field
		assert 'foo' not in inst.field
	
	def test_foreign_cast_document_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample(Concrete())
	
	def test_foreign_cast_dict_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample({})
	
	def test_foreign_cast_string_oid_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample('58329b3a927cc647e941x3c9')
	
	def test_foreign_cast_other_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample(object())
	
	def test_foreign_cast_numeric_fail(self):
		class Sample(Document):
			field = Reference(Concrete, cache=('foo.1', ))
		
		with pytest.raises(ValueError):
			Sample(oid('58329b3a927cc647e94153c9'))
	
	def test_foreign_cast_nested(self, Sample):
		class Ref(Document):
			field = Reference(Document, cache=('field.field', ))
		
		val = {'_id': oid('58329b3a927cc647e94153c9'), 'field': {'field': 27}}
		inst = Ref(val)
		
		assert inst.field['field']['field'] == 27
