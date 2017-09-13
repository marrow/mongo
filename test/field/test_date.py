# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime as _dt
from datetime import timedelta as _td
from datetime import tzinfo as _tzinfo

import pytest
from bson import ObjectId

from common import FieldExam
from marrow.mongo.field import Date
from marrow.mongo.util import utc

try:
	import pytz
except ImportError:
	pytz = False
finally:
	with_timezones = pytest.mark.skipif(not pytz, reason='timezone support (pytz) not installed')
	without_timezones = pytest.mark.skipif(pytz, reason='timezone support (pytz) installed')

try:
	import tzlocal
except ImportError:
	tzlocal = False
finally:
	with_tzlocal = pytest.mark.skipif(not tzlocal, reason='local timezone support (tzlocal) not installed')
	without_tzlocal = pytest.mark.skipif(tzlocal, reason='local timezone support (tzlocal) installed')


class TestDateField(FieldExam):
	__field__ = Date
	
	def test_date_like_oid(self, Sample):
		oid = ObjectId('586846800000000000000000')
		
		assert Sample(oid).field == _dt(2017, 1, 1, tzinfo=utc)
	
	def test_timezone_defaults(self, Sample):
		when = _dt(2001, 9, 1)
		instance = Sample(when)
		
		assert instance['field'].tzinfo == utc
		assert instance.field.tzinfo == utc
	
	def test_non_date_store(self, Sample):
		instance = Sample.from_mongo({'field': 27})
		
		assert instance.field == 27  # Pass-through unknown values.
	
	def test_timedelta_assignment(self, Sample):
		fuzz = _td(seconds=5)
		delta = _td(days=2, hours=12)
		now = _dt.utcnow()
		instance = Sample(delta)
		assert abs(instance.field.replace(tzinfo=None) - (now + delta)) < fuzz
	
	def test_document_assignment(self, Sample):
		now = _dt.utcnow().replace(microsecond=0)
		instance = Sample({'_id': ObjectId.from_datetime(now)})
		assert instance.field.replace(tzinfo=None) == now
	
	def test_invalid_assignment(self, Sample):
		instance = Sample()
		with pytest.raises(ValueError):
			instance.field = "Have you ever danced with the devil in the pale moonlight?"


class TestDateFieldExplicitNaive(FieldExam):
	__field__ = Date
	__kwargs__ = {'naive': 'America/Chicago'}
	
	@with_timezones
	def test_naive_explicit(self, Sample):
		tz = pytz.timezone('America/Chicago')
		when = _dt(1992, 1, 12)  # Prod. #3
		instance = Sample(when)
		assert tz.normalize(instance['field'].astimezone(tz)).replace(tzinfo=None) == when
	
	@without_timezones
	def test_naive_explicit_no_pytz(self, Sample):
		with pytest.raises(ValueError):
			Sample(_dt.now())


class TestDateFieldLocalNaive(FieldExam):
	__field__ = Date
	__kwargs__ = {'naive': 'local'}
	
	@with_tzlocal
	def test_naive_local(self, Sample):
		tz = tzlocal.get_localzone()
		when = _dt.now()  # Wherever you go, there you are.
		instance = Sample(when)
		assert tz.normalize(instance['field'].astimezone(tz)).replace(tzinfo=None) == when
	
	@without_tzlocal
	def test_naive_local_no_tzlocal(self, Sample):
		with pytest.raises(ValueError):
			Sample(_dt.now())


class TestDateFieldNativeNaive(FieldExam):
	__field__ = Date
	__kwargs__ = {'tz': 'naive'}
	
	def test_naive_native_simple(self, Sample):
		when = _dt.now()  # Wherever you go, there you are.
		instance = Sample(when)
		assert instance.field.tzinfo is None


class TestDateFieldBasicTzinfo(FieldExam):
	class TZ(_tzinfo):
		def utcoffset(self, dt):
			return _td(hours=-7)
		
		def tzname(self, dt):
			return 'Canada/Pacific'
		
		def dst(self, dt):
			return _td()
	
	__field__ = Date
	__kwargs__ = {'tz': TZ()}
	
	def test_basic_tzinfo_use(self, Sample):
		now = _dt(1902, 4, 24)
		instance = Sample(now)
		
		assert instance.field.tzinfo.tzname(instance.field) in ('PST', 'Canada/Pacific')
