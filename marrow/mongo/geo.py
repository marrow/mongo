# encoding: utf-8

"""GeoJSON support for Marrow Mongo."""

from collections.abc import MutableSequence

from . import Document, Field
from .field import String, Array, Number, Alias


class GeoJSON(Document):
	kind = String('type', required=True)


class GeoJSONCoord(GeoJSON):
	coordinates = Array(Field(), default=lambda: [], assign=True)
	
	def __init__(self, *coords, **kw):
		kw['coordinates'] = list(self.to_native(i) for i in (coords if coords else kw.get('coordinates', [])))
		super(GeoJSONCoord, self).__init__(**kw)
	
	def to_native(self, value):
		return value
	
	def to_foreign(self, value):
		return list(value)
	
	# Mutable Sequence Methods
	
	def index(self, item):
		return self.coordinates.index(self.to_foreign(item))
	
	def count(self, item):
		return self.coordinates.count(self.to_foreign(item))
	
	def append(self, item):
		self.coordinates.append(self.to_foreign(item))
	
	def reverse(self):
		return reversed(self)
	
	def extend(self, other):
		if isinstance(other, self.__class__):
			self.coordinates.extend(other.coordinates)
		else:
			self.coordinates.extend(self.to_foreign(i) for i in other)
	
	def pop(self, item, default=None):
		return self.to_native(self.coordinates.pop(self.to_foreign(item), default))
	
	def remove(self, item):
		return self.coordinates.remove(self.to_foreign(item))
	
	def __contains__(self, item):
		return self.to_foreign(item) in self.coordinates
	
	def __iter__(self):
		return iter(self.to_native(i) for i in self.coordinates)
	
	def __reversed__(self):
		return (self.to_native(i) for i in reversed(self.coordinates))
	
	def __getitem__(self, item):
		return self.to_native(self.coordinates[item])
	
	def __setitem__(self, item, value):
		self.coordinates[item] = self.to_foreign(value)
	
	def __delitem__(self, item):
		del self.coordinates[self.to_foreign(item)]
	
	def __len__(self):
		return len(self.coordinates)
	
	def insert(self, index, item):
		self.coordinates.insert(index, self.to_foreign(item))


MutableSequence.register(GeoJSONCoord)


class Point(GeoJSONCoord):
	"""A GeoJSON Point.
	
	Example:
	
		{ type: "Point", coordinates: [ 40, 5 ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#point
		http://geojson.org/geojson-spec.html#point
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number())
	
	lat = latitude = Alias('coordinates.1')
	long = longitude = Alias('coordinates.0')
	
	def __init__(self, longitude=0, latitude=0, **kw):
		super(Point, self).__init__(coordinates=kw.pop('coordinates', [longitude, latitude]), **kw)
	
	def to_foreign(self, value):
		return value


class LineString(GeoJSONCoord):
	"""A GeoJSON LineString.
	
	Example:
	
		{ type: "LineString", coordinates: [ [ 40, 5 ], [ 41, 6 ] ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#linestring
		http://geojson.org/geojson-spec.html#linestring
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Array(Number()))
	
	def to_native(self, value):
		return Point(*value)


class Polygon(GeoJSONCoord):
	"""A GeoJSON Polygon.
	
	Example:
	
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
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Array(Array(Number())))
	
	exterior = Alias('coordinates.0')
	
	def to_native(self, value):
		return LineString(*value)


class MultiPoint(GeoJSONCoord):
	"""A GeoJSON MultiPoint.
	
	Example:
	
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
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Array(Number()))
	
	def to_native(self, value):
		return Point(*value)


class MultiLineString(GeoJSONCoord):
	"""A GeoJSON MultiLineString.
	
	Example:
	
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
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Array(Array(Number())))
	
	def to_native(self, value):
		return LineString(*value)


class MultiPolygon(GeoJSONCoord):
	"""A GeoJSON MultiPolygon.
	
	Example:
	
		{
			type: "MultiPolygon",
			coordinates: [
				[ [ [ -73.958, 40.8003 ], [ -73.9498, 40.7968 ], [ -73.9737, 40.7648 ], [ -73.9814, 40.7681 ], [ -73.958, 40.8003 ] ] ],
				[ [ [ -73.958, 40.8003 ], [ -73.9498, 40.7968 ], [ -73.9737, 40.7648 ], [ -73.958, 40.8003 ] ] ]
			]
		}
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#multipolygon
		http://geojson.org/geojson-spec.html#multipolygon
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Array(Array(Array(Number()))))
	
	def to_native(self, value):
		return Polygon(*value)


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
	
	kind = String('type', default='point', assign=True)
	geometries = Array(GeoJSONCoord, default=lambda: [], assign=True)
	
	def __init__(self, *geometries, **kw):
		super(GeometryCollection, self).__init__(geometries=list(geometries), **kw)
