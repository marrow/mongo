# encoding: utf-8

from __future__ import unicode_literals

from .array import Array


class Set(Array):
	List = list
	
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		result = super(Set, self).to_native(obj, name, value)
		
		if result is not None:
			result = set(result)
		
		return result
