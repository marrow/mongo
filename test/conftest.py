from functools import partial

import pymongo
from pytest import fixture


@fixture(scope='module', autouse=True)
def connection(request) -> pymongo.MongoClient:
	"""Automatically connect before testing and discard data after testing."""
	connection = pymongo.MongoClient('mongodb://localhost/test')
	
	request.addfinalizer(partial(connection.drop_database, 'test'))
	return connection
