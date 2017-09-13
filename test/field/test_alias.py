# encoding: utf-8

from __future__ import unicode_literals

import warnings

import pytest

from marrow.mongo import Document
from marrow.mongo.field import Alias, Array, Embed, String
from marrow.schema.compat import unicode


class TestAliasDirect(object):
	class Sample(Document):
		field = String()
		alias = Alias('field')
		deprecated = Alias('field', deprecate="xyzzy")
	
	def test_query_reference(self):
		q = self.Sample.alias
		assert ~q == "field"
		assert isinstance(q._field, String)
	
	def test_data_access(self):
		inst = self.Sample.from_mongo({'field': 'foo'})
		assert inst.alias == 'foo'
	
	def test_data_assignment(self):
		inst = self.Sample()
		inst.alias = 'bar'
		assert inst.__data__ == {'field': 'bar'}
	
	def test_deprecated_access(self):
		inst = self.Sample.from_mongo({'field': 'foo'})
		
		with warnings.catch_warnings(record=True) as w:
			warnings.simplefilter('always')
			
			assert inst.deprecated == 'foo'
			
			assert len(w) == 1
			assert issubclass(w[-1].category, DeprecationWarning)
			assert 'via deprecated' in unicode(w[-1].message)
			assert 'xyzzy' in unicode(w[-1].message)
	
	def test_deprecated_assignment(self):
		inst = self.Sample()
		
		with warnings.catch_warnings(record=True) as w:
			warnings.simplefilter('always')
			
			inst.deprecated = 'bar'
			
			assert len(w) == 1
			assert issubclass(w[-1].category, DeprecationWarning)
			assert 'via deprecated' in unicode(w[-1].message)
			assert 'xyzzy' in unicode(w[-1].message)
		
		assert inst.__data__ == {'field': 'bar'}


class TestAliasArray(object):
	class Sample(Document):
		field = Array(String())
		alias = Alias('field.0')
	
	def test_query_reference(self):
		q = self.Sample.alias
		assert ~q == "field.0"
		assert isinstance(q._field, String)
	
	def test_data_access(self):
		inst = self.Sample.from_mongo({'field': ['foo']})
		assert inst.alias == 'foo'
	
	def test_data_assignment(self):
		inst = self.Sample.from_mongo({'field': ['foo']})
		inst.alias = 'bar'
		assert inst.__data__ == {'field': ['bar']}


class TestAliasEmbed(object):
	class Sample(Document):
		class Embedded(Document):
			field = String()
		
		field = Embed(Embedded)
		alias = Alias('field.field')
	
	def test_query_reference(self):
		q = self.Sample.alias
		assert ~q == "field.field"
		assert isinstance(q._field, String)
	
	def test_data_access(self):
		inst = self.Sample.from_mongo({'field': {'field': 'foo'}})
		assert inst.alias == 'foo'
	
	def test_data_assignment(self):
		inst = self.Sample().from_mongo({'field': {}})
		inst.alias = 'bar'
		assert inst.__data__ == {'field': {'field': 'bar'}}


class TestAliasArrayEmbed(object):
	class Sample(Document):
		class Embedded(Document):
			field = String()
		
		field = Array(Embedded)
		alias = Alias('field.0.field')
	
	def test_query_reference(self):
		q = self.Sample.alias
		assert ~q == "field.0.field"
		assert isinstance(q._field, String)
	
	def test_data_access(self):
		inst = self.Sample.from_mongo({'field': [{'field': 'foo'}]})
		assert inst.alias == 'foo'
	
	def test_data_assignment(self):
		inst = self.Sample.from_mongo({'field': [{'field': 'foo'}]})
		inst.alias = 'bar'
		assert inst.__data__ == {'field': [{'field': 'bar'}]}
