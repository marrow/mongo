# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo.field import Integer, String
from marrow.mongo.trait import Derived, Queryable


class TestDerived(object):
	class Sample(Derived):
		pass
	
	def test_reference(self):
		inst = self.Sample()
		assert inst['_cls'] == 'test_derived:TestDerived.Sample'
	
	def test_repr(self):
		inst = self.Sample()
		assert repr(inst).startswith('test_derived:TestDerived.Sample')
	
	def test_load(self):
		inst = Derived.from_mongo({'_cls': 'test_derived:TestDerived.Sample'})
		assert isinstance(inst, self.Sample)
	
	def test_index(self):
		assert '_cls' in self.Sample.__indexes__



# From: https://github.com/MongoEngine/mongoengine/issues/167#issuecomment-297513842

class Source(Derived, Queryable):
	__collection__ = 'sources'

class TextSource(Source):
	author = String()
	word_count = Integer()

class Book(TextSource):
	pages = Integer()

class Journal(TextSource):
	title = String()

class Article(TextSource):
	pass

#        Source
#          |
#       TextSource
#   /      |        \
# Book  Journal  Article

class TestPromotionDemotion(object):
	def test_specialize(self):
		a = Source()
		b = a.promote(Journal)
		assert isinstance(b, Journal)
		
		b.title = "Foo"
		assert b['title'] == "Foo"
	
	def test_specialize_failure(self):
		a = Source()
		
		with pytest.raises(TypeError):
			a.promote(Queryable)
		
		b = Book()
		
		with pytest.raises(TypeError):
			b.promote(Journal)
