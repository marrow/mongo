# encoding: utf-8

from __future__ import unicode_literals

from .array import Array


class Set(Array):
	class List(set):
		"""Placeholder set shadow class to identify already-cast sets."""
		
		@classmethod
		def new(cls):
			return cls()
