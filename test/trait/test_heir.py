# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document
from marrow.mongo.field import String
from marrow.mongo.trait import HChildren, Heirarchical

TREE = {"Books": [{"Programming": [{"Databases": ["MongoDB", "dbm"]}, "Languages"]}]}


@pytest.fixture(scope='module')
def db(connection):
	connection.drop_database('test')
	return connection.test



class HeirarchicalTest(object):
	class _Sample(Document):
		__collection__ = 'heir'
	
	@pytest.fixture(scope='class')
	def Sample(self, db):
		Sample = self._Sample.bind(db)
		self._populate(Sample)
		return Sample
	
	def _populate(self, Sample):
		pass
	
	def test_get_parent(self, Sample):
		with pytest.raises(NotImplementedError):
			Sample().get_parent()
	
	def test_find_ancestors(self, Sample):
		with pytest.raises(NotImplementedError):
			Sample().find_ancestors()
	
	def test_find_children(self, Sample):
		with pytest.raises(NotImplementedError):
			Sample().find_children()
	
	def test_find_descendants(self, Sample):
		with pytest.raises(NotImplementedError):
			Sample().find_descendants()
	
	def test_detach(self, Sample):
		assert Sample().detach() is None
	
	def test_attach(self, Sample):
		assert Sample().attach(Sample()) is None
	
	def test_attach_before(self, Sample):
		assert Sample().attach_before(Sample()) is None
	
	def test_attach_after(self, Sample):
		assert Sample().attach_after(Sample()) is None


class TestHeirarchical(HeirarchicalTest):
	class _Sample(Heirarchical):
		__collection__ = 'heir'
	
	pass


class TestHChildren(HeirarchicalTest):
	class _Sample(HChildren):
		__collection__ = 'heir_children'
		
		id = String('_id')
	
	def _populate(self, Sample):  # Algorithm differs from tree structure to tree structure.
		Sample.insert_many([
				Sample("MongoDB"),
				Sample("dbm"),
				Sample("Databases", children=["MongoDB", "dbm"]),
				Sample("Languages"),
				Sample("Programming", children=["Databases", "Languages"]),
				Sample("Books", children=["Programming"])
			])
	
	def test_get_root(self, Sample):
		root = Sample.find_one('Books')
		assert isinstance(root, Sample)
		assert root.id == "Books"
		assert root.children == ["Programming"]
	
	def test_get_parent(self, Sample):
		node = Sample.find_one("Languages")
		parent = node.get_parent()
		assert isinstance(parent, Sample)
		assert parent.id == "Programming"
	
	def test_find_siblings(self, Sample):
		node = Sample.find_one("Databases")
		siblings = list(Sample.from_mongo(i) for i in node.find_siblings())
		assert len(siblings) == 1
		
		sibling, = siblings
		assert isinstance(sibling, Sample)
		assert sibling.id == "Languages"
	
	def test_find_children(self, Sample):
		node = Sample.find_one("Programming")
		children = [i['_id'] for i in node.find_children()]
		assert children == ["Databases", "Languages"]
	
	def test_detach(self, Sample):
		node = Sample.find_one("dbm")
		parent = node.get_parent()
		assert "dbm" in parent.children
		
		assert node.detach()
		
		parent.reload('children')
		assert node.id not in parent.children
		assert node.get_parent() is None
	
	def test_attach(self, Sample):
		parent = Sample.find_one("Languages")
		
		node = Sample("Python")
		node.insert_one()
		
		assert parent.attach(node)
		
		parent.reload('children')
		assert node.id in parent.children
		assert node.get_parent() == parent
	
	def test_attach_to(self, Sample):
		parent = Sample.find_one("Languages")
		
		node = Sample("Objective-C")
		node.insert_one()
		
		assert node.attach_to(parent)
		
		parent.reload('children')
		assert node.id in parent.children
		assert node.get_parent() == parent
	
	def test_attach_before(self, Sample):
		sibling = Sample.find_one("Languages")
		parent = sibling.get_parent()
		
		node = Sample("Algorithms")
		node.insert_one()
		
		assert node.attach_before(sibling)
		
		parent.reload('children')
		assert node.id in parent.children
		assert node.get_parent() == parent
		assert parent.children.index(sibling.id) > parent.children.index(node.id)
	
	def test_attach_after(self, Sample):
		sibling = Sample.find_one("Databases")
		parent = sibling.get_parent()
		
		node = Sample("Operating System")
		node.insert_one()
		
		assert node.attach_before(sibling)
		
		parent.reload('children')
		assert node.id in parent.children
		assert node.get_parent() == parent
		assert parent.children.index(sibling.id) > parent.children.index(node.id)
