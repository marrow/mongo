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
		assert p.coordinates == [27, 42]
	
	def test_aliases(self, p):
		assert p.lat == 42
		assert p.long == 27
	
	def test_replacement(self, p):
		assert p[0] == 27
		p[0] = -27
		assert p.coordinates == [-27, 42]
	
	def test_conversion(self, p):
		assert dict(p) == {'type': 'Point', 'coordinates': [27, 42]}


class TestLineStringField(object):
	D = LineString
	
	@pytest.fixture
	def ls(self):
		return self.D((40, 5), (41, 6))
	
	def test_constructor(self, ls):
		assert isinstance(ls, self.D)
		assert ls.coordinates == ls.coordinates == [[40, 5], [41, 6]]
	
	def test_point_access(self, ls):
		assert isinstance(ls[0], Point)
		assert ls[0].coordinates == [40, 5]


class TestPolygonField(object):
	D = Polygon
	
	@pytest.fixture
	def p(self):
		return self.D([(0, 0), (3, 6), (6, 1), (0, 0)])
	
	def test_constructor(self, p):
		assert isinstance(p, self.D)
		assert p.coordinates == [[[0 , 0] , [3 , 6] , [6 , 1] , [0 , 0]]]
	
	def test_linestring_access(self, p):
		assert isinstance(p[0], LineString)
		assert p[0].coordinates == [[0 , 0] , [3 , 6] , [6 , 1] , [0 , 0]]


class TestMultiPointField(object):
	D = MultiPoint
	
	@pytest.fixture
	def mp(self):
		return self.D((-73.9580, 40.8003), (-73.9498, 40.7968), (-73.9737, 40.7648), (-73.9814, 40.7681))
	
	def test_constructor(self, mp):
		assert isinstance(mp, self.D)
		assert mp.coordinates == [
				[-73.9580, 40.8003], [-73.9498, 40.7968], [-73.9737, 40.7648], [-73.9814, 40.7681]]
	
	def test_point_access(self, mp):
		assert isinstance(mp[0], Point)
		assert mp[0].coordinates == [-73.9580, 40.8003]


class TestMultiLineStringField(object):
	D = MultiLineString
	
	@pytest.fixture
	def mls(self):
		return self.D([(-73.96943, 40.78519), (-73.96082, 40.78095)], [(-73.96415, 40.79229), (-73.95544, 40.78854)],
				[(-73.97162, 40.78205), (-73.96374, 40.77715)], [(-73.97880, 40.77247), (-73.97036, 40.76811)])
	
	def test_constructor(self, mls):
		assert isinstance(mls, self.D)
		assert mls.coordinates == [
				[[-73.96943, 40.78519], [-73.96082, 40.78095]], [[-73.96415, 40.79229], [-73.95544, 40.78854]],
				[[-73.97162, 40.78205], [-73.96374, 40.77715]], [[-73.97880, 40.77247], [-73.97036, 40.76811]]]
	
	def test_linestring_access(self, mls):
		assert isinstance(mls[0], LineString)
		assert mls[0].coordinates == [[-73.96943, 40.78519], [-73.96082, 40.78095]]


class TestMultiPolygonField(object):
	D = MultiPolygon
	
	@pytest.fixture
	def mp(self):
		return self.D(
				[[[-73.958, 40.8003], [-73.9498, 40.7968], [-73.9737, 40.7648], [-73.9814, 40.7681],
						[-73.958, 40.8003]]],
				[[[-73.958, 40.8003], [-73.9498, 40.7968], [-73.9737, 40.7648], [-73.958, 40.8003]]]
			)
	
	def test_constructor(self, mp):
		assert isinstance(mp, self.D)
		assert mp.coordinates == [
				[[[-73.958, 40.8003], [-73.9498, 40.7968], [-73.9737, 40.7648], [-73.9814, 40.7681],
						[-73.958, 40.8003]]],
				[[[-73.958, 40.8003], [-73.9498, 40.7968], [-73.9737, 40.7648], [-73.958, 40.8003]]]]
	
	def test_polygon_access(self, mp):
		assert isinstance(mp[1], Polygon)
		assert mp[1].coordinates == [[[-73.958, 40.8003], [-73.9498, 40.7968], [-73.9737, 40.7648], [-73.958, 40.8003]]]


class TestGeometryCollectionField(object):
	D = GeometryCollection
	
	@pytest.fixture
	def gc(self):
		return self.D(
				MultiPoint((-73.9580, 40.8003), (-73.9498, 40.7968), (-73.9737, 40.7648), (-73.9814, 40.7681)),
				MultiLineString(
						[(-73.96943, 40.78519), (-73.96082, 40.78095)],
						[(-73.96415, 40.79229), (-73.95544, 40.78854)],
						[(-73.97162, 40.78205), (-73.96374, 40.77715)],
						[(-73.97880, 40.77247), (-73.97036, 40.76811)]
					)
			)
	
	def test_constructor(self, gc):
		assert isinstance(gc, self.D)
		v = dict(gc)
		v['geometries'] = [dict(i) for i in v['geometries']]
		
		assert v == {
			'type': "GeometryCollection",
			'geometries': [
				{
					'type': "MultiPoint",
					'coordinates': [
						[ -73.9580, 40.8003 ],
						[ -73.9498, 40.7968 ],
						[ -73.9737, 40.7648 ],
						[ -73.9814, 40.7681 ]
					]
				},
				{
					'type': "MultiLineString",
					'coordinates': [
						[ [ -73.96943, 40.78519 ], [ -73.96082, 40.78095 ] ],
						[ [ -73.96415, 40.79229 ], [ -73.95544, 40.78854 ] ],
						[ [ -73.97162, 40.78205 ], [ -73.96374, 40.77715 ] ],
						[ [ -73.97880, 40.77247 ], [ -73.97036, 40.76811 ] ]
					]
				}
			]
		}
