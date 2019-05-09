"""General tests, and conformance tests for our ObjectID reimplementation."""

from datetime import datetime, timedelta
from pickle import dumps, loads

from bson.tz_util import utc
from pytest import mark, raises

from marrow.mongo import ObjectID
from marrow.schema.testing import ValidationTest, pytest_generate_tests


class AnyObjectID:
	def __eq__(self, other):
		return isinstance(other, ObjectID)

anyoid = AnyObjectID()


class TestPyMongoObjectID(ValidationTest):
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
	
	def test_invalid_values(self, invalid):
		# Overridden because in our case, we also vary on exception class.
		with raises(invalid[1]):
			self.validator(invalid[0])
	
	def test_coss_string_equality(self):
		assert ObjectID("123456789012123456789012") == ObjectID(b"\x12\x34\x56\x78\x90\x12\x12\x34\x56\x78\x90\x12")
	
	def test_identity_and_equality(self):
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
