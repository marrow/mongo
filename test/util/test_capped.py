# encoding: utf-8

from __future__ import unicode_literals


import pytest
from time import time, sleep
from pytest import fixture
from random import choice
from functools import partial
from threading import Thread

from marrow.mongo.util.capped import tail, _patch



# General structure: {message: "String", priority: 0}


@pytest.fixture
def uncapped(request, connection):
	db = connection.get_default_database()
	
	db.drop_collection('test_uncapped')
	db.create_collection(
			'test_uncapped',
			capped = False,
		)
	
	request.addfinalizer(partial(db.drop_collection, 'test_uncapped'))
	
	return db.test_uncapped


@pytest.fixture(autouse=True)
def capped(request, connection):
	db = connection.get_default_database()
	
	if tuple((int(i) for i in connection.server_info()['version'][:3].split('.'))) < (3, 2):
		pytest.xfail("Test expected to fail on MongoDB versions prior to 3.2.")
	
	db.drop_collection('test_capped')
	db.create_collection(
			'test_capped',
			capped = True,
			size = 16 * 1024 * 1024,
			max = 100,
		)
	
	request.addfinalizer(partial(db.drop_collection, 'test_capped'))
	
	return db.test_capped


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
	
	@pytest.mark.xfail(run=__debug__, reason="Development-time diagnostics unavailable in production.")
	def test_capped_trap(self, uncapped):
		with pytest.raises(TypeError):
			list(tail(uncapped))
	
	@pytest.mark.xfail(run=__debug__, reason="Development-time diagnostics unavailable in production.")
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
