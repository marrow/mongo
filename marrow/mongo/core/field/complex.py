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


class _HasKind(Field):
	"""A mix-in to provide an easily definable singular or plural set of document types."""
	
	kind = Attribute(default=None)  # One or more foreign model references, a string, Document subclass, or set of.
	
	def __init__(self, *args, **kw):
		if args:
			kw['kind'], args = args[0], args[1:]
		
		super(_HasKind, self).__init__(*args, **kw)
	
	def __fixup__(self, document):
		super(_HasKind, self).__fixup__(document)
		
		kind = self.kind
		
		if not kind:
			return
		
		if isinstance(kind, Field):
			kind.__name__ = self.__name__
			kind.__document__ = proxy(document)
			kind.__fixup__(document)  # Chain this down to embedded fields.
	
	def _kind(self, document=None):
		kind = self.kind
		
		if isinstance(kind, (str, unicode)):
			if kind.startswith('.'):
				# This allows the reference to be dynamic.
				kind = traverse(document or self.__document__, kind[1:])
				
				if not isinstance(kind, (str, unicode)):
					return kind
			else:
				kind = load(kind, 'marrow.mongo.document')
		
		return kind


class _CastingKind(Field):
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		from marrow.mongo.trait import Derived
		
		kind = self._kind(obj.__class__)
		
		if isinstance(value, Document):
			if __debug__ and kind and issubclass(kind, Document) and not isinstance(value, kind):
				raise ValueError("Not an instance of " + kind.__name__ + " or a sub-class: " + repr(value))
			
			return value
		
		if isinstance(kind, Field):
			return kind.transformer.native(value, (kind, obj))
		
		return (kind or Derived).from_mongo(value)
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		"""Transform to a MongoDB-safe value."""
		
		kind = self._kind(obj.__class__)
		
		if isinstance(value, Document):
			if __debug__ and kind and issubclass(kind, Document) and not isinstance(value, kind):
				raise ValueError("Not an instance of " + kind.__name__ + " or a sub-class: " + repr(value))
			
			return value
		
		if isinstance(kind, Field):
			return kind.transformer.foreign(value, (kind, obj))
		
		if kind:
			value = kind(**value)
		
		return value


class Array(_HasKind, _CastingKind, Field):
	__foreign__ = 'array'
	__allowed_operators__ = {'#array', '$elemMatch', '$eq'}
	
	class List(list):
		"""Placeholder list shadow class to identify already-cast arrays."""
		
		@classmethod
		def new(cls):
			return cls()
	
	def __init__(self, *args, **kw):
		if kw.get('assign', False):
			kw.setdefault('default', self.List.new)
		
		super(Array, self).__init__(*args, **kw)
	
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


class Embed(_HasKind, _CastingKind, Field):
	__foreign__ = 'object'
	__allowed_operators__ = {'#document'}
	
	def __init__(self, *args, **kw):
		if args:
			kw['kind'], args = args[0], args[1:]
			kw.setdefault('default', lambda: self._kind()())
		
		super(Embed, self).__init__(*args, **kw)


class Reference(_HasKind, Field):
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
		
		identifier = value
		
		# First, we handle the typcial Document object case.
		if isinstance(value, Document):
			identifier = value.__data__.get('_id', None)
			if identifier is None:
				raise ValueError("Can only store a reference to a saved Document instance with an `_id` stored.")
		
		elif isinstance(value, (str, unicode)) and len(value) == 24:
			try:
				identifier = OID(value)
			except InvalidId:
				pass
		
		kind = self._kind(obj.__class__)
		
		if self.concrete:
			if isinstance(value, Document) and value.__collection__:
				return DBRef(value.__collection__, identifier)
			
			if kind and kind.__collection__:
				return DBRef(kind.__collection__, identifier)
			
			raise ValueError("Could not infer collection name.")
		
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
		
		try:
			explicit = self.explicit
		except AttributeError:
			explicit = not bool(namespace)
		
		if not isinstance(value, (str, unicode)):
			value = canon(value)
		
		if namespace and ':' in value:  # Try to reduce to a known plugin short name.
			for point in iter_entry_points(namespace):
				qualname = point.module_name
				
				if point.attrs:
					qualname += ':' + '.'.join(point.attrs)
				
				if qualname == value:
					value = point.name
					break
		
		if ':' in value:
			if not explicit:
				raise ValueError("Explicit object references not allowed.")
			
			return value
		
		if namespace and value not in (i.name for i in iter_entry_points(namespace)):
			raise ValueError('Unknown plugin "' + value + '" for namespace "' + namespace + '".')
		
		return value


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
