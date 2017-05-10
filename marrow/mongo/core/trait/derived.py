# encoding: utf-8

from ... import Document, Index
from ...field import PluginReference


class Derived(Document):
	"""Access and store the class reference to a particular Document subclass.
	
	This allows for easy access to the magical `_cls` key as the `cls` attribute.
	"""
	
	__type_store__ = '_cls'  # The pseudo-field to store embedded document class references as.
	
	cls = PluginReference('marrow.mongo.document', '_cls', explicit=True, repr=False)
	cls.__sequence__ += 1000000
	
	_cls = Index('cls')
	
	def __init__(self, *args, **kw):
		"""Automatically derive and store the class path or plugin reference name."""
		
		super(Derived, self).__init__(*args, **kw)
		
		self.cls = self.__class__
