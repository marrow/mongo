# encoding: utf-8

"""GeoJSON support for Marrow Mongo."""

from __future__ import unicode_literals

from collections import MutableSequence
from numbers import Number as NumberABC

from . import Document, Field
from .field import Alias, Array, Number, String


class GeoJSON(Document):
	__type_store__ = 'type'
	
	kind = String('type', required=True)


class GeoJSONCoord(GeoJSON):
	coordinates = Array(Field(), default=lambda: [], assign=True)
	
	def __init__(self, *coords, **kw):
		kw['coordinates'] = list(self.to_foreign(i) for i in (coords if coords else kw.get('coordinates', [])))
		super(GeoJSONCoord, self).__init__(**kw)
	
	def to_native(self, value):
		return value
	
	def to_foreign(self, value):
		return list(getattr(value, 'coordinates', value))
	
	# Mutable Sequence Methods
	
	def insert(self, index, item):
		self.coordinates.insert(index, self.to_foreign(item))
	
	def append(self, item):
		self.coordinates.append(self.to_foreign(item))
	
	def extend(self, other):
		if isinstance(other, self.__class__):
			self.coordinates.extend(other.coordinates)
		else:
			self.coordinates.extend(self.to_foreign(i) for i in other)
	
	def __getitem__(self, item):
		if isinstance(item, NumberABC) or item.lstrip('-').isnumeric():
			return self.to_native(self.coordinates[int(item)])
		
		return super(GeoJSONCoord, self).__getitem__(item)
	
	def __setitem__(self, item, value):
		if isinstance(item, NumberABC) or item.lstrip('-').isnumeric():
			self.coordinates[int(item)] = self.to_foreign(value)
			return
		
		super(GeoJSONCoord, self).__setitem__(item, value)
	
	def __delitem__(self, item):
		if isinstance(item, NumberABC) or item.lstrip('-').isnumeric():
			del self.coordinates[int(item)]
			return
		
		super(GeoJSONCoord, self).__delitem__(item)
	
	def __len__(self):
		return len(self.coordinates)


MutableSequence.register(GeoJSONCoord)


class Point(GeoJSONCoord):
	"""A GeoJSON Point.
	
	Example:
	
		Point(40, 5)
		
		{ type: "Point", coordinates: [ 40, 5 ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#point
		http://geojson.org/geojson-spec.html#point
	"""
	
	kind = String('type', default='Point', assign=True)
	coordinates = Array(Number())
	
	lat = latitude = Alias('coordinates.1')
	long = longitude = Alias('coordinates.0')
	
	def __init__(self, longitude=0, latitude=0, **kw):
		super(Point, self).__init__(coordinates=kw.pop('coordinates', [longitude, latitude]), **kw)
	
	def to_foreign(self, value):
		return float(value)


class LineString(GeoJSONCoord):
	"""A GeoJSON LineString.
	
	Example:
	
		LineString((40, 5), (41, 6))
		
		{ type: "LineString", coordinates: [ [ 40, 5 ], [ 41, 6 ] ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#linestring
		http://geojson.org/geojson-spec.html#linestring
	"""
	
	kind = String('type', default='LineString', assign=True)
	coordinates = Array(Array(Number()))
	
	def to_native(self, value):
		return Point(*(getattr(value, 'coordinates', value)))


class Polygon(GeoJSONCoord):
	"""A GeoJSON Polygon.
	
	Example:
	
		Polygon([(0, 0), (3, 6), (6, 1), (0, 0)])
		
		{
			type: "Polygon",
			coordinates: [ [ [ 0 , 0 ] , [ 3 , 6 ] , [ 6 , 1 ] , [ 0 , 0  ] ] ]
		}
	
		{
			type : "Polygon",
			coordinates : [
				[ [ 0 , 0 ] , [ 3 , 6 ] , [ 6 , 1 ] , [ 0 , 0 ] ],
				[ [ 2 , 2 ] , [ 3 , 3 ] , [ 4 , 2 ] , [ 2 , 2 ] ]
			]
		}
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#polygon
		http://geojson.org/geojson-spec.html#polygon
	"""
	
	kind = String('type', default='Polygon', assign=True)
	coordinates = Array(Array(Array(Number())))
	
	exterior = Alias('coordinates.0')
	
	def to_native(self, value):
		return LineString(*(getattr(value, 'coordinates', value)))


