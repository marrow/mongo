# encoding: utf-8

from ..core.field import Field


class Embed(Field):
	kind = Attribute(default=None)
	
	__foreign__ = 'object'


class Reference(Field):
	__foreign__ = 'object'
