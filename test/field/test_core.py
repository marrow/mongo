# encoding: utf-8

import pytest

from marrow.mongo import Document, field
from marrow.mongo.core.field import FieldTransform, Field


def test_registry():
	assert field.Field is Field
	assert field['Field'] is Field
	assert field['marrow.mongo:Field'] is Field


class IntegerizingField(Field):
	"""This is backwards to how most fields operate, but may be useful for more complex types."""
	
	def to_foreign(self, document, field, value):
		"""Return the value to store in the database; transformed on attribute assignment."""
		return str(value)
	
	def to_native(self, document, field, value):
		"""Return the value that should be presented to Python; transformed on attribute access."""
		return int(value)


class Sample(Document):
	field = Field()
	integer = IntegerizingField()


class TestFieldTransform(object):
	def test_foreign_passthrough(self):
		assert FieldTransform().foreign(None, (Sample.field._field, Sample)) is None
		
		inst = Sample()
		inst.field = None
		
		assert inst['field'] is None
	
	def test_foreign_call(self):
		assert FieldTransform().foreign(27, (Sample.integer._field, Sample)) == '27'
		
		inst = Sample()
		inst.integer = 27
		
		assert inst['integer'] == '27'
	
	def test_native_passthrough(self):
		assert FieldTransform().native(None, (Sample.field._field, Sample)) is None
		
		inst = Sample.from_mongo({'field': None})
		assert inst.field is None
	
	def test_native_call(self):
		assert FieldTransform().native('42', (Sample.integer._field, Sample)) == 42
		
		inst = Sample.from_mongo({'integer': '42'})
		assert inst.integer == 42


class TestField(object):
	def test_repr_redefault(self):
		assert repr(Field(choices=None)) == "Field('<anonymous>')"
	
	def test_repr(self):
		assert repr(Field(default=27)) == "Field('<anonymous>', default=27)"
	
	def test_nullable(self):
		class Mock(Document):
			field = Field()
			nullable = Field(nullable=True)
		
		with pytest.raises(AttributeError):
			Mock().field
		
		assert Mock().nullable is None
	
	def test_exclusive_assignment(self):
		class Mock(Document):
			a = Field(exclusive={'b'})
			b = Field(exclusive={'a'})
			c = Field(exclusive={'a'})
		
		inst = Mock()
		inst.a = 27
		
		assert inst.__data__ == {'a': 27}
		
		with pytest.raises(AttributeError):
			inst.b = 42
		
		with pytest.raises(AttributeError):
			inst.c = 64
		
		inst = Mock()
		inst.b = 42
		
		with pytest.raises(AttributeError):
			inst.a = 27
		
		inst.c = 64
	
	def test_basic_usage(self):
		class Mock(Document):
			field = Field()
		
		inst = Mock()
		assert inst.__data__ == {}
		
		inst.field = 27
		assert inst.field == 27
		assert inst.__data__ == {'field': 27}
		
		del inst.field
		assert inst.__data__ == {}



class TestFieldSecurity(object):
	def test_writeable_predicate_simple(self):
		f = Field(write=None)
		assert f.is_writeable() is False
	
	def test_writeable_predicate_simple_callback(self):
		f = Field(write=lambda f: True)
		assert f.is_writeable() is True
	
	def test_writeable_predicate_contextual(self):
		f = Field(write=lambda c, f: c['v'])
		assert f.is_writeable({'v': False}) is False
	
	def test_readable_predicate_simple(self):
		f = Field(read=1)
		assert f.is_readable() is True
	
	def test_readable_predicate_simple_callback(self):
		f = Field(read=lambda f: True)
		assert f.is_readable() is True
	
	def test_readable_predicate_contextual(self):
		f = Field(read=lambda c, f: c['v'])
		assert f.is_readable({'v': False}) is False
