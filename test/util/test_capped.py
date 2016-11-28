# encoding: utf-8

from __future__ import unicode_literals

from functools import partial
from random import choice
from threading import Thread
from time import sleep, time

import pytest
from pytest import fixture

from marrow.mongo import Document
from marrow.mongo.util.capped import _patch, tail


class Uncapped(Document):
	__collection__ = 'test_uncapped'


class Capped(Document):
	__collection__ = 'test_capped'
	__capped__ = 16 * 1024 * 1024
	__capped_count__ = 100


@pytest.fixture
def uncapped(request, connection):
	db = connection.get_default_database()
	request.addfinalizer(partial(db.drop_collection, Uncapped.__collection__))
	
	return Uncapped.create_collection(db, True)


@pytest.fixture(autouse=True)
def capped(request, connection):
	db = connection.get_default_database()
	
	if tuple((int(i) for i in connection.server_info()['version'].split('.')[:3])) < (3, 2):
		pytest.xfail("Test expected to fail on MongoDB versions prior to 3.2.")
	
	request.addfinalizer(partial(db.drop_collection, Capped.__collection__))
	
	return Capped.create_collection(db, True)


_PRIORITY = (-2, -1, 0, 1, 2)


def gen_log_entries(collection, count=1000):
	collection.insert({'message': 'first'})  # To avoid immediate exit of the tail.ddddd
	
	for i in range(count-2):
		sleep(3.0/count)  # If we go too fast, the test might not be able to keep up.
		collection.insert({'message': 'test #' + str(i) + ' of ' + str(count), 'priority': choice(_PRIORITY)})
	
	collection.insert({'message': 'last'})


class TestCappedQueries(object):
	def test_single(self, capped):
		assert capped.count() == 0
		result = capped.insert({'message': 'first'})
		assert capped.count() == 1
		
		first = next(tail(capped))
		assert first['message'] == 'first'
		assert first['_id'] == result
	
	def test_basic_timeout(self, capped):
		capped.insert({'message': 'first'})
		
		start = time()
		
		result = list(tail(capped, timeout=0.5))
		
		delta = time() - start
		assert len(result) == capped.count()
		assert 0.4 < delta < 0.6
	
	def test_capped_trap(self, uncapped):
		with pytest.raises(TypeError):
			list(tail(uncapped))
	
	def test_empty_trap(self, capped):
		with pytest.raises(ValueError):
			list(tail(capped))
	
	def test_patch(self, capped):
		_patch()
		
		capped.insert({})
		
		assert len(list(capped.tail(timeout=0.25))) == 1
	
	def test_long_iteration(self, capped):
		assert not capped.count()
		
		# Start generating entries.
		t = Thread(target=gen_log_entries, args=(capped, ))
		t.start()
		
		count = 0
		for record in tail(capped, timeout=5):
			count += 1
			if record['message'] == 'last': break
		
		# Note that the collection only allows 100 entries...
		assert capped.count() == 100
		
		# But we successfully saw all 1000 generated records.  :)
		assert count == 1000
		
		t.join()
	
	def test_intermittent_iteration(self, capped):
		assert not capped.count()
		
		# Start generating entries.
		t = Thread(target=gen_log_entries, args=(capped, ))
		t.start()
		
		count = 0
		seen = None
		for record in tail(capped, timeout=2, aggregate=True):
			if count == 50:
				# Records are pooled in batches, so even after the query is timed out-i.e. we take
				# too long to do something in one of our iterations-we may still recieve additional
				# records before the pool drains and the cursor needs to pull more data from the
				# server.  To avoid weird test failures, we break early here.  Symptoms show up as
				# this test failing with "<semi-random large int> == 200" in the final count.
				# If you need to worry about this (i.e. having your own retry), track last seen.
				break
			
			count += 1
			seen = record['_id']
		
		for record in tail(capped, {'_id': {'$gt': seen}}, timeout=2, aggregate=True):
			count += 1
			if record['message'] == 'last': break
		
		t.join()
		
		assert capped.count() == 100
		assert count == 1000
