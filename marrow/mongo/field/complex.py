# encoding: utf-8

from bson import ObjectId as oid
from collections import Iterable
from pkg_resources import iter_entry_points

from marrow.schema import Attribute
from marrow.package.loader import traverse, load

from ..core import Document, Field
from ..util import adjust_attribute_sequence
from ..util.compat import str, unicode


@adjust_attribute_sequence(-1000, 'kind')  # Allow 'kind' to be passed positionally first.
class _HasKinds(Field):
	"""A mix-in to provide an easily definable singular or plural set of document types."""
	
	kind = Attribute(default=None)  # One or more foreign model references, a string, Document subclass, or set of.
	
	@property
	def kinds(self):
		values = self.kind
		
		if not isinstance(values, Iterable):
			values = (values, )
		
		for value in values:
			if isinstance(value, (str, unicode)):
				value = load(value, 'marrow.mongo.document')
			
			yield value


class Embed(_HasKinds, Field):
	__foreign__ = 'object'
	
	def __init__(self, *kinds, **kw):
		kw['kind'] = kinds
		
		if kw.get('assign', False) and 'default' not in kw:
			if len(kinds) != 1:
				raise ValueError("If auto-assignment is selected, must specify only one allowed kind.")
			
			def embed_default():
				if isinstance(kinds[0], (str, unicode)):
					return load(kinds[0], 'marrow.mongo.document')
				return kinds[0]
			
			kw['default'] = embed_default
		
		super(Embed, self).__init__(**kw)
	
	def to_native(self, obj, name, value):
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		if not isinstance(value, Document):
			kinds = list(self.kinds)
			
			if len(kinds) == 1:
				value = kinds[0].from_mongo(value)
			else:
				value = Document.from_mongo(value)  # This handles _cls lookup.
		
		return value
	
	def to_foreign(self, obj, name, value):
		"""Transform to a MongoDB-safe value."""
		
		kinds = list(self.kinds)
		
		if not isinstance(value, Document):
			if len(kinds) != 1:
				raise ValueError("Ambigouous assignment, assign an instance of: " + \
						", ".join(kind.__name__ for kind in kinds))
			
			value = kinds[0](**value)
			# DISCUSS: value.__data__.update(value) instead?
		
		if '_cls' not in value and len(kinds) != 1:
			value['_cls'] = name(value.__class__)
		
		return value


class Reference(_HasKinds, Field):
	concrete = Attribute(default=False)  # If truthy, will store a DBRef instead of ObjectId.
	cache = Attribute(default=None)  # Attributes to preserve from the referenced object at the reference level.
	reverse = Attribute(default=None)  # What to assign as a reverse accessor?
	
	@property
	def __foreign__(self):
		"""Advertise that we store a simple reference, or deep reference, or object, depending on configuration."""
		
		if not self.cache:
			if self.concrete:
				return 'dbPointer'
			
			return 'objectId'
		
		return 'object'
	
	def to_native(self, obj, name, value):
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		# Identify the 
		kinds = list(self.kinds)
		
		if isinstance(value, oid):
			return value
		
		# Return a partially populated record based on our cached values.
		return kinds[0].from_mongo(value, value.keys())
	
	def to_foreign(self, obj, name, value):
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
		
		if not cache and self.cache and not issubclass(self.kind, Document):
			raise ValueError("Passed an identifier (not a Document instance) when multiple document kinds registered.")
		
		if self.cache:
			raise NotImplementedError()
			
			if not cache:
				raise NotImplementedError()  # TODO: Load values to cache.
			
			store = {'_id': identifier, '_cls': name(self.kind)}
			
			for i in self.cache:
				store[self.__document__._get_mongo_name_for(i)] = traverse(cache, i)
		
		return store


@adjust_attribute_sequence(-1000, 'namespace')  # Allow the namespace to be defined first.
class PluginReference(Field):
	"""A Python object reference.
	
	Generally, for safety sake, you want this to come from a list of available plugins in a given namespace. If a
	namespace is given, the default for `explicit` will be `False`.  If `explicit` is `True` (or no namespace is
	defined) object assignments and literal paths will be allowed.
	"""
	
	namespace = Attribute()  # The plugin namespace to use when loading.
	explicit = Attribute()  # Allow explicit, non-plugin references.
	
	__foreign__ = {'string'}
	
	def to_native(self, obj, name, value):
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		try:
			namespace = self.namespace
		except AttributeError:
			namespace = None
		
		return load(value, namespace) if namespace else load(value)
	
	def to_foreign(self, obj, name, value):
		"""Transform to a MongoDB-safe value."""
		
		try:
			namespace = self.namespace
		
		except AttributeError:
			namespace = None
			
			if __debug__:
				names = {}
				plugins = {}
		
		else:
			if __debug__:
				names = {i.name: i.load() for i in iter_entry_points(namespace)}
				plugins = {j: i for i, j in names.items()}
		
		try:
			explicit = self.explicit
		except AttributeError:
			explicit = not bool(namespace)
		
		if isinstance(value, (str, unicode)):
			if ':' in value:
				if not explicit:
					raise ValueError("Explicit object references not allowed.")
				
			elif __debug__ and namespace and value not in names:
				raise ValueError('Unknown plugin "' + value + '" for namespace "' + namespace + '".')
			
			return value
		
		if __debug__ and namespace and not explicit and value not in plugins:
			raise ValueError(repr(value) + ' object is not a known plugin for namespace "' + namespace + '".')
		
		return plugins.get(value, name(value))
