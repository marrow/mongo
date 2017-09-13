# encoding: utf-8

from __future__ import unicode_literals

from collections import OrderedDict, Mapping as _Mapping

from ....schema import Attribute
from .array import Array


class Mapping(Array):
	key = Attribute(default='name')
	
	def to_native(self, obj, name, value):
		kind = self._kind(obj.__class__)
		
		result = super(Mapping, self).to_native(obj, name, value)
		result = ((doc[~getattr(kind, self.key)], doc) for doc in result)
		
		return OrderedDict(result)
	
	def to_foreign(self, obj, name, value):
		if isinstance(value, _Mapping):
			value = value.values()
		
		return super(Mapping, self).to_foreign(obj, name, value)
