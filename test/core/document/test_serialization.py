# encoding: utf-8

from marrow.mongo import Document
from marrow.mongo.field import Number, String
from marrow.mongo.trait import Derived, Identified


class Sample(Document):
	string = String()
	number = Number()


class Other(Identified, Document):
	field = String()


class StringPk(Document):
	__pk__ = 'tag'
	
	tag = String('_id')


class NumberPk(Document):
	__pk__ = 'index'
	
	index = Number()


class DynamicRepr(Document):
	__type_store__ = True
	
	first = String(repr=False)
	second = String(repr=lambda doc, f: False)
	
	def __repr__(self, *args, **kw):
		kw['key'] = 27
		return super(DynamicRepr, self).__repr__('pos', *args, **kw)


class TestProgrammersRepresentation(object):
	def test_basic_sample(self):
		record = Sample("a", 1)
		assert repr(record).replace("u'", "'") == "Sample(string='a', number=1)"
	
	def test_identified_sample(self):
		record = Other('58a8e86f0aa7399e8d735310', "Hello world!")
		assert repr(record).replace("u'", "'") == "Other(58a8e86f0aa7399e8d735310, field='Hello world!')"
	
	def test_string_identifier(self):
		record = StringPk('test')
		assert repr(record) == "StringPk(test)"
	
	def test_other_identifier(self):
		record = NumberPk(27)
		assert repr(record) == "NumberPk(27)"
	
	def test_dynamic_repr(self):
		record = DynamicRepr("27", "42")
		assert repr(record).replace("u'", "'") == "test_serialization:DynamicRepr(pos, key=27)"


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
		record = Derived.from_mongo({'_cls': 'Document', 'foo': 'bar'})
		assert record.__class__.__name__ == 'Document'
		assert record['foo'] == 'bar'


class TestJsonSerialization(object):
	def test_json_deserialization(self):
		record = Sample.from_json('{"string": "bar"}')
		assert record.string == 'bar'
	
	def test_json_serialization(self):
		result = Sample("foo", 27).to_json(sort_keys=True)
		assert result == '{"number": 27, "string": "foo"}'
