# encoding: utf-8

from bson import DBRef, ObjectId as oid
from collections import Iterable
from pkg_resources import iter_entry_points

from marrow.schema import Attribute
from marrow.package.canonical import name as canon
from marrow.package.loader import traverse, load

from .. import Document, Field
from ...util.compat import str, unicode


class _HasKinds(Field):
	"""A mix-in to provide an easily definable singular or plural set of document types."""
	
	kind = Attribute(default=None)  # One or more foreign model references, a string, Document subclass, or set of.
	
	def __init__(self, *kinds, **kw):
		if kinds:
			kw['kind'] = kinds
		
		super(_HasKinds, self).__init__(**kw)
	
	@property
	def kinds(self):
		values = self.kind
		
		if isinstance(values, (str, unicode)) or not isinstance(values, Iterable):
			values = (values, )
		
		for value in values:
			if isinstance(value, (str, unicode)):
				value = load(value, 'marrow.mongo.document')
			
			yield value


class _CastingKind(Field):
	def to_native(self, obj, name, value):
		if not isinstance(value, Document):
			"""Transform the MongoDB value into a Marrow Mongo value."""
			
			kinds = list(self.kinds)
			
			if len(kinds) == 1:
				value = kinds[0].from_mongo(value)
			else:
				value = Document.from_mongo(value)  # TODO: Pass in allowed classes.
		
		return value
	
	def to_foreign(self, obj, name, value):
		"""Transform to a MongoDB-safe value."""
		
		kinds = list(self.kinds)
		
		if not isinstance(value, Document):
			if len(kinds) != 1:
				raise ValueError("Ambigouous assignment, assign an instance of: " + \
						", ".join(repr(kind) for kind in kinds))
			
			value = kinds[0](**value)  # We're going from Python-land to MongoDB, we like instantiation.
		
		if '_cls' not in value and len(kinds) != 1:  # Automatically add the tracking field.
			value['_cls'] = canon(value.__class__)  # TODO: Optimize down to registered plugin name if possible.
		
		return value


class Array(_HasKinds, _CastingKind, Field):
	__foreign__ = 'array'
	__allowed_operators__ = {'#array', '$elemMatch'}
	
	def to_native(self, obj, name, value):
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		return [super(Array, self).to_native(obj, name, i) for i in value]
	
	def to_foreign(self, obj, name, value):
		"""Transform to a MongoDB-safe value."""
		
		return [super(Array, self).to_foreign(obj, name, i) for i in value]


class Embed(_HasKinds, _CastingKind, Field):
	__foreign__ = 'object'
	__allowed_operators__ = {'#document'}


class Reference(_HasKinds, Field):
	concrete = Attribute(default=False)  # If truthy, will store a DBRef instead of ObjectId.
	#cache = Attribute(default=None)  # Attributes to preserve from the referenced object at the reference level.
	
	@property
	def __foreign__(self):
		"""Advertise that we store a simple reference, or deep reference, or object, depending on configuration."""
		
		#if not self.cache:
		if self.concrete:
			return 'dbPointer'
		
		return 'objectId'
		
		#return 'object'
	
	def to_foreign(self, obj, name, value):
		"""Transform to a MongoDB-safe value."""
		
		# First, we handle the typcial Document object case.
		if isinstance(value, Document):
			identifier = value.__data__.get('_id', None)
			if identifier is None:
				raise ValueError("Can only store a reference to a saved Document instance with an `_id` stored.")
		
		elif isinstance(value, (str, unicode)) and len(value) == 24:
			try:
				identifier = oid(value)
			except:
				identifier = value
		
		kinds = list(self.kinds)
		
		if not isinstance(value, Document) and len(kinds) > 1:
			raise ValueError("Passed an identifier (not a Document instance) when multiple document kinds registered.")
		
		if self.concrete:
			if isinstance(value, Document):
				return DBRef(value.__collection__, identifier)
			
			return DBRef(kinds[0].__collection__, identifier)
		
		return identifier


class PluginReference(Field):
	"""A Python object reference.
	
	Generally, for safety sake, you want this to come from a list of available plugins in a given namespace. If a
	namespace is given, the default for `explicit` will be `False`.  If `explicit` is `True` (or no namespace is
	defined) object assignments and literal paths will be allowed.
	"""
	
	namespace = Attribute()  # The plugin namespace to use when loading.
	explicit = Attribute()  # Allow explicit, non-plugin references.
	
	__foreign__ = {'string'}
	
	def __init__(self, *args, **kw):
		if args:
			kw['namespace'] = args[0]
			args = args[1:]
		
		super(PluginReference, self).__init__(*args, **kw)
	
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
				names = plugins = {}
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
		
		return plugins.get(value, canon(value))
