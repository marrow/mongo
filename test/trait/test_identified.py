import pytest
from bson import ObjectId

from marrow.mongo import Field, Index
from marrow.mongo.trait import Identified


@pytest.fixture
def Sample(request):
	class Sample(Identified):
		pass
	
	return Sample


class TestIdentifiedTrait(object):
	def test_document_comparison(self, Sample):
		id = ObjectId()
		a = Sample(id)
		b = Sample(id)
		assert a == b
		assert not (a != b)
		b.id = None
		assert not (a == b)
		assert a != b
	
	def test_identifier_comparison(self, Sample):
		id = ObjectId()
		a = Sample(id)
		assert a == id
		assert not (a != id)
		assert not (a == "not the ID")
		assert a != "not the ID"
