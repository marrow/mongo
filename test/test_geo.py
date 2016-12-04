# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document
from marrow.mongo.document import (
		GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon)
from marrow.mongo.field import Embed


class TestPointField(object):
	D = Point
	
	@pytest.fixture
	def p(self):
		return self.D(27, 42)
	
	@pytest.fixture
	def S(self):
		class Sample(Document):
			field = Embed(Point)
		
		return Sample
	
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
	
	def test_near(self, S):
		q = S.field.near((20, 40), min=2, max=10)
		assert dict(q) == {'field': {'$near': {'$geometry': {'type': 'Point',
				'coordinates': [20, 40]}, '$minDistance': 2.0, '$maxDistance': 10.0}}}
	
	def test_intersects(self, S):
		q = S.field.intersects(Point(10, 15))
		assert dict(q) == {'field': {'$geoIntersects': {'$geometry': {'type': 'Point',
				'coordinates': [10, 15]}}}}
	
	def test_intersects_crs(self, S):
		q = S.field.intersects(Point(10, 15), 'urn:x-mongodb:crs:strictwinding:EPSG:4326')
		assert dict(q) == {'field': {'$geoIntersects': {'$geometry': {'type': 'Point',
				'coordinates': [10, 15], 'crs': {'type': "name", 'properties': {
				'name': "urn:x-mongodb:crs:strictwinding:EPSG:4326"}}}}}}
	
	def test_within_geometry(self, S):
		q = S.field.within(Point(10, 15), crs='urn:x-mongodb:crs:strictwinding:EPSG:4326')
		assert dict(q) == {'field': {'$geoWithin': {'$geometry': {'type': 'Point',
				'coordinates': [10, 15], 'crs': {'type': "name", 'properties': {
				'name': "urn:x-mongodb:crs:strictwinding:EPSG:4326"}}}}}}
	
	def test_within_center(self, S):
		q = S.field.within(center=(5, 10), radius=10)
		assert dict(q) == {'field': {'$geoWithin': {'$center': [[5, 10], 10]}}}
	
	def test_within_sphere(self, S):
		q = S.field.within(sphere=(5, 10), radius=10)
		assert dict(q) == {'field': {'$geoWithin': {'$centerSphere': [[5, 10], 10]}}}
	
	def test_within_box(self, S):
		q = S.field.within(box=[(5, 0), (0, 5)])
		assert dict(q) == {'field': {'$geoWithin': {'$box': [[5, 0], [0, 5]]}}}
	
	def test_within_polygon(self, S):
		q = S.field.within(polygon=[(1, 1), (2, 2), (1, 2), (1, 1)])
		assert dict(q) == {'field': {'$geoWithin': {'$polygon': [[1, 1], [2, 2], [1, 2], [1, 1]]}}}
	
	def test_within_error(self, S):
		with pytest.raises(TypeError):
			S.field.within()


class TestLineStringField(object):
	D = LineString
	
	@pytest.fixture
	def ls(self):
		return self.D((40, 5), (41, 6))
	
	def test_constructor(self, ls):
		assert isinstance(ls, self.D)
		assert ls.coordinates == [[40, 5], [41, 6]]
	
	def test_point_access(self, ls):
		assert isinstance(ls[0], Point)
		assert ls[0].coordinates == [40, 5]
	
	def test_insert(self, ls):
		ls.insert(0, (27, 42))
		assert ls.coordinates == [[27, 42], [40, 5], [41, 6]]
	
	def test_append(self, ls):
		ls.append((27, 42))
		assert ls.coordinates == [[40, 5], [41, 6], [27, 42]]
	
	def test_extend(self, ls):
		ls.extend([(27, 42)])
		assert ls.coordinates == [[40, 5], [41, 6], [27, 42]]
	
	def test_extend_similar(self, ls):
		ls.extend(ls)
		assert ls.coordinates == [[40, 5], [41, 6], [40, 5], [41, 6]]
	
	def test_setitem_passthrough(self, ls):
		ls['foo'] = 27
		assert dict(ls)['foo'] == 27
	
	def test_delitem(self, ls):
		del ls[1]
		assert ls.coordinates == [[40, 5]]
	
	def test_delitem_passthrough(self, ls):
		with pytest.raises(KeyError):
			del ls['foo']


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
