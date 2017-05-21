# encoding: utf-8

from __future__ import unicode_literals

from weakref import proxy

from ....package.loader import traverse
from ....schema import Attribute


class Alias(Attribute):
	"""Reference a field, potentially nested, elsewhere in the document.
	
	This provides a shortcut for querying nested fields, for example, in GeoJSON, to more easily access the latitude
	and longitude:
	
		class Point(Document):
			kind = String('type', default='point', assign=True)
			coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
			latitude = Alias('coordinates.1')
			longitude = Alias('coordinates.0')
	
	You can now read and write `latitude` and `longitude` on instances of `Point`, as well as query the nested values
	through class attribute access.
	"""
	
	path = Attribute()
	
	def __init__(self, path, **kw):
		super(Alias, self).__init__(path=path, **kw)
	
	def __fixup__(self, document):
		"""Called after an instance of our Field class is assigned to a Document."""
		
		self.__document__ = proxy(document)
	
	def __get__(self, obj, cls=None):
		if obj is None:
			return traverse(self.__document__, self.path)
		
		return traverse(obj, self.path)
	
	def __set__(self, obj, value):
		parts = self.path.split('.')
		final = parts.pop()
		current = obj
		
		for part in parts:
			if part.lstrip('-').isdigit():
				current = current[int(part)]
				continue
			
			current = getattr(current, part)
		
		if final.lstrip('-').isdigit():
			current[int(final)] = value
		else:
			setattr(current, final, value)
