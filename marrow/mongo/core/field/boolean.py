# encoding: utf-8

from __future__ import unicode_literals

from .base import Field


class Boolean(Field):
	__foreign__ = 'bool'
	__disallowed_operators__ = {'#array'}
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		try:
			value = value.lower()
		except AttributeError:
			return bool(value)
		
		if value in ('true', 't', 'yes', 'y', 'on', '1', True):
			return True
		
		if value in ('false', 'f', 'no', 'n', 'off', '0', False):
			return False
		
		raise ValueError("Unknown or non-boolean value: " + value)
