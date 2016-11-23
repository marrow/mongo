# encoding: utf-8

"""GeoJSON support for Marrow Mongo."""

from weakref import proxy

from marrow.package.loader import traverse
from marrow.schema import Attribute

from . import Document, Field
from .query import Q
from .field import String, Array, Number, Alias


class GeoJSON(Document):
	kind = String('type', required=True)
	coordinates = Array(Field(), default=lambda: [], assign=True)


class Point(GeoJSON):
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
	
	def __init__(self, longitude=0, latitude=0):
		return super(Point, self).__init__(coordinates=[longitude, latitude])


class LineString(GeoJSON):
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class Polygon(GeoJSON):
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class MultiPoint(GeoJSON):
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class MultiLineString(GeoJSON):
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class MultiPolygon(GeoJSON):
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	pass


class GeometryCollection(Document):
	kind = String('type', default='point', assign=True)
	geometries = Array(GeoJSON, default=lambda: [0, 0], assign=True)
	
	pass
