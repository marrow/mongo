# encoding: utf-8

from marrow.mongo import Document
from marrow.mongo.field import String, Number


class Sample(Document):
	string = String()
	number = Number()


class TestMongoSerialization(object):
	def test_unnessicary_deserialization(self):
		record = Sample("a", 1)
		assert Sample.from_mongo(record) is record
	
	def test_rest_passthrough(self):
		record = Sample("a", 1)
		assert record.as_rest is record
	
	def test_standard_use(self):
		record = Sample.from_mongo({'string': 'foo', 'number': 27})
		assert record.string == 'foo'
		assert record.number == 27
	
	def test_explicit_class(object):
		record = Sample.from_mongo({'_cls': 'Document', 'foo': 'bar'})
		assert record.__class__.__name__ == 'Document'
		assert record['foo'] == 'bar'


class TestJsonSerialization(object):
	def test_json_deserialization(self):
		record = Sample.from_json('{"string": "bar"}')
		assert record.string == 'bar'
	
	def test_json_serialization(self):
		result = Sample("foo", 27).to_json(sort_keys=True)
		assert result == '{"number": 27, "string": "foo"}'
