# encoding: utf-8

from __future__ import unicode_literals

from .number import Number


class Integer(Number):
	__foreign__ = 'integer'
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return int(value)
