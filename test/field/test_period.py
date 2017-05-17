# encoding: utf-8

from __future__ import unicode_literals

from datetime import timedelta

from common import FieldExam
from marrow.mongo.field import Period


class TestHourPeriodField(FieldExam):
	__field__ = Period
	__kwargs__ = {'hours': 1}
	
	def test_delta(self, Sample):
		assert Sample.field.delta == timedelta(hours=1)


class TestMinutePeriodField(FieldExam):
	__field__ = Period
	__kwargs__ = {'minutes': 10}
	
	def test_delta(self, Sample):
		assert Sample.field.delta == timedelta(minutes=10)


class TestSecondPeriodField(FieldExam):
	__field__ = Period
	__kwargs__ = {'seconds': 15}
	
	def test_delta(self, Sample):
		assert Sample.field.delta == timedelta(seconds=15)
