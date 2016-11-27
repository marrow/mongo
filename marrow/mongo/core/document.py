# encoding: utf-8

from __future__ import unicode_literals

from collections import MutableMapping

from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from bson.json_util import dumps, loads
from bson.tz_util import utc
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from ...package.loader import load
from ...schema import Attributes, Container
from ...schema.compat import odict
from ..util import SENTINEL
from .field import Field
from .index import Index

__all__ = ['Document']


class Document(Container):
	"""A MongoDB document definition.
	
	This is the top-level class your own document schemas should subclass. They may also subclass eachother; field
	declaration order is preserved, with subclass fields coming after those provided by the parent class(es). Any
	fields redefined will have their original position preserved.
	
	Documents may be bound to a PyMongo `Collection` instance, allowing for easier identification of where a document
	has been loaded from, and to allow reloading and loading of previously un-projected data. This is not meant to
	implement a full Active Record pattern; no `save` method or similar is provided. (You are free to add one
	yourself, of course!)
	"""
	
	# Note: These may be dynamic based on content; always access from an instance where possible.
	__store__ = odict # For fields, this may be a bson type like Binary, or Code.
	__foreign__ = {'object'}  # The representation for the database side of things, ref: $type
	__type_store__ = '_cls'  # The pseudo-field to store embedded document class references as.
	
	__bound__ = False  # Has this class been "attached" to a live MongoDB connection?
	__collection__ = None  # The name of the collection to "attach" to using bind().
	__read_preference__ = ReadPreference.PRIMARY  # Default read preference to assign when binding.
	__read_concern__ = ReadConcern()  # Default read concern.
	__write_concern__ = WriteConcern(w=1)  # Default write concern.
	__capped__ = False  # The size of the capped collection to create in bytes.
	__capped_count__ = None  # The optional number of records to limit the capped collection to.
	__engine__ = None  # Override the default storage engine (and configuration) as a mapping of `{name: options}`.
	__validate__ = 'off'  # Control validation strictness: off, strict, or moderate.
	
	__projection__ = None  # The set of fields used during projection, to identify fields which are not loaded.
	__validator__ = None  # The MongoDB Validation document matching these records.
	__fields__ = Attributes(only=Field)  # An ordered mapping of field names to their respective Field instance.
	__fields__.__sequence__ = 10000
	__indexes__ = Attributes(only=Index)  # An ordered mapping of index names to their respective Index instance.
	__indexes__.__sequence__ = 10000
	
	def __init__(self, *args, **kw):
		"""Construct a new MongoDB Document instance.
		
		Utilizing Marrow Schema, arguments may be passed positionally (in definition order) or by keyword, or using a
		mixture of the two. Any fields marked for automatic assignment will be automatically accessed to trigger such
		assignment.
		"""
		
		prepare_defaults = kw.pop('_prepare_defaults', True)
		
		super(Document, self).__init__(*args, **kw)
		
		if prepare_defaults:
			self._prepare_defaults()
	
	@classmethod
	def _get_default_projection(cls):
		"""Construct the default projection document."""
		
		projected = []  # The fields explicitly requested for inclusion.
		neutral = []  # Fields returning neutral (None) status.
		omitted = False  # Have any fields been explicitly omitted?
		
		for name, field in cls.__fields__.items():
			if field.project is None:
				neutral.append(name)
			elif field.project:
				projected.append(name)
			else:
				omitted = True
		
		if not projected and not omitted:
			# No preferences specified.
			return None
			
		elif not projected and omitted:
			# No positive inclusions given, but negative ones were.
			projected = neutral
		
		return {name: True for name in projected}
	
	@classmethod
	def __attributed__(cls):
		"""Executed after each new subclass is constructed."""
		
		cls.__projection__ = cls._get_default_projection()
	
	def _prepare_defaults(self):
		"""Trigger assignment of default values."""
		
		for name, field in self.__fields__.items():
			if field.assign:
				getattr(self, name)
	
	@classmethod
	def bind(cls, db=None, collection=None):
		"""Bind a copy of the collection to the class, modified per our class' settings."""
		
		if db is collection is None:
			raise ValueError("Must bind to either a database or explicit collection.")
		
		collection = cls.get_collection(db or collection)
		
		cls.__bound__ = True
		cls._collection = collection
		
		return cls
	
	# Database Operations
	
	@classmethod
	def _collection_configuration(cls, creation=False):
		config = {
				'codec_options': CodecOptions(
						document_class = cls.__store__,
						tz_aware = True,
						uuid_representation = STANDARD,
						tzinfo = utc,
					),
				'read_preference': cls.__read_preference__,
				'read_concern': cls.__read_concern__,
				'write_concern': cls.__write_concern__,
			}
		
		if not creation:
			return config
		
		if cls.__capped__:
			config['size'] = cls.__capped__
			config['capped'] = True
			
			if cls.__capped_count__:
				config['max'] = cls.__capped_count__
		
		if cls.__engine__:
			config['storageEngine'] = cls.__engine__
		
		if cls.__validate__ != 'off':
			config['validator'] = cls.__validator__
			config['validationLevel'] = 'strict' if cls.__validate__ is True else cls.__validate__
		
		return config
	
	@classmethod
	def create_collection(cls, target, recreate=False, indexes=True):
		"""Ensure the collection identified by this document class exists, creating it if not.
		
		http://api.mongodb.com/python/current/api/pymongo/database.html#pymongo.database.Database.create_collection
		"""
		
		if isinstance(target, Collection):
			name = target.name
			target = target.database
		else:
			name = cls.__collection__
		
		if recreate:
			target.drop_collection(name)
		
		collection = target.create_collection(name, **cls._collection_configuration(True))
		
		if indexes:
			cls.create_indexes(collection)
		
		return collection
	
	@classmethod
	def get_collection(cls, target):
		"""Retrieve a properly configured collection object as configured by this document class.
		
		If given an existing collection, will instead call `collection.with_options`.
		
		http://api.mongodb.com/python/current/api/pymongo/database.html#pymongo.database.Database.get_collection
		"""
		
		if isinstance(target, Collection):
			return target.with_options(**cls._collection_configuration())
		
		elif isinstance(target, Database):
			return target.get_collection(cls.__collection__, **cls._collection_configuration())
		
		raise TypeError("Can not retrieve collection from: " + repr(target))
	
	@classmethod
	def create_indexes(cls, target, recreate=False):
		"""Iterate all known indexes and construct them."""
		
		results = []
		collection = cls.get_collection(target)
		
		if recreate:
			collection.drop_indexes()
		
		for index in cls.__indexes__.values():
			results.append(index.create_index(collection))
		
		return results
	
	# Data Conversion and Casting
	
	@classmethod
	def from_mongo(cls, doc, projected=None):
		"""Convert data coming in from the MongoDB wire driver into a Document instance."""
		
		if isinstance(doc, Document):
			return doc
		
		if cls.__type_store__ in doc:  # Instantiate any specific class mentioned in the data.
			cls = load(doc[cls.__type_store__], 'marrow.mongo.document')
		
		instance = cls(_prepare_defaults=False)
		instance.__data__ = instance.__store__(doc)
		instance._prepare_defaults()  # pylint:disable=protected-access
		instance.__loaded__ = set(projected) if projected else None
		
		return instance
	
	@classmethod
	def from_json(cls, json):
		"""Convert JSON data into a Document instance."""
		
		deserialized = loads(json)
		return cls.from_mongo(deserialized)
	
	def to_json(self, *args, **kw):
		"""Convert our Document instance back into JSON data. Additional arguments are passed through."""
		
		return dumps(self, *args, **kw)
	
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
		"""Retrieve data from the backing store."""
		
		return self.__data__[name]
	
	def __setitem__(self, name, value):
		"""Assign data directly to the backing store."""
		
		self.__data__[name] = value
	
	def __delitem__(self, name):
		"""Unset a value from the backing store."""
		
		del self.__data__[name]
	
	def __iter__(self):
		"""Iterate the names of the values assigned to our backing store."""
		
		return iter(self.__data__.keys())
	
	def __len__(self):
		"""Retrieve the size of the backing store."""
		
		return len(getattr(self, '__data__', {}))
	
	def keys(self):
		"""Iterate the keys assigned to the backing store."""
		
		return self.__data__.keys()
	
	def items(self):
		"""Iterate 2-tuple pairs of (key, value) from the backing store."""
		
		return self.__data__.items()
	
	def iteritems(self):
		"""Python 2 interation, as per items."""
		
		return self.__data__.items()
	
	def values(self):
		"""Iterate the values within the backing store."""
		
		return self.__data__.values()
	
	def __contains__(self, key):
		"""Determine if the given key is present in the backing store."""
		
		return key in self.__data__
	
	def __eq__(self, other):
		"""Equality comparison between the backing store and other value."""
		
		return self.__data__ == other
	
	def __ne__(self, other):
		"""Inverse equality comparison between the backing store and other value."""
		
		return self.__data__ != other
	
	def get(self, key, default=None):
		"""Retrieve a value from the backing store with a default value."""
		
		return self.__data__.get(key, default)
	
	def clear(self):
		"""Empty the backing store of data."""
		
		self.__data__.clear()
	
	def pop(self, name, default=SENTINEL):
		"""Retrieve and remove a value from the backing store, optionally with a default."""
		
		if default is SENTINEL:
			return self.__data__.pop(name)
		
		return self.__data__.pop(name, default)
	
	def popitem(self):
		"""Pop an item 2-tuple off the backing store."""
		
		return self.__data__.popitem()
	
	def update(self, *args, **kw):
		"""Update the backing store directly."""
		
		self.__data__.update(*args, **kw)
	
	def setdefault(self, key, value=None):
		"""Set a value in the backing store if no value is currently present."""
		
		return self.__data__.setdefault(key, value)


MutableMapping.register(Document)  # Metaclass conflict if we subclass.
