# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document
from marrow.mongo.field import String
from marrow.mongo.trait import HAncestors, HChildren, Heirarchical, HNested, HParent, HPath
from marrow.schema.compat import unicode


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
		
		assert node.attach_after(sibling)
		
		parent.reload('children')
		assert node.id in parent.children
		assert node.get_parent() == parent
		assert parent.children.index(sibling.id) < parent.children.index(node.id)


class TestHParent(HeirarchicalTest):
	class _Sample(HParent):
		__collection__ = 'heir_parent'
		
		id = String('_id')
	
	def _populate(self, Sample):  # Algorithm differs from tree structure to tree structure.
		Sample.insert_many([
				Sample("Books"),
				Sample("Programming", parent="Books"),
				Sample("Databases", parent="Programming"),
				Sample("Languages", parent="Programming"),
				Sample("dbm", parent="Databases"),
				Sample("MongoDB", parent="Databases"),
			])
	
	def test_get_root(self, Sample):
		root = Sample.find_one('Books')
		assert isinstance(root, Sample)
		assert root.id == "Books"
		assert root.parent is None
	
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
		children = list(sorted(i['_id'] for i in node.find_children()))
		assert children == ["Databases", "Languages"]
	
	def test_detach(self, Sample):
		node = Sample.find_one("dbm")
		parent = node.get_parent()
		assert node.parent == parent.id
		
		assert node.detach()
		assert node.parent is None
		
		node.reload('parent')
		assert node.parent is None
		assert node.get_parent() is None
	
	def test_attach(self, Sample):
		parent = Sample.find_one("Languages")
		
		node = Sample("Python")
		node.insert_one()
		
		assert parent.attach(node)
		assert node.parent == parent.id
		
		node.reload('parent')
		assert node.parent == parent.id
		assert node.get_parent() == parent
	
	def test_attach_to(self, Sample):
		parent = Sample.find_one("Languages")
		
		node = Sample("Objective-C")
		node.insert_one()
		
		assert node.attach_to(parent)
		assert node.parent == parent.id
		
		node.reload('parent')
		assert node.parent == parent.id
		assert node.get_parent() == parent


