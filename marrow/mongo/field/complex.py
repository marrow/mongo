# encoding: utf-8

from marrow.schema import Attribute

from ..core import Field


class Embed(Field):
	kind = Attribute(default=None)
	
	__foreign__ = 'object'


class Reference(Field):
	__foreign__ = 'object'
