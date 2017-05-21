# encoding: utf-8

from __future__ import unicode_literals

from bson import ObjectId

from .base import Field


class Date(Field):
	__foreign__ = 'date'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		if isinstance(value, ObjectId):
			return value.generation_time
		
		return value