class TestHAncestors(HeirarchicalTest):
	class _Sample(HAncestors):
		__collection__ = 'heir_ancestors'
		
		id = String('_id')
	
	def _populate(self, Sample):  # Algorithm differs from tree structure to tree structure.
		Sample.insert_many([
				Sample("Books"),
				Sample("Programming", parent="Books", ancestors=["Books"]),
				Sample("Databases", parent="Programming", ancestors=["Books", "Programming"]),
				Sample("Languages", parent="Programming", ancestors=["Books", "Programming"]),
				Sample("dbm", parent="Databases", ancestors=["Books", "Programming", "Databases"]),
				Sample("MongoDB", parent="Databases", ancestors=["Books", "Programming", "Databases"]),
			])
	
	def test_get_root(self, Sample):
		root = Sample.find_one('Books')
		assert isinstance(root, Sample)
		assert root.id == "Books"
		assert root.parent is None
		assert root.ancestors == []
	
	def test_get_parent(self, Sample):
		node = Sample.find_one("Languages")
		assert node.ancestors == ["Books", "Programming"]
		parent = node.get_parent()
		assert isinstance(parent, Sample)
		assert parent.id == "Programming"
		assert parent.ancestors == ["Books"]
	
	def test_find_ancestors(self, Sample):
		node = Sample.find_one("Databases")
		ancestors = node.find_ancestors(projection=('id', ))
		ancestors = list(i['_id'] for i in ancestors)
		assert ancestors == list(reversed(node.ancestors))
	
	def test_find_siblings(self, Sample):
		node = Sample.find_one("Databases")
		siblings = list(Sample.from_mongo(i) for i in node.find_siblings())
		assert len(siblings) == 1
		
		sibling, = siblings
		assert isinstance(sibling, Sample)
		assert sibling.id == "Languages"
	
	def test_find_children(self, Sample):
		node = Sample.find_one("Programming")
		children = list(sorted(i['_id'] for i in node.find_children()))
		assert children == ["Databases", "Languages"]
	
	def test_find_descendants(self, Sample):
		node = Sample.find_one("Databases")
		descendants = list(sorted(i['_id'] for i in node.find_descendants()))
		assert descendants == ["MongoDB", "dbm"]
	
	def test_detach(self, Sample):
		node = Sample.find_one("dbm")
		parent = node.get_parent()
		assert node.parent == parent.id
		assert node.ancestors[:len(parent.ancestors) + 1] == parent.ancestors + [parent.id]
		
		assert node.detach()
		assert node.parent is None
		assert node.ancestors == []
		
		node.reload('parent', 'ancestors')
		assert node.parent is None
		assert node.get_parent() is None
		assert node.ancestors == []
	
	def test_attach(self, Sample):
		parent = Sample.find_one("Languages")
		
		node = Sample("Python")
		node.insert_one()
		
		assert parent.attach(node)
		assert node.parent == parent.id
		assert parent.id in node.ancestors
		assert len(node.ancestors) == len(parent.ancestors) + 1
		
		node.reload('parent', 'ancestors')
		assert node.parent == parent.id
		assert node.get_parent() == parent
		assert parent.id in node.ancestors
		assert len(node.ancestors) == len(parent.ancestors) + 1
	
	def test_attach_to(self, Sample):
		parent = Sample.find_one("Languages")
		
		node = Sample("Objective-C")
		node.insert_one()
		
		assert node.attach_to(parent)
		assert node.parent == parent.id
		assert parent.id in node.ancestors
		assert len(node.ancestors) == len(parent.ancestors) + 1
		
		node.reload('parent', 'ancestors')
		assert node.parent == parent.id
		assert node.get_parent() == parent
		assert parent.id in node.ancestors
		assert len(node.ancestors) == len(parent.ancestors) + 1


class TestHPath(HeirarchicalTest):
	class _Sample(HPath):
		__collection__ = 'heir_path'
	
	def _populate(self, Sample):  # Algorithm differs from tree structure to tree structure.
		Sample.insert_many([
				Sample(slug="Books", path='/Books'),
				Sample(slug="Programming", path="/Books/Programming"),
				Sample(slug="Databases", path="/Books/Programming/Databases"),
				Sample(slug="Languages", path="/Books/Programming/Languages"),
				Sample(slug="dbm", path="/Books/Programming/Databases/dbm"),
				Sample(slug="MongoDB", path="/Books/Programming/Databases/MongoDB"),
			])
	
	def test_get_root(self, Sample):
		root = Sample.find_one(path='/Books')
		assert isinstance(root, Sample)
		assert root.slug == "Books"
		assert root.get_parent() is None
	
	def test_get_parent(self, Sample):
		node = Sample.find_one(path="/Books/Programming/Languages")
		parent = node.get_parent()
		assert isinstance(parent, Sample)
		assert parent.slug == "Programming"
		assert parent.path == node.path.parent
	
	def test_find_ancestors(self, Sample):
		node = Sample.find_one(path="/Books/Programming/Databases")
		ancestors = node.find_ancestors(projection=('path', ))
		ancestors = list(i['path'] for i in ancestors)
		
		for i in ancestors:
			assert unicode(node.path).startswith(unicode(i))
	
	def test_find_siblings(self, Sample):
		node = Sample.find_one(path="/Books/Programming/Databases")
		siblings = list(Sample.from_mongo(i) for i in node.find_siblings())
		assert len(siblings) == 1
		
		sibling, = siblings
		assert isinstance(sibling, Sample)
		assert sibling.slug == "Languages"
	
	def test_find_children(self, Sample):
		node = Sample.find_one(path="/Books/Programming")
		children = list(sorted(i['slug'] for i in node.find_children()))
		assert children == ["Databases", "Languages"]
	
	def test_find_descendants(self, Sample):
		node = Sample.find_one(path="/Books/Programming/Databases")
		descendants = list(sorted(i['slug'] for i in node.find_descendants()))
		assert descendants == ["MongoDB", "dbm"]
	
	def test_detach(self, Sample):
		node = Sample.find_one(slug="dbm")
		
		assert node.detach()
		assert node.get_parent() is None
		assert unicode(node.path) == node.slug
	
	def test_attach(self, Sample):
		parent = Sample.find_one(slug="Languages")
		
		node = Sample(slug="Python", path="Python")  # Obvious TODO
		node.insert_one()
		
		assert parent.attach(node)
		assert unicode(node.path) == '/Books/Programming/Languages/Python'
		
		node.reload('path')
		assert unicode(node.path) == '/Books/Programming/Languages/Python'
	
	def test_attach_to(self, Sample):
		parent = Sample.find_one(slug="Languages")
		
		node = Sample(slug="Objective-C", path="Objective-C")  # Obvious TODO
		node.insert_one()
		
		assert node.attach_to(parent)
		assert unicode(node.path) == '/Books/Programming/Languages/Objective-C'
		
		node.reload('path')
		assert unicode(node.path) == '/Books/Programming/Languages/Objective-C'
		assert node.get_parent() == parent


