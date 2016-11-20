# encoding: utf-8

"""MongoDB filter, projection, and update operation helpers.

These encapsulate the functionality of creating combinable mappings 
"""

from __future__ import unicode_literals

from copy import deepcopy
from collections import Mapping, MutableMapping
from pytz import utc
from bson.codec_options import CodecOptions
from marrow.schema.compat import odict

from ..util import SENTINEL
from ..util.compat import py3, unicode



class Ops(object):
	__slots__ = ('operations', 'collection', 'document')
	
	def __init__(self, operations=None, collection=None, document=None):
		self.operations = operations or odict()
		self.collection = collection
		self.document = document
	
	def __repr__(self, extra=None):
		return "{}({}{}{}{})".format(
				self.__class__.__name__,
				repr([(i, j) for i, j in self.operations.items()]),
				", collection={}".format() if self.collection else "",
				", document={}".format() if self.document else "",
				extra or ""
			)
	
	@property
	def as_query(self):
		return self.operations
	
	# Binary Operator Protocols
	
	def __and__(self, other):
		operations = deepcopy(self.operations)
		other = self.__class__(
				operations = other.as_query if hasattr(other, 'as_query') else other,
				collection = self.collection,
				document = self.document
			)
		
		for k, v in getattr(other, 'operations', {}).items():
			if k not in operations:
				operations[k] = v
			else:
				if not isinstance(operations[k], Mapping):
					operations[k] = odict((('$eq', operations[k]), ))
				
				if not isinstance(v, Mapping):
					v = odict((('$eq', v), ))
				
				operations[k].update(v)
		
		return self.__class__(operations=operations, collection=self.collection, document=self.document)
	
	def __or__(self, other):
		operations = deepcopy(self.operations)
		
		other = other.as_query if hasattr(other, 'as_query') else other
		
		if len(operations) == 1 and '$or' in operations:
			# Update existing $or.
			operations['$or'].append(other)
			return self.__class__(
					operations = operations,
					collection = self.collection,
					document = self.document
				)
		
		return self.__class__(
				operations = {'$or': [operations, other]},
				collection = self.collection,
				document = self.document
			)
	
	# Mapping Protocol
	
	def __getitem__(self, name):
		return self.operations[name]
	
	def __setitem__(self, name, value):
		self.operations[name] = value
	
	def __delitem__(self, name):
		del self.operations[name]
	
	def __iter__(self):
		return iter(self.operations.keys())
	
	def __len__(self):
		return len(self.operations)
	
	if py3:
		def keys(self):
			return self.operations.keys()
		
		def items(self):
			return self.operations.items()
		
		def values(self):
			return self.operations.values()
	
	else:
		def keys(self):
			return self.operations.iterkeys()
		
		def items(self):
			return self.operations.iteritems()
		
		def values(self):
			return self.operations.itervalues()
	
	def __contains__(self, key):
		return key in self.operations
	
	def __eq__(self, other):
		return self.operations == other
	
	def __ne__(self, other):
		return self.operations != other
	
	def get(self, key, default=None):
		return self.operations.get(key, default)
	
	def clear(self):
		self.operations.clear()
	
	def pop(self, name, default=SENTINEL):
		if default is SENTINEL:
			return self.operations.pop(name)
		
		return self.operations.pop(name, default)
	
	def popitem(self):
		return self.operations.popitem()
	
	def update(self, *args, **kw):
		self.operations.update(*args, **kw)
	
	def setdefault(self, key, value=None):
		return self.operations.setdefault(key, value)


MutableMapping.register(Ops)  # Metaclass conflict if we subclass.
