# encoding: utf-8

from __future__ import unicode_literals

import pytest
from pymongo.errors import WriteError

from marrow.mongo import Field, Index
from marrow.mongo.trait import Queryable


@pytest.fixture
def db(request, connection):
	return connection.test


@pytest.fixture
def Sample(request, db):
	class Sample(Queryable):
		__collection__ = 'queryable_collection'
		__engine__ = {'mmapv1': {}}
		
		id = None  # Remove the default identifier.
		field = Field()
		other = Field()
		
		_field = Index('field', background=False)
	
	Sample.bind(db).create_collection(drop=True)
	
	return Sample


class TestQueryableTrait(object):
	def test_foo(self, Sample):
		pass
