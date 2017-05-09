# encoding: utf-8

from __future__ import unicode_literals

from collections import MutableMapping

from bson import ObjectId
from bson.json_util import dumps, loads

from ...package.loader import load
from ...package.canonical import name as named
from ...schema import Attributes, Container
from ...schema.compat import str, unicode, odict
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
	__type_store__ = None  # The pseudo-field to store embedded document class references as.
	__pk__ = None  # The primary key of the document, to make searchable if embedded, or the name of the '_id' field.
	
	__fields__ = Attributes(only=Field)  # An ordered mapping of field names to their respective Field instance.
	__fields__.__sequence__ = 10000  # TODO: project=False
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
	
	def _prepare_defaults(self):
		"""Trigger assignment of default values."""
		
		for name, field in self.__fields__.items():
			if field.assign:
				getattr(self, name)
	
	# Data Conversion and Casting
	
	@classmethod
	def from_mongo(cls, doc, projected=None):
		"""Convert data coming in from the MongoDB wire driver into a Document instance."""
		
		if doc is None:
			return None
		
		if isinstance(doc, Document):
			return doc
		
		if cls.__type_store__ in doc:  # Instantiate any specific class mentioned in the data.
			cls = load(doc[cls.__type_store__], 'marrow.mongo.document')
		
		instance = cls(_prepare_defaults=False)
		instance.__data__ = doc
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
	
	# Python Magic Methods
	
	def __repr__(self, *args, **kw):
		"""A generic programmers' representation of documents.
		
		We add a little non-standard protocol on top of Python's own `__repr__`, allowing passing of additional
		positional or keyword paramaters for inclusion in the result. This allows subclasses to define additional
		information not based on simple field presence.
		"""
		
		parts = []
		
		if self.__pk__:
			pk = getattr(self, self.__pk__, None)
			
			if isinstance(pk, ObjectId):
				pk = unicode(pk)
			elif isinstance(pk, (str, unicode)):
				pass
			else:
				pk = repr(pk)
			
			parts.append(pk)
		
		parts.extend(args)
		
		for name, field in self.__fields__.items():
			if name == self.__pk__:
				continue
			
			if field.repr is not None:
				if callable(field.repr):
					if not field.repr(self, field):
						continue
				else:
					if not field.repr:
						continue
			
			value = getattr(self, name, None)
			
			if value:
				parts.append(name + "=" + repr(value))
		
		for k in kw:
			parts.append(k + "=" + repr(kw[k]))
		
		if self.__type_store__:
			cls = self.get(self.__type_store__, named(self.__class__))
		else:
			cls = self.__class__.__name__
		
		return "{0}({1})".format(cls, ", ".join(parts))
	
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
	
	iteritems = items  # Python 2 interation, as per items.
	
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
