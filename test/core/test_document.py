# encoding: utf-8

import pytest

from marrow.mongo.core.document import *
from marrow.mongo.field.base import Field


class Person(Document):
	name = Field()
	age = Field()


@pytest.fixture
def doc(request):
	return Person("Alice", 27)


class TestDocumentMapping(object):
	def test_getitem(self, doc):
		with pytest.raises(KeyError):
			doc['foo']
		
		assert single_ops['roll'] == 27
	
	def test_setitem(self, empty_ops):
		assert repr(empty_ops) == "Ops([])"
		empty_ops['meaning'] = 42
		assert repr(empty_ops) == "Ops([('meaning', 42)])"
	
	def test_delitem(self, empty_ops, single_ops):
		with pytest.raises(KeyError):
			del empty_ops['roll']
		
		assert repr(single_ops) == "Ops([('roll', 27)])"
		del single_ops['roll']
		assert repr(single_ops) == "Ops([])"
	
	def test_length(self, empty_ops, single_ops):
		assert len(empty_ops) == 0
		assert len(single_ops) == 1
	
	def test_keys(self, empty_ops, single_ops):
		assert list(empty_ops.keys()) == []
		assert list(single_ops.keys()) == ['roll']
	
	def test_items(self, empty_ops, single_ops):
		assert list(empty_ops.items()) == []
		assert list(single_ops.items()) == [('roll', 27)]
	
	def test_values(self, empty_ops, single_ops):
		assert list(empty_ops.values()) == []
		assert list(single_ops.values()) == [27]
	
	def test_contains(self, single_ops):
		assert 'foo' not in single_ops
		assert 'roll' in single_ops
	
	def test_equality_inequality(self, empty_ops, single_ops):
		assert empty_ops == {}
		assert empty_ops != {'roll': 27}
		assert single_ops != {}
		assert single_ops == {'roll': 27}
	
	def test_get(self, single_ops):
		assert single_ops.get('foo') is None
		assert single_ops.get('foo', 42) == 42
		assert single_ops.get('roll') == 27
	
	def test_clear(self, single_ops):
		assert len(single_ops.operations) == 1
		single_ops.clear()
		assert len(single_ops.operations) == 0
	
	def test_pop(self, single_ops):
		assert len(single_ops.operations) == 1
		
		with pytest.raises(KeyError):
			single_ops.pop('foo')
		
		assert single_ops.pop('foo', 42) == 42
		assert len(single_ops.operations) == 1
		
		assert single_ops.pop('roll') == 27
		assert len(single_ops.operations) == 0
	
	def test_popitem(self, single_ops):
		assert len(single_ops.operations) == 1
		assert single_ops.popitem() == ('roll', 27)
		assert len(single_ops.operations) == 0
		
		with pytest.raises(KeyError):
			single_ops.popitem()
	
	def test_update(self, empty_ops, single_ops):
		assert len(empty_ops.operations) == 0
		empty_ops.update(name="Bob Dole")
		assert len(empty_ops.operations) == 1
		assert repr(empty_ops) == "Ops([('name', 'Bob Dole')])"
		
		assert len(single_ops.operations) == 1
		assert repr(single_ops) == "Ops([('roll', 27)])"
		single_ops.update([('name', "Bob Dole")])
		assert len(single_ops.operations) == 2
		assert repr(single_ops) in ("Ops([('roll', 27), ('name', 'Bob Dole')])", "Ops([('name', 'Bob Dole'), ('roll', 27)])")
	
	def test_setdefault(self, empty_ops):
		assert len(empty_ops.operations) == 0
		empty_ops.setdefault('fnord', 42)
		assert len(empty_ops.operations) == 1
		assert empty_ops.operations['fnord'] == 42
		empty_ops.setdefault('fnord', 27)
		assert len(empty_ops.operations) == 1
		assert empty_ops.operations['fnord'] == 42
