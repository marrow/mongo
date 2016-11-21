# encoding: utf-8

from __future__ import unicode_literals

import pytest
from datetime import datetime, timedelta
from bson import ObjectId as oid
from bson.tz_util import utc

from marrow.mongo import Document
from marrow.mongo.field import Number, Double, Integer, Long
from marrow.mongo.util.compat import unicode


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
