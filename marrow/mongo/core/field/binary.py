# encoding: utf-8

from __future__ import unicode_literals

from .base import Field


class Binary(Field):
	__foreign__ = 'binData'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		return bytes(value)
