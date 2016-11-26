# encoding: utf-8

from functools import partial

import pymongo
import pytest


@pytest.fixture(scope="module", autouse=True)
def connection(request):
	"""Automatically connect before testing and discard data after testing."""
	connection = pymongo.MongoClient('mongodb://localhost/test')
	
	request.addfinalizer(partial(connection.drop_database, 'test'))
	return connection
