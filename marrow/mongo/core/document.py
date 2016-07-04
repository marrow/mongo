# encoding: utf-8

from pytz import utc
from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from pymongo.read_preferences import ReadPreference
from collections import OrderedDict as odict, MutableMapping

from marrow.package.loader import load
from marrow.schema import Container, Attributes

from .field import Field
from .index import Index
from ..util import SENTINEL
from ..util.compat import py3


class Document(Container):
	# Note: These may be dynamic based on content; always access from an instance where possible.
	__store__ = odict  # Internally, this is the representation used for the Python side of communication.
	__foreign__ = {'object'}  # The representation for the database side of things, ref: $type
	
	_bound = False
	__collection__ = None
	__read_preference__ = ReadPreference.PRIMARY
	
	__projected__ = None
	__fields__ = Attributes(only=Field)
	__fields__.__sequence__ = 20000
	__indexes__ = Attributes(only=Index)
	__indexes__.__sequence__ = 20001
	
	def __init__(self, *args, **kw):
		"""Construct a new MongoDB Document."""
		fields = self.__fields__ = self.__fields__  # This stores the result of lazy evaluation.
		super(Document, self).__init__(*args, **kw)
		
		# Trigger assignment of default values.
		for name, field in fields.items():
			if field.assign:
				getattr(self, name)
	
	@property
	def __field_names__(self):
		"""Generate the name of the fields defined on the current document.
		
		This is a dynamic property because this represents actual data-defined fields, not schema-defined.
		"""
		names = tuple(self.__fields__)
		
		# These are explicit field names, returned regardless of presence in the actual data.
		for name in names:  # Python 2 deprecation note: yield from
			yield name
		
		# These are aditional fields present in the underlying document.
		for name in self.__data__:
			if name in names: continue  # Skip documented fields.
			yield name
	
	@classmethod
	def bind(cls, db=None, collection=None):
		"""Bind a copy of the collection to the class, modified per our class' settings."""
		
		if db is collection is None:
			raise ValueError("Must bind to either a database or explicit collection.")
		
		if collection is None:
			collection = db[cls.__collection__]
		
		collection = collection.with_options(
				codec_options = CodecOptions(
						document_class = odict,
						tz_aware = True,
						uuid_representation = STANDARD,
						tzinfo = utc,
					),
				read_preference = cls.__read_preference__,
				read_concern = None,  # TODO: Class-level configuration.
				write_concern = None,  # TODO: Class-level configuration.
			)
		
		cls._bound = True
		cls.__collection__ = collection
		
		return cls
	
	@classmethod
	def _get_mongo_name_for(cls, name):
		current = cls
		
		if '__' in name:  # In case we're getting the name from a Django-style argument.
			name = name.replace('__', '.')
		
		path = []
		parts = name.split('.')
		
		while parts:
			part = parts.pop(0)
	
	@classmethod
	def from_mongo(cls, doc, projected=None):
		if '_cls' in doc:
			cls = load(doc['_cls'], 'marrow.mongo.model')
		
		instance = cls()
		instance.__data__ = instance.__store__(doc)
		instance.__loaded__ = projected
		
		return instance
	
	@property
	def as_rest(self):
		"""Prepare a REST API-safe version of this document.
		
		This, or your overridden version in subclasses, must return a value that `json.dumps` can process, with the
		assistance of PyMongo's `bson.json_util` extended encoding. For details on the latter bit, see:
		
		https://docs.mongodb.com/manual/reference/mongodb-extended-json/
		"""
		return self  # We're sufficiently dictionary-like to pass muster.
	
	# Mapping Protocol
	
	def __getitem__(self, name):
		return self.__data__[name]
	
	def __setitem__(self, name, value):
		self.__data__[name] = value
	
	def __delitem__(self, name):
		del self.__data__[name]
	
	def __iter__(self):
		return iter(self.__data__.keys())
	
	def __len__(self):
		return len(getattr(self, '__data__', {}))
	
	if py3:
		def keys(self):
			return self.__data__.keys()
		
		def items(self):
			return self.__data__.items()
		
		def values(self):
			return self.__data__.values()
	
	else:
		def keys(self):
			return self.__data__.iterkeys()
		
		def items(self):
			return self.__data__.iteritems()
		
		def values(self):
			return self.__data__.itervalues()
	
	def __contains__(self, key):
		return key in self.__data__
	
	def __eq__(self, other):
		return self.__data__ == other
	
	def __ne__(self, other):
		return self.__data__ != other
	
	def get(self, key, default=None):
		return self.__data__.get(key, default)
	
	def clear(self):
		self.__data__.clear()
	
	def pop(self, name, default=SENTINEL):
		if default is SENTINEL:
			return self.__data__.pop(name)
		
		return self.__data__.pop(name, default)
	
	def popitem(self):
		return self.__data__.popitem()
	
	def update(self, *args, **kw):
		self.__data__.update(*args, **kw)
	
	def setdefault(self, key, value=None):
		return self.__data__.setdefault(key, value)


MutableMapping.register(Document)  # Metaclass conflict if we subclass.
