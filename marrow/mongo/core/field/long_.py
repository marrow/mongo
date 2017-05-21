# encoding: utf-8

from __future__ import unicode_literals

from bson.int64 import Int64

from .number import Number


class Long(Number):
	__foreign__ = 'long'
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return Int64(int(value))
