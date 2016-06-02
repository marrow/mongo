# encoding: utf-8

from pymongo.common import CodecOptions
from collections import OrderedDict as odict, MutableMapping

from marrow.package.loader import load
from marrow.schema import Element, Container, Attributes

from .field import Field
from ..util import SENTINEL
from ..util.compat import py3


class Document(Container):
	__store__ = odict
	__foreign__ = 'object'
	__fields__ = Attributes(only=Field)
	__fields__.__sequence__ = 20000
	
	def __init__(self, *args, **kw):
		fields = self.__fields__ = self.__fields__
		super(Document, self).__init__(*args, **kw)
		for name, field in fields.items():
			if field.generated:
				getattr(self, name)
	
	@classmethod
	def bind(cls, collection):
		return collection.with_options(codec_options=CodecOptions(document_class=cls))
	
	@classmethod
	def from_mongo(cls, doc):
		if '_cls' in doc:
			cls = load(doc['_cls'])
		
		instance = cls()
		instance.__data__ = instance.__store__(doc)
		
		return instance
	
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
