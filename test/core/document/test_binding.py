# encoding: utf-8

from __future__ import unicode_literals

import pytest

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
