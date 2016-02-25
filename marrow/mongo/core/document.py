# encoding: utf-8

from collections import OrderedDict as odict, MutableMapping
from itertools import chain

from marrow.package.loader import load
from marrow.schema import Element, Container, Attribute

from .util import py2, SENTINEL, adjust_attribute_sequence


class Document(Container):
	__store__ = odict
	__foreign__ = 'object'
	
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
		return len(self.__data__)
	
	if py2:
		def keys(self):
			return self.__data__.iterkeys()
		
		def items(self):
			return self.__data__.iteritems()
		
		def values(self):
			return self.__data__.itervalues()
	
	else:
		def keys(self):
			return self.__data__.keys()
		
		def items(self):
			return self.__data__.items()
		
		def values(self):
			return self.__data__.values()
	
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
