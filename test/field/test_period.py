# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta

from common import FieldExam
from marrow.mongo.field import Period


class TestHourPeriodField(FieldExam):
	__field__ = Period
	__kwargs__ = {'hours': 1}
	
	def test_delta(self, Sample):
		assert Sample.field.delta == timedelta(hours=1)
	
	def test_exact(self, Sample):
		expect = dt = datetime(2017, 1, 1, 0, 0, 0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
		
		expect = dt = datetime(2017, 1, 1, 1, 5, 0)
		assert Sample(dt).field.replace(tzinfo=None) != expect
		
		expect = dt = datetime(2017, 1, 1, 2, 0, 0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_near(self, Sample):
		dt = datetime(2017, 1, 1, 1, 2, 3)
		expect = dt.replace(minute=0, second=0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_before(self, Sample):
		dt = datetime(2017, 1, 1, 2, 59, 59)
		expect = dt.replace(minute=0, second=0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_step(self, Sample):
		dt = datetime(2017, 1, 1, 3, 0, 0)
		period = Sample.field.delta
		expect = dt.replace(hour=4)
		snapped = Sample(dt).field.replace(tzinfo=None)
		
		assert snapped + period == expect


class TestMinutePeriodField(FieldExam):
	__field__ = Period
	__kwargs__ = {'minutes': 10}
	
	def test_delta(self, Sample):
		assert Sample.field.delta == timedelta(minutes=10)
	
	def test_exact(self, Sample):
		expect = dt = datetime(2017, 1, 1, 0, 0, 0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
		
		expect = dt = datetime(2017, 1, 1, 0, 10, 30)
		assert Sample(dt).field.replace(tzinfo=None) != expect
		
		expect = dt = datetime(2017, 1, 1, 0, 20, 0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_near(self, Sample):
		dt = datetime(2017, 1, 1, 1, 2, 3)
		expect = dt.replace(minute=0, second=0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_before(self, Sample):
		dt = datetime(2017, 1, 1, 2, 59, 59)
		expect = dt.replace(minute=50, second=0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_step(self, Sample):
		dt = datetime(2017, 1, 1, 3, 0, 0)
		period = Sample.field.delta
		expect = dt.replace(minute=10)
		snapped = Sample(dt).field.replace(tzinfo=None)
		
		assert snapped + period == expect


class TestSecondPeriodField(FieldExam):
	__field__ = Period
	__kwargs__ = {'seconds': 15}
	
	def test_delta(self, Sample):
		assert Sample.field.delta == timedelta(seconds=15)
	
	def test_exact(self, Sample):
		expect = dt = datetime(2017, 1, 1, 0, 0, 0)
		assert Sample(dt).field.replace(tzinfo=None) == expect
		
		expect = dt = datetime(2017, 1, 1, 0, 0, 25)
		assert Sample(dt).field.replace(tzinfo=None) != expect
		
		expect = dt = datetime(2017, 1, 1, 0, 0, 30)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_near(self, Sample):
		dt = datetime(2017, 1, 1, 1, 0, 16)
		expect = dt.replace(second=15)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_before(self, Sample):
		dt = datetime(2017, 1, 1, 2, 59, 59)
		expect = dt.replace(second=45)
		assert Sample(dt).field.replace(tzinfo=None) == expect
	
	def test_step(self, Sample):
		dt = datetime(2017, 1, 1, 3, 0, 0)
		period = Sample.field.delta
		expect = dt.replace(second=15)
		snapped = Sample(dt).field.replace(tzinfo=None)
		
		assert snapped + period == expect
