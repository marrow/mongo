# encoding: utf-8

from weakref import WeakValueDictionary

from ... import Document, Index
from ...field import PluginReference


class Derived(Document):
	"""Access and store the class reference to a particular Document subclass.
	
	This allows for easy access to the magical `_cls` key as the `cls` attribute. This value will be populated
	automatically.  It also allows for easier access to and automatic tracking of subclasses, via the `__subclasses__` mapping attribute.
	"""
	
	__type_store__ = '_cls'  # The pseudo-field to store embedded document class references as.
	
	cls = PluginReference('marrow.mongo.document', '_cls', explicit=True, repr=False, positional=False)
	
	_cls = Index('cls')
	
	def __init__(self, *args, **kw):
		"""Automatically derive and store the class path or plugin reference name."""
		
		kw.setdefault('cls', self.__class__)
		super(Derived, self).__init__(*args, **kw)
	
	@classmethod
	def __attributed__(cls):
		"""Record the construction of a subclass."""
		
		if cls.__name__ == 'Derived':
			return
		
		if not hasattr(cls, '__subclasses__'):
			cls.__dict__['__subclasses__'] = WeakValueDictionary()
			return
		
		cls.__subclasses__[cls.__name__] = cls