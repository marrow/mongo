# encoding: utf-8

import pytest

from marrow.mongo import Document, Field, Index


@pytest.fixture
def coll(connection):
	return connection.test.collection


class Sample(Document):
	field = Field('field_name')
	_field = Index('field', background=False)
	_inverse = Index('-field', background=False)


class TestIndex(object):
	def test_ordering(self):
		assert Sample._field.fields == [('field_name', 1)]
		assert Sample._inverse.fields == [('field_name', -1)]
	
	def test_creation(self, coll):
		Sample._field.create_index(coll)
		indexes = coll.index_information()
		assert '_field' in indexes
		assert indexes['_field'] == {
				'background': False,
				'key': [('field_name', 1)],
				'ns': 'test.collection',
				'sparse': False,
				'v': 1,
			}
