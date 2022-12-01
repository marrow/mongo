# encoding: utf-8

from __future__ import unicode_literals

from .string import String


class Path(String):
	def to_native(self, obj, name, value):  # pylint:disable=unused-argument
		return _Path(value)
