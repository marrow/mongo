# encoding: utf-8

from __future__ import unicode_literals

import pytest
from pymongo.errors import WriteError

from marrow.mongo import Field, Index
from marrow.mongo.trait import Collection


@pytest.fixture
def db(request, connection):
	return connection.test


@pytest.fixture
def coll(request, db):
	return db.collection


@pytest.fixture
def Sample(request):
	class Sample(Collection):
		__collection__ = 'collection'
		__engine__ = {'mmapv1': {}}
		
		id = None  # Remove the default identifier.
		field = Field()
		other = Field()
		
		_field = Index('field', background=False)
	
	return Sample


class TestDocumentBinding(object):
	def test_bind_fail(self, Sample):
		with pytest.raises(TypeError):
			Sample.bind()
	
	def test_bind_specific_collection(self, coll, Sample):
		assert not Sample.__bound__
		
		Sample.bind(coll)
		
		assert Sample.__bound__
	
	def test_bind_specific_collection_twice(self, coll, Sample):
		assert not Sample.__bound__
		
		Sample.bind(coll)
		
		assert Sample.__bound__
		
		first = Sample.__bound__
		Sample.bind(coll)
		
		assert Sample.__bound__ is first
		
		assert Sample.get_collection() is first
	
	def test_bind_database(self, db, Sample):
		assert not Sample.__bound__
		
		Sample.bind(db)
		
		assert Sample.__bound__
	
	def test_create_collection(self, db, Sample):
		assert Sample.create_collection(db, drop=True, indexes=False).name == 'collection'
	
	def test_create_bound_collection(self, db, Sample):
		assert Sample.bind(db).create_collection(drop=True, indexes=False).name == 'collection'
	
	def test_create_collection_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample.create_collection()
		
		with pytest.raises(TypeError):
			Sample.create_collection("Hoi.")
	
	def test_create_collection_collection(self, db, Sample):
		assert Sample.create_collection(db.foo, True).name == 'foo'
	
	def test_get_collection_failure(self, Sample):
		with pytest.raises(TypeError):
			Sample.get_collection(None)
		
		with pytest.raises(TypeError):
			Sample.get_collection("Hoi.")
	
	def test_validation(self, db, Sample):
		if tuple((int(i) for i in db.client.server_info()['version'].split('.')[:3])) < (3, 2):
			pytest.xfail("Test expected to fail on MongoDB versions prior to 3.2.")
		
		Sample.__validate__ = 'strict'
		Sample.__validator__ = {'field': {'$gt': 27}}
		Sample.create_collection(db, True, indexes=False)
		Sample = Sample.bind(db)
		
		Sample(42).insert()
		
		with pytest.raises(WriteError):
			Sample(12).insert()
	
	def test_index_construction(self, db, Sample):
		c = Sample.create_collection(db, True, indexes=False)
		Sample.create_indexes(c, True)
		
		indexes = c.index_information()
		assert '_field' in indexes
		del indexes['_field']['v']
		assert indexes['_field'] == {
				'background': False,
				'key': [('field', 1)],
				'ns': 'test.collection',
				'sparse': False
			}
	
	def test_update_empty(self, db, Sample):
		Sample.bind(db).create_collection(drop=True)
		
		with pytest.raises(TypeError):
			Sample().update_one()
