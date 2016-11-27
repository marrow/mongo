# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document
from marrow.mongo.document import (
		GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon)


class TestPointField(object):
	D = Point
	
	@pytest.fixture
	def p(self):
		return self.D(27, 42)
	
	def test_constructor(self, p):
		assert isinstance(p, self.D)
		assert list(p) == [27, 42]
	
	def test_aliases(self, p):
		assert p.lat == 42
		assert p.long == 27
	
	def test_replacement(self, p):
		assert p[0] == 27
		p[0] = -27
		assert list(p) == [-27, 42]


class TestLineStringField(object):
	D = LineString
	
	@pytest.fixture
	def ls(self):
		return self.D((40, 5), (41, 6))
	
	def test_constructor(self, ls):
		assert isinstance(ls, self.D)
		assert list(ls) == ls.coordinates == [[40, 5], [41, 6]]
	
	def test_point_access(self, ls):
		assert isinstance(ls[0], Point)
		assert list(ls[0]) == [40, 5]


class TestPolygonField(object):
	D = Polygon
	
	@pytest.fixture
	def p(self):
		return self.D([(0, 0), (3, 6), (6, 1), (0, 0)])
	
	pass


class TestMultiPointField(object):
	D = MultiPoint


class TestMultiLineStringField(object):
	D = MultiLineString


class TestMultiPolygonField(object):
	D = MultiPolygon


class TestGeometryCollectionField(object):
	D = GeometryCollection
