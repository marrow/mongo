# encoding: utf-8

from bson import ObjectId as oid
from marrow.schema import Attribute
from marrow.schema.transform import BaseTransform
from marrow.package.canonical import name
from marrow.package.loader import traverse

from ..core import Document, Field
from ..util import adjust_attribute_sequence
from ..util.compat import str, unicode



@adjust_attribute_sequence(-1000, 'kind')  # Allow 'kind' to be passed positionally first.
class Embed(Field):
	kind = Attribute(default=None)  # The Document class (or set of allowable) to use when unpacking.
	
	__foreign__ = 'object'



class ReferenceTransform(BaseTransform):
	def foreign(self, value, field):
		"""Transform to a MongoDB-safe value."""
		
		cache = None
		
		# First, we handle the typcial Document object case.
		if isinstance(value, Document):
			cache = value
			identifier = getattr(value, 'id', None)
			if identifier is None:
				raise ValueError("Can only store a reference to a saved Document instance with an `id`.")
		
		elif isinstance(value, (str, unicode)) and len(value) == 24:
			try:
				identifier = oid(value)
			except:
				identifier = value
		
		if not cache and field.cache and not issubclass(field.kind, Document):
			raise ValueError("Passed an identifier (not a Document instance) when multiple document kinds registered.")
		
		if field.cache:
			raise NotImplementedError()
			
			if not cache:
				raise NotImplementedError()  # TODO: Load values to cache.
			
			store = {'_id': identifier, '_cls': name(field.kind)}
			
			for i in field.cache:
				store[field.__document__._get_mongo_name_for(i)] = traverse(cache, i)
	
	def native(self, value, field):
		"""Transform the MongoDB value into a Marrow Mongo value."""
		pass


@adjust_attribute_sequence(-1000, 'kind')  # Allow 'kind' to be passed positionally first.
class Reference(Field):
	kind = Attribute(default=None)  # One or more foreign model references, a string, Document subclass, or set of.
	concrete = Attribute(default=False)  # If truthy, will store a DBRef instead of ObjectId.
	cache = Attribute(default=None)  # Attributes to preserve from the referenced object at the reference level.
	
	__foreign__ = {'objectId', 'dbPointer', 'object'}  # We store a simple reference, or deep reference, or object.

