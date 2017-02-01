# encoding: utf-8

from marrow.mongo import Document, Index
from marrow.mongo.field import PluginReference


class Derived(Document):
	"""Access and store the class reference to a particular Document subclass.
	
	This allows for easy access to the magical `_cls` key as the `cls` attribute.
	"""
	
	__type_store__ = '_cls'  # The pseudo-field to store embedded document class references as.
	
	cls = PluginReference('marrow.mongo.document', '_cls')  # TODO: Auto-calculate from instance.
	
	_cls = Index('cls')
