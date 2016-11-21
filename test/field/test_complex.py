# encoding: utf-8

from __future__ import unicode_literals

import pytest
from datetime import datetime, timedelta
from bson import ObjectId as oid
from bson.tz_util import utc

from marrow.mongo import Document
from marrow.mongo.core.field.complex import _HasKinds
from marrow.mongo.field import Array, Embed, Reference, PluginReference
from marrow.mongo.util.compat import unicode


class FieldExam(object):
	__args__ = ()
	__kw__ = {}
	
	@pytest.fixture()
	def Sample(self, request):
		class Sample(Document):
			field = self.__field__(*self.__args__, **self.__kw__)
		
		return Sample


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


class TestReferneceField(FieldExam):
	__field__ = Reference
	__args__ = (Document, )
	
	def test_native_cast(self, Sample):
		pass
	
	def test_foreign_cast(self, Sample):
		pass


class TestPluginReferenceField(FieldExam):
	__field__ = PluginReference
	__args__ = ('marrow.mongo.document', )
	
	def test_native_cast(self, Sample):
		pass
	
	def test_foreign_cast(self, Sample):
		pass