class MultiPoint(GeoJSONCoord):
	"""A GeoJSON MultiPoint.
	
	Example:
	
		MultiPoint((-73.9580, 40.8003), (-73.9498, 40.7968), (-73.9737, 40.7648), (-73.9814, 40.7681))
		
		{
			type: "MultiPoint",
			coordinates: [
				[ -73.9580, 40.8003 ],
				[ -73.9498, 40.7968 ],
				[ -73.9737, 40.7648 ],
				[ -73.9814, 40.7681 ]
			]
		}
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#multipoint
		http://geojson.org/geojson-spec.html#multipoint
	"""
	
	kind = String('type', default='MultiPoint', assign=True)
	coordinates = Array(Array(Number()))
	
	def to_native(self, value):
		return Point(*(getattr(value, 'coordinates', value)))


class MultiLineString(GeoJSONCoord):
	"""A GeoJSON MultiLineString.
	
	Example:
	
		MultiLineString([(-73.96943, 40.78519), (-73.96082, 40.78095)], [(-73.96415, 40.79229), (-73.95544, 40.78854)],
				[(-73.97162, 40.78205), (-73.96374, 40.77715)], [(-73.97880, 40.77247), (-73.97036, 40.76811)])
		
		{
			type: "MultiLineString",
			coordinates: [
				[ [ -73.96943, 40.78519 ], [ -73.96082, 40.78095 ] ],
				[ [ -73.96415, 40.79229 ], [ -73.95544, 40.78854 ] ],
				[ [ -73.97162, 40.78205 ], [ -73.96374, 40.77715 ] ],
				[ [ -73.97880, 40.77247 ], [ -73.97036, 40.76811 ] ]
			]
		}
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#multilinestring
		http://geojson.org/geojson-spec.html#multilinestring
	"""
	
	kind = String('type', default='MultiLineString', assign=True)
	coordinates = Array(Array(Array(Number())))
	
	def to_native(self, value):
		return LineString(*(getattr(value, 'coordinates', value)))


class MultiPolygon(GeoJSONCoord):
	"""A GeoJSON MultiPolygon.
	
	Example:
	
		{
			type: "MultiPolygon",
			coordinates: [
				[ [ [ -73.958, 40.8003 ], [ -73.9498, 40.7968 ], [ -73.9737, 40.7648 ], [ -73.9814, 40.7681 ],
						[ -73.958, 40.8003 ] ] ],
				[ [ [ -73.958, 40.8003 ], [ -73.9498, 40.7968 ], [ -73.9737, 40.7648 ], [ -73.958, 40.8003 ] ] ]
			]
		}
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#multipolygon
		http://geojson.org/geojson-spec.html#multipolygon
	"""
	
	kind = String('type', default='MultiPolygon', assign=True)
	coordinates = Array(Array(Array(Array(Number()))))
	
	def to_native(self, value):
		return Polygon(*(getattr(value, 'coordinates', value)))


class GeometryCollection(GeoJSON):
	"""A GeoJSON GeometryCollection.
	
	Example:
	
		{
			type: "GeometryCollection",
			geometries: [
				{
					type: "MultiPoint",
					coordinates: [
						[ -73.9580, 40.8003 ],
						[ -73.9498, 40.7968 ],
						[ -73.9737, 40.7648 ],
						[ -73.9814, 40.7681 ]
					]
				},
				{
					type: "MultiLineString",
					coordinates: [
						[ [ -73.96943, 40.78519 ], [ -73.96082, 40.78095 ] ],
						[ [ -73.96415, 40.79229 ], [ -73.95544, 40.78854 ] ],
						[ [ -73.97162, 40.78205 ], [ -73.96374, 40.77715 ] ],
						[ [ -73.97880, 40.77247 ], [ -73.97036, 40.76811 ] ]
					]
				}
			]
		}
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#geometrycollection
		http://geojson.org/geojson-spec.html#geometrycollection
	"""
	
	kind = String('type', default='GeometryCollection', assign=True)
	geometries = Array(GeoJSONCoord, default=lambda: [], assign=True)
	
	def __init__(self, *geometries, **kw):
		super(GeometryCollection, self).__init__(geometries=list(geometries), **kw)
