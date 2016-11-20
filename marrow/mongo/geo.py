# encoding: utf-8

"""GeoJSON support for Marrow Mongo."""

from weakref import proxy

from marrow.package.loader import traverse
from marrow.schema import Attribute

from . import Document
from .query import Q
from .field import String, Array, Number


class IndexedSubfield(Attribute):
	"""Allow for more direct access to arrays of fixed lengths.
	
	This allows for far more direct access to a target field's array element; it is a shortcut for an `@property`
	solution that works for instance access (both retrieval and assignment) as well as class-based access for the
	construction of a relevant `Q` proxy.
	"""
	
	path = Attribute()
	path.__sequence__ -= 10000
	
	def __fixup__(self, document):
		"""Called after an instance of our Field class is assigned to a Document."""
		self.__document__ = proxy(document)
	
	def __get__(self, obj, cls=None):
		if obj is None:
			parts = self.path.split('.')
			current = cls
			
			for part in parts:
				if part.isnumeric():
					current = Q(current._document, list(current._field.kinds)[0])
					current._name = current._name + '.' + part
					continue
				
				current = getattr(current, part)
			
			return current
		
		return traverse(obj, self.path)
	
	def __set__(self, obj, value):
		parts = self.path.split('.')
		final = parts.pop()
		current = obj
		
		for part in parts:
			if part.isnumeric():
				current = current[int(part)]
				continue
			
			current = getattr(current, part)
		
		if final.isnumeric():
			current[int(final)] = value
		else:
			setattr(current, final, value)


class Point(Document):
	__allowed_operators__ = {'#geo'}
	
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	
	lat = latitude = IndexedSubfield('coordinates.1')
	long = longitude = IndexedSubfield('coordinates.0')
	
	def __init__(self, longitude=0, latitude=0):
		return super(Point, self).__init__(coordinates=[longitude, latitude])
