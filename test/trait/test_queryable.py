# encoding: utf-8

from __future__ import unicode_literals

import pytest
from bson import ObjectId
from pymongo.cursor import CursorType
from pymongo.errors import WriteError

from marrow.mongo import Index, U
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



class TestQueryableCore(object):
	def test_prepare_find_cursor_type_explicit(self, Sample):
		cls, collection, query, options = Sample._prepare_find(cursor_type=CursorType.TAILABLE)
		assert options['cursor_type'] == CursorType.TAILABLE
	
	def test_prepare_find_cursor_conflict(self, Sample):
		with pytest.raises(TypeError):
			Sample._prepare_find(cursor_type=CursorType.TAILABLE, tail=True)
		
		with pytest.raises(TypeError):
			Sample._prepare_find(cursor_type=CursorType.TAILABLE, wait=True)
		
		with pytest.raises(TypeError):
			Sample._prepare_find(cursor_type=CursorType.TAILABLE, tail=True, wait=True)
	
	def test_prepare_find_cursor_type_tail(self, Sample):
		cls, collection, query, options = Sample._prepare_find(tail=True)
		assert options['cursor_type'] == CursorType.TAILABLE_AWAIT
	
	def test_prepare_find_cursor_type_tail_not_wait(self, Sample):
		cls, collection, query, options = Sample._prepare_find(tail=True, wait=False)
		assert options['cursor_type'] == CursorType.TAILABLE
	
	def test_prepare_find_cursor_type_tail_wait_error(self, Sample):
		with pytest.raises(TypeError):
			cls, collection, query, options = Sample._prepare_find(tail=True, await=False)
	
	def test_prepare_find_cursor_type_wait_conflict(self, Sample):
		with pytest.raises(TypeError):
			Sample._prepare_find(wait=False)
	
	def test_prepare_find_max_time_modifier(self, Sample):
		cls, collection, query, options = Sample._prepare_find(max_time_ms=1000)
		assert options['modifiers'] == {'$maxTimeMS': 1000}
	
	def test_prepare_aggregate_skip_limit(self, Sample):
		cls, collection, stages, options = Sample._prepare_aggregate(skip=10, limit=10)
		
		assert stages == [
				{'$skip': 10},
				{'$limit': 10},
			]


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
	
	def test_find_in_sequence(self, db, Sample):
		if tuple((int(i) for i in db.client.server_info()['version'].split('.')[:3])) < (3, 4):
			pytest.xfail("Test expected to fail on MongoDB versions prior to 3.4.")
		
		results = Sample.find_in_sequence('integer', [42, 27])
		results = list(results)
		
		assert [i['string'] for i in results] == ['baz', 'bar']
	
	def test_reload_all(self, Sample):
		doc = Sample.find_one(integer=42)
		assert doc.string == 'baz'
		Sample.get_collection().update_one(Sample.id == doc, U(Sample, integer=1337, string="hoi"))
		assert doc.string == 'baz'
		doc.reload()
		assert doc.string == 'hoi'
		assert doc.integer == 1337
	
	def test_reload_specific(self, Sample):
		doc = Sample.find_one(integer=42)
		assert doc.string == 'baz'
		Sample.get_collection().update_one(Sample.id == doc, U(Sample, integer=1337, string="hoi"))
		assert doc.string == 'baz'
		doc.reload('string')
		assert doc.string == 'hoi'
		assert doc.integer == 42
	
	def test_insert_one(self, Sample):
		doc = Sample(string='diz', integer=2029)
		assert doc.id
		doc.insert_one()
		assert Sample.get_collection().count() == 5
