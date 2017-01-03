# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta

import pytest
from bson import ObjectId as oid
from bson.tz_util import utc

from marrow.mongo import Document
from marrow.mongo.field import TTL, Binary, Boolean, Date, ObjectId, Regex, String, Timestamp
from marrow.schema.compat import unicode


class FieldExam(object):
	@pytest.fixture()
	def Sample(self, request):
		class Sample(Document):
			field = self.__field__()
		
		return Sample


class TestStringField(FieldExam):
	__field__ = String
	
	def test_strip_basic(self, Sample):
		Sample.field.strip = True
		
		inst = Sample('\tTest\n   ')
		assert inst.field == 'Test'
	
	def test_strip_specific(self, Sample):
		Sample.field.strip = '* '
		
		inst = Sample('** Test *')
		assert inst.field == 'Test'
	
	def test_case_lower(self, Sample):
		Sample.field.case = 'lower'
		
		inst = Sample('Test')
		assert inst.field == 'test'
	
	def test_case_upper(self, Sample):
		Sample.field.case = 'upper'
		
		inst = Sample('Test')
		assert inst.field == 'TEST'
	
	def test_case_title(self, Sample):
		Sample.field.case = 'title'
		
		inst = Sample('Test words')
		assert inst.field == 'Test Words'


class TestBinaryField(FieldExam):
	__field__ = Binary
	
	def test_conversion(self, Sample):
		inst = Sample(b'abc')
		assert isinstance(inst.__data__['field'], bytes)
		assert inst.field == b'abc'


class TestObjectIdField(FieldExam):
	__field__ = ObjectId
	
	def test_id_default(self):
		class Sample(Document):
			id = ObjectId('_id')
		
		assert isinstance(Sample().id, oid)
	
	def test_cast_string(self, Sample):
		inst = Sample('5832223f927cc6c1a10609f7')
		
		assert isinstance(inst.__data__['field'], oid)
		assert unicode(inst.field) == '5832223f927cc6c1a10609f7'
	
	def test_cast_oid(self, Sample):
		v = oid()
		inst = Sample(v)
		
		assert inst.__data__['field'] is v
	
	def test_cast_datetime(self, Sample):
		v = datetime.utcnow().replace(microsecond=0, tzinfo=utc)
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], oid)
		assert inst.field.generation_time == v
	
	def test_cast_timedelta(self, Sample):
		v = -timedelta(days=7)
		r = (datetime.utcnow() + v).replace(microsecond=0, tzinfo=utc)
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], oid)
		assert inst.field.generation_time == r
	
	def test_cast_document(self, Sample):
		v = {'_id': oid()}
		inst = Sample(v)
		assert inst.field == v['_id']


class TestBooleanField(FieldExam):
	__field__ = Boolean
	
	def test_cast_boolean(self, Sample):
		inst = Sample(True)
		assert inst.field is True
		
		inst = Sample(False)
		assert inst.field is False
	
	def test_cast_strings(self, Sample):
		inst = Sample("true")
		assert inst.field is True
		
		inst = Sample("false")
		assert inst.field is False
	
	def test_cast_none(self, Sample):
		inst = Sample(None)
		assert inst.field is None
	
	def test_cast_other(self, Sample):
		inst = Sample(1)
		assert inst.field is True
	
	def test_cast_failure(self, Sample):
		with pytest.raises(ValueError):
			Sample('hehehe')


class TestDateField(FieldExam):
	__field__ = Date


class TestTTLField(FieldExam):
	__field__ = TTL
	
	def test_cast_timedelta(self, Sample):
		v = timedelta(days=7)
		r = (datetime.utcnow() + v).replace(microsecond=0, tzinfo=utc)
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], datetime)
		assert inst.field.replace(microsecond=0, tzinfo=utc) == r
	
	def test_cast_datetime(self, Sample):
		v = datetime.utcnow().replace(microsecond=0, tzinfo=utc)
		inst = Sample(v)
		
		assert isinstance(inst.__data__['field'], datetime)
		assert inst.field is v
	
	def test_cast_integer(self, Sample):
		v = timedelta(days=7)
		r = (datetime.utcnow() + v).replace(microsecond=0, tzinfo=utc)
		inst = Sample(7)
		
		assert isinstance(inst.__data__['field'], datetime)
		assert inst.field.replace(microsecond=0, tzinfo=utc) == r
	
	def test_cast_failure(self, Sample):
		with pytest.raises(ValueError):
			Sample('xyzzy')


class RegexField(FieldExam):
	__field__ = Regex


class TestTimestampField(FieldExam):
	__field__ = Timestamp
