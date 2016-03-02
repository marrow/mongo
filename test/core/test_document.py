# encoding: utf-8

import pytest

from marrow.mongo.core.document import Document
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
		
		assert doc['age'] == 27
	
	def test_setitem(self, doc):
		assert len(doc) == 2
		doc['meaning'] = 42
		assert len(doc) == 3
	
	def test_delitem(self, doc):
		with pytest.raises(KeyError):
			del doc['roll']
		
		assert len(doc) == 2
		del doc['name']
		assert len(doc) == 1
	
	def test_length(self, doc):
		assert len(doc) == 2
	
	def test_keys(self, doc):
		assert list(doc.keys()) == ['name', 'age']
	
	def test_items(self, doc):
		assert list(doc.items()) == [('name', "Alice"), ('age', 27)]
	
	def test_values(self, doc):
		assert list(doc.values()) == ["Alice", 27]
	
	def test_contains(self, doc):
		assert 'foo' not in doc
		assert 'name' in doc
	
	def test_equality_inequality(self, doc):
		assert doc != {}
		assert doc == {'name': "Alice", 'age': 27}
	
	def test_get(self, doc):
		assert doc.get('foo') is None
		assert doc.get('foo', 42) == 42
		assert doc.get('age') == 27
	
	def test_clear(self, doc):
		assert len(doc.__data__) == 2
		doc.clear()
		assert len(doc.__data__) == 0
	
	def test_pop(self, doc):
		assert len(doc.__data__) == 2
		
		with pytest.raises(KeyError):
			doc.pop('foo')
		
		assert doc.pop('foo', 42) == 42
		assert len(doc.__data__) == 2
		
		assert doc.pop('age') == 27
		assert len(doc.__data__) == 1
	
	def test_popitem(self, doc):
		assert len(doc.__data__) == 2
		assert doc.popitem() == ('age', 27)
		assert len(doc.__data__) == 1
		
		doc.popitem()
		
		with pytest.raises(KeyError):
			doc.popitem()
	
	def test_update(self, doc):
		assert len(doc.__data__) == 2
		doc.update(name="Bob Dole")
		assert len(doc.__data__) == 2
		assert doc.name == "Bob Dole"
		
		doc.update([('bob', "Bob Dole")])
		assert len(doc.__data__) == 3
	
	def test_setdefault(self, doc):
		assert len(doc.__data__) == 2
		doc.setdefault('fnord', 42)
		assert len(doc.__data__) == 3
		assert doc.__data__['fnord'] == 42
		doc.setdefault('fnord', 27)
		assert len(doc.__data__) == 3
		assert doc.__data__['fnord'] == 42
