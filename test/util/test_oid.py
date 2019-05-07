"""General tests, and conformance tests for our ObjectID reimplementation."""

import pytest

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
			b"\x12\x34\x56\x78\x90\x12" * 2,  # Binary string.
			b"123456789012",  # This is also a valid binary string.
		)
	
	invalid = (
			(27, TypeError),  # Integers are bogus.
			(42.0, TypeError),  # Floats doubly so.  (See what I did there?)
			({"test": 27}, TypeError),  # Dictionary is a nope.
			(["gesundheit"], TypeError),  # Lists are right out.
			
			# ('', ValueError),  # It's a string, but not a useful one.
			('12345678901', ValueError),  # Too short.
			('1234567890123', ValueError),  # Too long.
			('abcdefghijkl', ValueError),  # It's a string, but not hex.
		)
	
	def test_invalid_values(self, invalid):
		with pytest.raises(invalid[1]):
			self.validator(invalid[0])
	
	def test_coss_string_equality(self):
		assert ObjectID("123456789012123456789012") == ObjectID(b"\x12\x34\x56\x78\x90\x12\x12\x34\x56\x78\x90\x12")
	
	def test_identity(self):
		a = ObjectID()
		b = ObjectID(a)
		assert a == b
	
	