class TestHNested(HeirarchicalTest):
	class _Sample(HNested):
		__collection__ = 'heir_nested'
		
		id = String('_id')
	
	def _populate(self, Sample):  # Algorithm differs from tree structure to tree structure.
		Sample.insert_many([
				Sample("Books", left=1, right=12),
				Sample("Programming", left=2, right=11),
				Sample("Languages", left=3, right=4),
				Sample("Databases", left=5, right=10),
				Sample("MongoDB", left=6, right=7),
				Sample("dbm", left=8, right=9),
			])
	
	def test_get_root(self, Sample):
		root = Sample.find_one('Books')
		assert isinstance(root, Sample)
	
	def test_get_parent(self, Sample):
		node = Sample.find_one("Languages")
		
		parent = node.get_parent()
		assert isinstance(parent, Sample)
		
		assert parent.id == "Programming"
	
	def test_find_ancestors(self, Sample):
		node = Sample.find_one("Databases")
		ancestors = node.find_ancestors(projection=('id', ))
		ancestors = list(i['_id'] for i in ancestors)
		
		assert ancestors == ['Books', 'Programming']
	
	def test_find_descendants(self, Sample):
		node = Sample.find_one("Databases")
		descendants = list(sorted(i['_id'] for i in node.find_descendants()))
		assert len(descendants) == (node.right - node.left - 1) / 2  # Internal consistency.
		assert descendants == ["MongoDB", "dbm"]
	
	def test_detach(self, Sample):
		node = Sample.find_one("dbm")
		
		assert node.detach()
		assert node.get_parent() is None
		assert node.left == 11
		assert node.right == 12
		
		root = Sample.find_one("Books")
		assert root.left == 1
		assert root.right == 10
	
	def test_attach(self, Sample):
		return
		parent = Sample.find_one(slug="Languages")
		
		node = Sample(slug="Python", path="Python")  # Obvious TODO
		node.insert_one()
		
		assert parent.attach(node)
		assert unicode(node.path) == '/Books/Programming/Languages/Python'
		
		node.reload('path')
		assert unicode(node.path) == '/Books/Programming/Languages/Python'
	
	def test_attach_to(self, Sample):
		return
		parent = Sample.find_one(slug="Languages")
		
		node = Sample(slug="Objective-C", path="Objective-C")  # Obvious TODO
		node.insert_one()
		
		assert node.attach_to(parent)
		assert unicode(node.path) == '/Books/Programming/Languages/Objective-C'
		
		node.reload('path')
		assert unicode(node.path) == '/Books/Programming/Languages/Objective-C'
		assert node.get_parent() == parent
