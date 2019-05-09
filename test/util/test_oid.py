"""General tests, and conformance tests for our ObjectID reimplementation."""

from datetime import datetime, timedelta
from os import getpid
from pickle import dumps, loads

from bson import BSON
from bson.tz_util import utc
from pytest import mark, param, raises

from marrow.mongo import ObjectID
from marrow.mongo.util.oid import HWID
from marrow.schema.testing import ValidationTest, pytest_generate_tests
from test_date import with_timezones

try:
	from hashlib import md5
except ImportError:
	md5 = None

try:
	import fnv
except ImportError:
	fnv = None

try:
	from pytz import timezone
except ImportError:
	pass


class AnyObjectID:
	def __eq__(self, other):
		return isinstance(other, ObjectID)

anyoid = AnyObjectID()


class TestObjectID(ValidationTest):
	"""Tests inspired by / borrowed from PyMongo itself to ensure conformance."""
	
	validator = ObjectID
	binary = True
	
	valid = (
			(None, anyoid),
			('', anyoid),
			"123456789012345678901234",  # Textual hex-encoded string.
			# XXX: The following two differ from bson.ObjectId by permitting comparison between ObjectID and bytes.
			b"\x12\x34\x56\x78\x90\x12" * 2,  # Binary string.
			b"123456789012",  # This is also a valid binary string.
			(datetime(2017, 1, 1), "586846800000000000000000"),
			(datetime(2017, 1, 1, tzinfo=utc), "586846800000000000000000"),
		)
	
	invalid = (
			(27, TypeError),  # Integers are bogus.
			(42.0, TypeError),  # Floats doubly so.  (See what I did there?)
			({"test": 27}, TypeError),  # Dictionary is a nope.
			(["gesundheit"], TypeError),  # Lists are right out.
			({"wat"}, TypeError),  # This set is bereft of life.
			
			# XXX: Differs from bson.ObjectId: an empty string value is treated as None.
			# ('', ValueError),  # It's a string, but not a useful one.
			('hello', ValueError),  # Not even close.
			('12345678901', ValueError),  # Too short.
			('1234567890123', ValueError),  # Too long.
			('abcdefghijkl', ValueError),  # It's a string, but not hex.
			(b"123456789012345678901234", ValueError),  # XXX: Differs from bson.ObjectId!
			('123456789012123456789G12', ValueError),
			(b'123456789012123456789G12', ValueError),
		)
	
	def test_valid_values(self, valid):
		# Overridden to include is_valid testing.
		ValidationTest.test_valid_values(self, valid)
		
		assert self.validator.is_valid(valid[0] if isinstance(valid, tuple) else valid)
	
	def test_invalid_values(self, invalid):
		# Overridden because in our case, we also vary on exception class.
		assert not self.validator.is_valid(invalid[0])
		
		with raises(invalid[1]):
			self.validator(invalid[0])
	
	def test_coss_string_equality(self):
		assert ObjectID("123456789012123456789012") == ObjectID(b"\x12\x34\x56\x78\x90\x12\x12\x34\x56\x78\x90\x12")
	
	def test_identity_equality_comparisons(self):
		assert ObjectID(b"123456789012") == ObjectID(b"123456789012")
		
		a = ObjectID()
		b = ObjectID(a)
		
		assert a is not b
		assert a == b
		assert a == str(b)
		assert a == bytes(b)  # XXX: Differs from bson.ObjectId!
		# In the above case, we treat ObjectID as a transparent binary value, equivalent to its binary encoded form.
		
		assert ObjectID() != ObjectID()
		assert not (ObjectID(b"123456789012") != ObjectID("313233343536373839303132"))
		assert not (a != b)  # Explicit inequality comparison.
		
		assert a == a.binary == ObjectID(a.binary)
		assert a != 27
		
		with raises(TypeError):
			assert a < 27
		
		with raises(TypeError):
			assert a > 27
		
		with raises(TypeError):
			assert a <= 27
		
		with raises(TypeError):
			assert a >= 27
		
		assert ObjectID() > a
		assert a < ObjectID()
		
		assert ObjectID() >= a
		assert a <= ObjectID()
	
	def test_repr(self):
		oid = ObjectID('5cd33f61f761ee5819f110a5')
		assert repr(oid) == "ObjectID('5cd33f61f761ee5819f110a5', generated='2019-05-08T20:43:13+00:00')"
		
		oid = ObjectID('1234567890abcdef12345678')
		assert repr(oid) == "ObjectID('1234567890abcdef12345678', generated='1979-09-05T22:51:36+00:00')"
		
		oid = ObjectID(b'123456789012')
		assert repr(oid) == "ObjectID('313233343536373839303132', generated='1996-02-26T22:24:52+00:00')"
		
		oid = ObjectID('1234567890abcdef12345678')
		assert oid.binary == b'\x124Vx\x90\xab\xcd\xef\x124Vx'
		assert repr(oid) == "ObjectID('1234567890abcdef12345678', generated='1979-09-05T22:51:36+00:00')"
		
		oid = ObjectID(b'\x124Vx\x90\xab\xcd\xef\x124Vx')
		assert str(oid) == '1234567890abcdef12345678'
		assert repr(oid) == "ObjectID('1234567890abcdef12345678', generated='1979-09-05T22:51:36+00:00')"
	
	def test_times(self):
		# Note, compared to PyMongo's generation time tests, we don't need to worry about stripping tzinfo.
		# We do timezone support properly; it's all UTC.
		# Incidentally, the repr tests cover timestamp interpretation, too.
		
		now = datetime.utcnow().replace(tzinfo=utc)
		
		dt = ObjectID().generation_time
		ts = ObjectID().time
		ft = ObjectID(timedelta(seconds=5)).time
		
		assert dt == ts  # These must be synonyms for each-other.
		assert (dt - now).total_seconds() < 1
		assert (ts - now).total_seconds() < 1
		assert 4 < (ft - now).total_seconds() < 6
	
	@mark.parametrize("protocol", [0, 1, 2, -1])
	def test_pickling(self, protocol):
		oid = ObjectID()
		pickle = dumps(oid, protocol=protocol)
		assert oid == loads(pickle)
	
	@mark.parametrize("scheme", [
			'random',
			'modern',
			param('legacy', marks=[mark.xfail(reason='FIPS mode enabled')] if md5 is None else []),
			param('fips', marks=[mark.xfail(reason='FIPS mode not enabled')] if fnv is None else []),
			param('unknown', marks=[mark.xfail()]),
			'custom',
			b'12345',
		])
	def test_hwid(self, scheme):
		HWID['custom'] = b'CAFFE'
		
		oid = ObjectID(hwid=scheme)
		
		if scheme in ('random', 'modern', 'custom'):
			assert oid.hwid in HWID.values()
		
		elif scheme in ('legacy', 'fips'):
			assert oid.hwid[:3] in HWID.values()
			
			# Technically PIDs can exceed our available integer width.
			# So we allow the number to overflow and "wrap around".
			assert oid.process == getpid() % 0xFFFF
		
		else:
			assert oid.hwid == b'12345'
	
	def test_hex_assignment(self):
		oid = ObjectID()
		oid.hwid = '4341464645'
		assert oid.hwid == b'CAFFE'
	
	def test_component_removal(self):
		oid = ObjectID(hwid=b"CAFFE")
		
		# Deleteing these two, with the custom HWID, leaves only the HWID.
		del oid.time
		del oid.sequence
		
		assert str(oid) == '000000004341464645000000'
	
	def test_date_assignment(self):
		oid = ObjectID(b"\0" * 12)
		assert str(oid) == '000000000000000000000000'
		
		oid.time = datetime(2018, 1, 1, tzinfo=utc)
		assert str(oid) == '5a497a000000000000000000'
		
		oid.time = timedelta(days=1)
		result = str(oid).rstrip('0')
		assert 24 - len(result) == 16
	
	def test_bad_hwid(self):
		with raises(ValueError):
			ObjectID(hwid=b"123456")
	
	def test_bson_encoding(self):
		oid = ObjectID(b"\0" * 12)
		result = BSON.encode({'test': oid})
		assert result == b'\x17\x00\x00\x00\x07test\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		# Above binary structure: mapping, ObjectID attribute, "test" key name, literal ObjectID.
	
	def test_hashability(self):
		# Important tha these are permitted for use as dictionary keys.
		d = {ObjectID(): "bob"}
		assert len(d) == 1
		k = next(iter(d))
		assert isinstance(k, ObjectID)
		assert k == next(iter(d))
	
	@with_timezones
	def test_from_tz_aware(self):
		tz = timezone('Japan')
		when = datetime(1992, 1, 12, 12, 0, 0).replace(tzinfo=tz)
		oid = ObjectID(when)
		assert str(oid) == '296f27b80000000000000000'
		assert repr(oid) == "ObjectID('296f27b80000000000000000', generated='1992-01-11T17:22:00+00:00')"
