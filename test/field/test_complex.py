# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta

import pytest
from bson import ObjectId as oid
from bson import DBRef
from bson.tz_util import utc

from marrow.mongo import Document
from marrow.mongo.core.field.complex import _HasKinds
from marrow.mongo.field import Array, Embed, PluginReference, Reference, String
from marrow.schema.compat import odict, unicode


class FieldExam(object):
	__args__ = ()
	__kw__ = {}
	
	@pytest.fixture()
	def Sample(self, request):
		class Sample(Document):
			field = self.__field__(*self.__args__, **self.__kw__)
		
		return Sample


class Concrete(Document):
	__collection__ = 'collection'
	
	foo = String()
	bar = String()


class TestHasKinds(object):
	def test_singular(self):
		inst = _HasKinds(kind=1)
		assert list(inst.kinds) == [1]
	
	def test_iterable(self):
		inst = _HasKinds(kind=(1, 2))
		assert list(inst.kinds) == [1, 2]
	
	def test_positional(self):
		inst = _HasKinds(1, 2)
		assert list(inst.kinds) == [1, 2]
	
	def test_reference(self):
		inst = _HasKinds(kind='Document')
		assert list(inst.kinds) == [Document]


class TestSingularArrayField(FieldExam):
	__field__ = Array
	__args__ = (Document, )
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': [{'foo': 27, 'bar': 42}]})
		assert isinstance(inst.field[0], Document)
		assert inst.field[0]['foo'] == 27
		assert inst.field[0]['bar'] == 42
	
	def test_foreign_cast(self, Sample):
		inst = Sample(field=[{}])
		assert isinstance(inst.field[0], Document)


class TestMultipleArrayField(FieldExam):
	__field__ = Array
	__args__ = (Document, Document)
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': [{'foo': 27, 'bar': 42}]})
		assert isinstance(inst.field[0], Document)
		assert inst.field[0]['foo'] == 27
		assert inst.field[0]['bar'] == 42
	
	def test_foreign_cast_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample(field=[{}])
	
	def test_foreign_reference(self, Sample):
		inst = Sample(field=[Document()])
		assert inst.field[0]['_cls'] == 'marrow.mongo.core.document:Document'


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


class TestMultipleEmbedField(FieldExam):
	__field__ = Embed
	__args__ = (Document, Document)
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': {'foo': 27, 'bar': 42}})
		assert isinstance(inst.field, Document)
		assert inst.field['foo'] == 27
		assert inst.field['bar'] == 42
	
	def test_foreign_cast_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample(field={})
	
	def test_foreign_reference(self, Sample):
		inst = Sample(field=Document())
		assert inst.field['_cls'] == 'marrow.mongo.core.document:Document'


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
	
	def test_foreign_cast_string_oid(self, Sample):
		inst = Sample()
		inst.field = '58329b3a927cc647e94153c9'
		assert inst['field'] == oid('58329b3a927cc647e94153c9')
	
	def test_foreign_cast_string_not_oid(self, Sample):
		inst = Sample()
		inst.field = '58329b3a927cz647e94153c9'
		assert inst['field'] == '58329b3a927cz647e94153c9'


class TestMultipleReferenceField(FieldExam):
	__field__ = Reference
	__args__ = (Document, Document)
	
	def test_foreign(self, Sample):
		assert Sample.field._field.__foreign__ == 'objectId'
	
	def test_foreign_cast_document_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample(Document())
	
	def test_foreign_cast_document(self, Sample):
		inst = Sample()
		doc = Document()
		doc['_id'] = 27
		inst.field = doc
		assert inst['field'] == 27
	
	def test_foreign_cast_string_oid(self, Sample):
		inst = Sample()
		with pytest.raises(ValueError):
			inst.field = '58329b3a927cc647e94153c9'
	
	def test_foreign_cast_string_not_oid(self, Sample):
		inst = Sample()
		with pytest.raises(ValueError):
			inst.field = '58329b3a927cz647e94153c9'


class TestConcreteReferenceField(FieldExam):
	__field__ = Reference
	__args__ = (Concrete, )
	__kw__ = dict(concrete=True)
	
	def test_foreign(self, Sample):
		assert Sample.field._field.__foreign__ == 'dbPointer'
	
	def test_foreign_cast_document(self, Sample):
		val = Concrete()
		val['_id'] = oid('58329b3a927cc647e94153c9')
		inst = Sample(val)
		assert isinstance(inst.field, DBRef)
	
	def test_foreign_cast_document_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample(Concrete())
	
	def test_foreign_cast_reference(self, Sample):
		inst = Sample('58329b3a927cc647e94153c9')
		assert isinstance(inst.field, DBRef)


class TestCachingReferenceField(FieldExam):
	__field__ = Reference
	__args__ = (Concrete, )
	__kw__ = dict(cache=('foo', ))
	
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
		assert inst.field['_cls'] == 'test_complex:Concrete'
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


class TestExplicitPluginReferenceField(FieldExam):
	__field__ = PluginReference
	
	def test_native_cast(self, Sample):
		inst = Sample.from_mongo({'field': 'marrow.mongo:Document'})
		assert inst.field is Document
	
	def test_foreign_cast(self, Sample):
		inst = Sample(Document)
		assert inst['field'] == 'marrow.mongo.core.document:Document'


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
