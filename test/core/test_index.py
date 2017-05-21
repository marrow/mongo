# encoding: utf-8

import pytest

from marrow.mongo import Document, Field, Index


@pytest.fixture
def coll(connection):
	return connection.test.collection


class Sample(Document):
	field = Field('field_name')
	other = Field('other_field')
	_field = Index('field', background=False)
	_inverse = Index('-field', background=False)


class TestIndex(object):
	def test_ordering(self):
		assert Sample._field.fields == [('field_name', 1)]
		assert Sample._inverse.fields == [('field_name', -1)]
	
	def test_creation(self, coll):
		Sample._field.create(coll)
		indexes = coll.index_information()
		assert '_field' in indexes
		del indexes['_field']['v']
		assert indexes['_field'] == {
				'background': False,
				'key': [('field_name', 1)],
				'ns': 'test.collection',
				'sparse': False,
			}
	
	def test_removal(self, coll):
		Sample._field.create(coll)
		indexes = coll.index_information()
		assert '_field' in indexes
		del indexes['_field']['v']
		assert indexes['_field'] == {
				'background': False,
				'key': [('field_name', 1)],
				'ns': 'test.collection',
				'sparse': False,
			}
		Sample._field.drop(coll)
		indexes = coll.index_information()
		assert '_field' not in indexes
	
	def test_adaption(self):
		class Updated(Sample):
			_field = Sample._field.adapt('other', sparse=True)
		
		assert Sample._field.fields == [('field_name', 1)]
		assert Updated._field.fields == [('field_name', 1), ('other_field', 1)]
		
		assert not Sample._field.sparse
		assert Updated._field.sparse
