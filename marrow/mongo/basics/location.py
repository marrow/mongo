# encoding: utf-8

"""Common Location (address) model."""

from ...schema.compat import unicode, py3
from .. import Document
from ..field import String, Embed


__all__ = ('BaseLocation', )


class BaseLocation(Document):
	address = String()
	city = String()
	region = String()
	country = String()
	postal = String()
	geo = Embed('Point')
	
	def __unicode__(self):
		# TODO: Locale
		parts = [getattr(self, i, None) for i in self.__fields__]
		return "\n".join(unicode(i) for i in parts if i)
	
	if py3:
		__str__ = __unicode__
	
	def __repr__(self):
		parts = [(i + "=" + repr(getattr(self, i, None))) for i in self.__fields__]
		return self.__class__.__name__ + "(" + ", ".join(parts) + ")"
