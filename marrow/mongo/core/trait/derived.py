# encoding: utf-8

from ... import Document, Index
from ...field import PluginReference


class Derived(Document):
	"""Access and store the class reference to a particular Document subclass.
	
	This allows for easy access to the magical `_cls` key as the `cls` attribute.
	"""
	
	__type_store__ = '_cls'  # The pseudo-field to store embedded document class references as.
	
	cls = PluginReference('marrow.mongo.document', '_cls', explicit=True, repr=False)
	
	_cls = Index('cls')
