# encoding: utf-8

from __future__ import unicode_literals

import pytest
from bson import ObjectId
from pymongo.errors import WriteError

from marrow.mongo import Field, Index, U
from marrow.mongo.field import Integer, String
from marrow.mongo.trait import Queryable


@pytest.fixture
def db(request, connection):
	return connection.test


@pytest.fixture
def Sample(request, db):
	class Sample(Queryable):
		__collection__ = 'queryable_collection'
		
		string = String()
		integer = Integer()
		
		_field = Index('integer', background=False)
	
	Sample.bind(db).create_collection(drop=True)
	
	# Don't trigger code coverage just to insert test data...
	Sample.__bound__.insert_many([
			{'string': 'foo', 'integer': 7},
			{'string': 'bar', 'integer': 27},
			{'string': 'baz', 'integer': 42},
			{'_id': ObjectId('59129d460aa7397ce3f9643e'), 'string': 'pre', 'integer': None},
		])
	
	return Sample


class TestQueryableTrait(object):
	def test_find(self, Sample):
		rs = Sample.find()
		assert rs.count() == 4
		assert [i['integer'] for i in rs] == [7, 27, 42, None]
	
	def test_find_first(self, Sample):
		doc = Sample.find_one()
		assert isinstance(doc, Sample)
		assert doc.string == 'foo'
		assert doc.integer == 7
	
	def test_find_one(self, Sample):
		doc = Sample.find_one(Sample.integer == 27)
		assert doc.string == 'bar'
	
	def test_find_one_short(self, Sample):
		doc = Sample.find_one('59129d460aa7397ce3f9643e')
		assert doc.string == 'pre'
		assert doc.integer is None
	
	def test_find_in_sequence(self, Sample):
		pass
	
	def test_reload(self, Sample):
		doc = Sample.find_one(integer=42)
		assert doc.string == 'baz'
		Sample.get_collection().update(Sample.id == doc, U(Sample, string="hoi"))
		assert doc.string == 'baz'
		doc.reload()
		assert doc.string == 'hoi'
	
	def test_insert_one(self, Sample):
		pass
	
	def test_insert_many(self, Sample):
		pass
