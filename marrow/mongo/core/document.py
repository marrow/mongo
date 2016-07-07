# encoding: utf-8

from pytz import utc
from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from bson.json_util import dumps, loads
from pymongo.read_preferences import ReadPreference
from collections import OrderedDict as dict, MutableMapping

from marrow.package.loader import load
from marrow.schema import Container, Attributes

from .field import Field
from .index import Index
from ..util import SENTINEL
from ..util.compat import py3


class Document(Container):
	"""A MongoDB document definition."""
	
	# Note: These may be dynamic based on content; always access from an instance where possible.
	__store__ = dict  # For fields, this may be a bson type like Binary, or Code.
	__foreign__ = {'object'}  # The representation for the database side of things, ref: $type
	
	__bound__ = False  # Has this class been "attached" to a live MongoDB connection?
	__collection__ = None  # The name of the collection to "attach" to using bind().
	__read_preference__ = ReadPreference.PRIMARY  # Default read preference to assign when binding.
	
	__projected__ = None  # The set of fields used during projection, to identify fields which are not loaded.
	__fields__ = Attributes(only=Field)  # An ordered mapping of field names to their respective Field instance.
	__fields__.__sequence__ = 20000
	__indexes__ = Attributes(only=Index)  # An ordered mapping of index names to their respective Index instance.
	__indexes__.__sequence__ = 20001
	
	def __init__(self, *args, **kw):
		"""Construct a new MongoDB Document instance.
		
		Utilizing Marrow Schema, arguments may be passed positionally (in definition order) or by keyword, or using a
		mixture of the two. Any fields marked for automatic assignment will be automatically accessed to trigger such
		assignment.
		"""
		
		super(Document, self).__init__(*args, **kw)
		
		# Trigger assignment of default values.
		for name, field in self.__fields__.items():
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
						document_class = dict,
						tz_aware = True,
						uuid_representation = STANDARD,
						tzinfo = utc,
					),
				read_preference = cls.__read_preference__,
				read_concern = None,  # TODO: Class-level configuration.
				write_concern = None,  # TODO: Class-level configuration.
			)
		
		cls.__bound__ = True
		cls.__collection__ = collection
		
		return cls
	
	@classmethod
	def _get_mongo_name_for(cls, name):
		"""Walk a string path (dot or double underscore separated) to find the MongoDB path to the attribute.
		
		This is the reverse of the process on individual Field._get_mongo_name, which walks up to the root document.
		"""
		
		current = cls
		
		if '__' in name:  # In case we're getting the name from a Django-style argument.
			name = name.replace('__', '.')
		
		path = []
		parts = name.split('.')
		
		while parts:
			part = parts.pop(0)
			
			if getattr(current, 'translated', False) and (not path or path[0] != 'localized'):
				path.insert(0, 'localized')  # We have a translated field on our hands...
			
			if hasattr(current, part):
				current = getattr(current, part)
				path.append(current.__name__)
		
		return '.'.join(path)
	
	@classmethod
	def from_mongo(cls, doc, projected=None):
		"""Convert data coming in from the MongoDB wire driver into a Document instance."""
		
		if '_cls' in doc:  # Instantiate any specific class mentioned in the data.
			cls = load(doc['_cls'], 'marrow.mongo.document')
		
		instance = cls()
		instance.__data__ = instance.__store__(doc)
		instance.__loaded__ = set(projected) if projected else None
		
		return instance
	
	def to_mongo(self):
		"""Convert data going back into the MongoDB wire driver. This is a no-op, just pass the instance instead."""
		return self
	
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
