# encoding: utf-8

from __future__ import unicode_literals

from collections import Iterable, Mapping
from weakref import proxy

from bson import ObjectId as OID
from bson import DBRef
from bson.errors import InvalidId
from pkg_resources import iter_entry_points

from .. import Document, Field
from ....package.canonical import name as canon
from ....package.loader import load, traverse
from ....schema import Attribute
from ....schema.compat import odict, str, unicode


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
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		if not isinstance(value, Document):
			
			kinds = list(self.kinds)
			
			if len(kinds) == 1:
				if hasattr(kinds[0], 'transformer'):
					value = kinds[0].transformer.native(value, (kinds[0], obj))
				else:
					value = kinds[0].from_mongo(value)
			else:
				value = Document.from_mongo(value)  # TODO: Pass in allowed classes.
		
		return value
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		"""Transform to a MongoDB-safe value."""
		
		kinds = list(self.kinds)
		
		if not isinstance(value, Document):
			if len(kinds) != 1:
				raise ValueError("Ambigouous assignment, assign an instance of: " + \
						", ".join(repr(kind) for kind in kinds))
			
			kind = kinds[0]
			
			# Attempt to figure out what to do with the value.
			if isinstance(kind, Field):
				kind.__name__ = self.__name__
				return kind.transformer.foreign(value, (kind, obj))
			
			value = kind(**value)
		
		if isinstance(value, Document) and value.__type_store__ not in value and len(kinds) != 1:
			value[value.__type_store__] = canon(value.__class__)  # Automatically add the tracking field.
		
		return value


class Array(_HasKinds, _CastingKind, Field):
	__foreign__ = 'array'
	__allowed_operators__ = {'#array', '$elemMatch'}
	
	class List(list):
		pass
	
	def to_native(self, obj, name, value):
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		if isinstance(value, self.List):
			return value
		
		result = self.List(super(Array, self).to_native(obj, name, i) for i in value)
		obj.__data__[self.__name__] = result
		
		return result
	
	def to_foreign(self, obj, name, value):
		"""Transform to a MongoDB-safe value."""
		
		return self.List(super(Array, self).to_foreign(obj, name, i) for i in value)


class Embed(_HasKinds, _CastingKind, Field):
	__foreign__ = 'object'
	__allowed_operators__ = {'#document'}
	
	def to_native(self, obj, name, value):
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		if isinstance(value, Document):
			return value
		
		result = super(Embed, self).to_native(obj, name, value)
		obj.__data__[self.__name__] = result
		
		return result
	
	def to_foreign(self, obj, name, value):
		"""Transform to a MongoDB-safe value."""
		
		result = super(Embed, self).to_foreign(obj, name, value)
		return result


class Reference(_HasKinds, Field):
	concrete = Attribute(default=False)  # If truthy, will store a DBRef instead of ObjectId.
	cache = Attribute(default=None)  # Attributes to preserve from the referenced object at the reference level.
	
	@property
	def __foreign__(self):
		"""Advertise that we store a simple reference, or deep reference, or object, depending on configuration."""
		
		if self.cache:
			return 'object'
		
		if self.concrete:
			return 'dbPointer'
		
		return 'objectId'
	
	def _populate_cache(self, value):
		inst = odict()
		
		if isinstance(value, Document):
			try:
				inst['_id'] = value.__data__['_id']
				inst[value.__type_store__] = canon(value.__class__)
			except KeyError:
				raise ValueError("Must reference a document with an _id.")
		
		elif isinstance(value, Mapping):
			try:
				inst['_id'] = value['_id']
			except KeyError:
				raise ValueError("Must reference a document with an _id.")
		
		elif isinstance(value, OID):
			inst['_id'] = value
		
		elif isinstance(value, (str, unicode)) and len(value) == 24:
			try:
				inst['_id'] = OID(value)
			except InvalidId:
				raise ValueError("Not referenceable: " + repr(value))
		
		else:
			raise ValueError("Not referenceable: " + repr(value))
		
		for field in self.cache:
			if __debug__:  # This verification is potentially expensive, so skip it in production.
				if any(chunk.isnumeric() for chunk in field.split('.')):
					raise ValueError("May not contain numeric array references.")
			
			try:
				nested = traverse(value, field)
				
			except LookupError:
				pass
			
			else:
				current = inst
				parts = field.split('.')
				
				for part in parts[:-1]:
					current = current.setdefault(part, odict())
				
				current[parts[-1]] = nested
		
		return inst
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		"""Transform to a MongoDB-safe value."""
		
		if self.cache:
			return self._populate_cache(value)
		
		# First, we handle the typcial Document object case.
		if isinstance(value, Document):
			identifier = value.__data__.get('_id', None)
			if identifier is None:
				raise ValueError("Can only store a reference to a saved Document instance with an `_id` stored.")
		
		elif isinstance(value, (str, unicode)) and len(value) == 24:
			try:
				identifier = OID(value)
			except InvalidId:
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
	
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		try:
			namespace = self.namespace
		except AttributeError:
			namespace = None
		
		return load(value, namespace) if namespace else load(value)
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
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
	
	def __init__(self, path):
		super(Alias, self).__init__(path=path)
	
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
