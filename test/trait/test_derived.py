import os

from pytest import raises

from marrow.mongo.field import Integer, String
from marrow.mongo.trait import Derived, Queryable


class TestDerived:
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

class TestPromotionDemotion:
	def test_specialize(self):
		a = Source()
		b = a.promote(Journal)
		assert isinstance(b, Journal)
		
		b.title = "Foo"
		assert b['title'] == "Foo"
	
	def test_specialize_fail_underived_uncle(self):
		a = Source()
		
		with raises(TypeError):
			a.promote(Queryable)
	
	def test_specialize_fail_derived_uncle(self):
		b = Book()
		
		with raises(TypeError):
			b.promote(Journal)



class Asset(Derived, Queryable):
	id = String('_id')


class Page(Asset):
	content = String()
	view = String(default='render')


class Folder(Asset):
	view = String(default='list')


class Gallery(Folder):
	thumbnail = Integer(default=320)
	view = Folder.view.adapt(default='grid')


class TestAssetPromotion:
	# From original ticket description.
	
	def test_folder_gallery(self):
		inst = Folder('sample')
		
		assert inst.id == 'sample'
		assert inst.view == 'list'
		
		inst = inst.promote(Gallery)
		
		assert isinstance(inst, Gallery)
		assert inst.id == 'sample'
		assert inst.thumbnail == 320
		assert inst.view == 'grid'
	
	def test_folder_page(self):
		inst = Folder('sample')
		
		with raises(TypeError):
			inst.promote(Page)
	
	def test_folder_asset(self):
		inst = Folder('sample')
		
		assert inst.view == 'list'
		
		inst = inst.demote(Asset)
		
		assert isinstance(inst, Asset)
		assert inst.id == 'sample'
		
		with raises(AttributeError):
			inst.view
