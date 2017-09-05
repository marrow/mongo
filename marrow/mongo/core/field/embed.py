# encoding: utf-8

from __future__ import unicode_literals

from .base import _HasKind, _CastingKind, Field


class Embed(_HasKind, _CastingKind, Field):
	__foreign__ = 'object'
	__allowed_operators__ = {'#document', '$eq', '#rel'}
	
	def __init__(self, *args, **kw):
		if args:
			kw['kind'], args = args[0], args[1:]
			kw.setdefault('default', lambda: self._kind()())
		
		super(Embed, self).__init__(*args, **kw)
