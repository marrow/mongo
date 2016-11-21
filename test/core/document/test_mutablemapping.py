# encoding: utf-8

import pytest

from marrow.schema.compat import odict
from marrow.mongo import Document, Field
from marrow.mongo.util import SENTINEL


class Person(Document):
	name = Field()
	age = Field(default=42, assign=True)


@pytest.fixture
def doc(request):
	return Person("Alice", 27)


class TestDocumentMutableMapping(object):
	def test_getitem(self, doc):
		"""Allow dictionary-style write access to stored data."""
		
		with pytest.raises(KeyError):
			doc['foo']
		
		assert doc['age'] == 27
	
	def test_setitem(self, doc):
		"""Allow dictionary-style write access to stored data."""
		
		assert len(doc) == 2
		doc['meaning'] = SENTINEL
		assert len(doc) == 3
		assert doc['meaning'] is doc.__data__['meaning'] is SENTINEL
	
	def test_delitem(self, doc):
		"""Allow dictionary-style deletiodn of stored data."""
		
		with pytest.raises(KeyError):
			del doc['roll']
		
		assert len(doc) == 2
		del doc['name']
		assert len(doc) == 1
	
	def test_iteration(self, doc):
		assert list(iter(doc)) == ['name', 'age']
	
	def test_length(self, doc):
		"""It is possible to get the number of keys in the stored data."""
		
		assert len(doc) == 2
	
	def test_keys(self, doc):
		"""Retreival of keys for stored data, preserving declaration order."""
		
		assert list(doc.keys()) == ['name', 'age']
		doc['foo'] = 42
		assert list(doc.keys()) == ['name', 'age', 'foo']
	
	def test_items(self, doc):
		"""Retreival of item tuples for stored data, preserving declaration order."""
		
		assert list(doc.items()) == [('name', "Alice"), ('age', 27)]
		doc['foo'] = 42
		assert list(doc.items()) == [('name', "Alice"), ('age', 27), ('foo', 42)]
	
	def test_values(self, doc):
		"""Retrieval of stored data values, preserving declaration order."""
		
		assert list(doc.values()) == ["Alice", 27]
		doc['foo'] = 42
		assert list(doc.values()) == ["Alice", 27, 42]
	
	def test_contains(self, doc):
		"""It is possible to identify defined fields by name."""
		
		assert 'foo' not in doc
		assert 'name' in doc
	
	def test_equality_inequality(self, doc):
		"""It is possible to compare the document against dictionary-alike types."""
		
		assert doc != {}
		assert doc == {'name': "Alice", 'age': 27}
		assert doc == odict((('name', 'Alice'), ('age', 27)))
	
	def test_get(self, doc):
		"""Explicit retrieval of value by name, allowing default values."""
		
		assert doc.get('foo') is None
		assert doc.get('foo', 42) == 42
		assert doc.get('age') == 27
	
	def test_clear(self, doc):
		"""Existing data can be cleared in a single operation."""
		
		assert len(doc.__data__) == 2
		doc.clear()
		assert len(doc.__data__) == 0
	
	def test_pop(self, doc):
		"""Data can be retrieved and removed by key in a single operation, allowing default values."""
		
		assert len(doc.__data__) == 2
		
		with pytest.raises(KeyError):
			doc.pop('foo')
		
		assert doc.pop('foo', 42) == 42
		assert len(doc.__data__) == 2
		
		assert doc.pop('age') == 27
		assert len(doc.__data__) == 1
	
	def test_popitem(self, doc):
		"""Data can be retrieved and removed in FILO order."""
		assert len(doc.__data__) == 2
		assert doc.popitem() == ('age', 27)
		assert len(doc.__data__) == 1
		
		doc.popitem()
		
		with pytest.raises(KeyError):
			doc.popitem()
	
	def test_update(self, doc):
		"""The dataset can be explicitly updated from iterables or other dictionary-alikes."""
		
		assert len(doc.__data__) == 2
		doc.update(name="Bob Dole")
		assert len(doc.__data__) == 2
		assert doc.name == "Bob Dole"
		
		doc.update([('bob', "Bob Dole")])
		assert len(doc.__data__) == 3
	
	def test_setdefault(self, doc):
		"""Default values can be assigned explicitly."""
		
		assert len(doc.__data__) == 2
		doc.setdefault('fnord', 42)
		assert len(doc.__data__) == 3
		assert doc.__data__['fnord'] == 42
		doc.setdefault('fnord', 27)
		assert len(doc.__data__) == 3
		assert doc.__data__['fnord'] == 42
