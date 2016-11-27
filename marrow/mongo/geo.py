# encoding: utf-8

"""GeoJSON support for Marrow Mongo."""

from collections.abc import MutableSequence
from weakref import proxy

from marrow.package.loader import traverse
from marrow.schema import Attribute

from . import Document, Field
from .query import Q
from .field import String, Array, Number, Alias


class GeoJSON(Document):
	kind = String('type', required=True)


class GeoJSONCoord(GeoJSON):
	coordinates = Array(Field(), default=lambda: [], assign=True)
	
	def to_native(self, value):
		return value
	
	def to_foreign(self, value):
		return value
	
	# Mutable Sequence Methods
	
	def index(self, item):
		return self.coordinates.index(item)
	
	def count(self, item):
		return self.coordinates.count(item)
	
	def append(self, item):
		self.coordinates.append(item)
	
	def reverse(self, other):
		self.coordinates.reverse()
	
	def extend(self, other):
		if isinstance(other, GeoJSONCoord):
			self.coordinates.extend(other.coordinates)
		else:
			self.coordinates.extend(other)
	
	def pop(self, item, default=None):
		return self.to_native(self.coordinates.pop(item, default))
	
	def remove(self, item):
		return self.coordinates.remove(item)
	
	def __contains__(self, item):
		return item in self.coordinates
	
	def __iter__(self):
		return iter(self.coordinates)
	
	def __reversed__(self):
		return reversed(self.coordinates)
	
	def __getitem__(self, item):
		return self.to_native(self.coordinates[item])
	
	def __setitem__(self, item, value):
		self.coordinates[item] = value
	
	def __delitem__(self, item):
		del self.coordinates[item]
	
	def __len__(self):
		return len(self.coordinates)
	
	def insert(self, index, coord):
		self.coordinates.insert(index, coord)


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
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	lat = latitude = Alias('coordinates.1')
	long = longitude = Alias('coordinates.0')
	
	def __init__(self, longitude=0, latitude=0, **kw):
		return super(Point, self).__init__(coordinates=kw.pop('coordinates', [longitude, latitude]), **kw)


class LineString(GeoJSONCoord):
	"""A GeoJSON LineString.
	
	Example:
	
		{ type: "LineString", coordinates: [ [ 40, 5 ], [ 41, 6 ] ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#linestring
		http://geojson.org/geojson-spec.html#linestring
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [], assign=True)
	
	def __init__(self, *coords, **kw):
		self.coordinates = list(coords)
	
	pass


class Polygon(GeoJSONCoord):
	"""A GeoJSON Point.
	
	Example:
	
		{ type: "Point", coordinates: [ 40, 5 ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#point
		http://geojson.org/geojson-spec.html#point
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class MultiPoint(GeoJSONCoord):
	"""A GeoJSON Point.
	
	Example:
	
		{ type: "Point", coordinates: [ 40, 5 ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#point
		http://geojson.org/geojson-spec.html#point
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class MultiLineString(GeoJSONCoord):
	"""A GeoJSON Point.
	
	Example:
	
		{ type: "Point", coordinates: [ 40, 5 ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#point
		http://geojson.org/geojson-spec.html#point
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class MultiPolygon(GeoJSONCoord):
	"""A GeoJSON Point.
	
	Example:
	
		{ type: "Point", coordinates: [ 40, 5 ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#point
		http://geojson.org/geojson-spec.html#point
	"""
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class GeometryCollection(GeoJSON):
	"""A GeoJSON Point.
	
	Example:
	
		{ type: "Point", coordinates: [ 40, 5 ] }
	
	References:
	
		https://docs.mongodb.com/manual/reference/geojson/#point
		http://geojson.org/geojson-spec.html#point
	"""
	
	kind = String('type', default='point', assign=True)
	geometries = Array(GeoJSON, default=lambda: [0, 0], assign=True)
	
	pass
