# encoding: utf-8

from __future__ import unicode_literals

import pytest
from pymongo.errors import WriteError

from marrow.mongo import Document, Field


@pytest.fixture
def db(request, connection):
	return connection.test


@pytest.fixture
def coll(request, db):
	return db.collection


@pytest.fixture
def Sample(request):
	class Sample(Document):
		__collection__ = 'collection'
		__engine__ = {'mmapv1': {}}
		
		field = Field()
	
	return Sample


class TestDocumentBinding(object):
	def test_bind_fail(self, Sample):
		with pytest.raises(ValueError):
			Sample.bind()
	
	def test_bind_specific_collection(self, coll, Sample):
		assert not Sample.__bound__
		
		Sample.bind(collection=coll)
		
		assert Sample.__bound__
	
	def test_bind_database(self, db, Sample):
		assert not Sample.__bound__
		
		Sample.bind(db)
		
		assert Sample.__bound__
	
	def test_create_collection(self, db, Sample):
		assert Sample.create_collection(db).name == 'collection'
	
	def test_validation(self, db, Sample):
		if tuple((int(i) for i in db.client.server_info()['version'].split('.')[:3])) < (3, 2):
			pytest.xfail("Test expected to fail on MongoDB versions prior to 3.2.")
		
		Sample.__validate__ = 'strict'
		Sample.__validator__ = {'field': {'$gt': 27}}
		c = Sample.create_collection(db, True)
		
		c.insert_one(Sample(42))
		
		with pytest.raises(WriteError):
			c.insert_one(Sample(12))
