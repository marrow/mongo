# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta
from decimal import Decimal as dec

import pytest
from bson import ObjectId as oid
from bson.decimal128 import Decimal128
from bson.tz_util import utc

from marrow.mongo import Document
from marrow.mongo.field import Decimal, Double, Integer, Long, Number
from marrow.schema.compat import unicode


class FieldExam(object):
	@pytest.fixture()
	def Sample(self, request):
		class Sample(Document):
			field = self.__field__()
		
		return Sample


class TestNumberField(FieldExam):
	__field__ = Number
	
	def test_passthrough(self, Sample):
		inst = Sample()
		inst.field = 42.1
		assert inst.field == 42.1
	
	def test_integer(self, Sample):
		result = Sample('27').field
		assert isinstance(result, int)
		assert result == 27
	
	def test_float(self, Sample):
		result = Sample('27.2').field
		assert isinstance(result, float)
		assert result == 27.2
	
	def test_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample(object())


class TestDoubleField(FieldExam):
	__field__ = Double
	
	def test_float(self, Sample):
		result = Sample(27.2).field
		assert isinstance(result, float)
		assert result == 27.2
	
	def test_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample(object())


class TestIntegerField(FieldExam):
	__field__ = Integer
	
	def test_integer(self, Sample):
		result = Sample(27).field
		assert isinstance(result, int)
		assert result == 27
	
	def test_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample(object())


class TestLongField(FieldExam):
	__field__ = Long
	
	def test_biginteger(self, Sample):
		result = Sample(272787482374844672646272463).field
		assert result == 272787482374844672646272463


class TestDecimalField(FieldExam):
	__field__ = Decimal
	
	def test_decimal(self, Sample):
		v = dec('3.141592')
		result = Sample(v)
		assert isinstance(result['field'], Decimal128)
		assert result['field'] == Decimal128('3.141592')
		assert result.field == v
	
	def test_decimal_cast_up(self, Sample):
		result = Sample.from_mongo({'field': 27.4})
		v = result.field
		assert isinstance(v, dec)
		assert float(v) == 27.4
	
	def test_decimal_from_number(self, Sample):
		result = Sample(27)
		assert isinstance(result['field'], Decimal128)
		assert result['field'] == Decimal128('27')
		assert int(result.field) == 27
