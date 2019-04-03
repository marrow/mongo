from weakref import WeakValueDictionary

from ... import Document, Index
from ...field import PluginReference


class Derived(Document):
	"""Access and store the class reference to a particular Document subclass.
	
	This allows for easy access to the magical `_cls` key as the `cls` attribute. This value will be populated
	automatically.  This also allows for transformation (promotion/demotion) to a more specialized subclass or more
	general parent class respectively.
	"""
	
	__type_store__ = '_cls'  # The pseudo-field to store embedded document class references as.
	
	cls = PluginReference('marrow.mongo.document', '_cls', explicit=True, repr=False, positional=False)
	
	_cls = Index('cls')
	
	def __init__(self, *args, **kw):
		"""Automatically derive and store the class path or plugin reference name."""
		
		kw.setdefault('cls', self.__class__)
		super(Derived, self).__init__(*args, **kw)
	
	def _as(self, cls, update=False, preserve=True):
		self.cls = cls
		
		# if update:  TODO: Optionally actually update the record.
		
		return cls.from_mongo(self.__data__)
	
	def promote(self, cls, update=False, preserve=True):
		"""Transform this record into an instance of a more specialized subclass."""
		
		if not issubclass(cls, self.__class__):
			raise TypeError("Must promote to a subclass of " + self.__class__.__name__)
		
		return self._as(cls, update, preserve)
	
	def demote(self, cls=None, update=False, preserve=True):
		"""Transform this record into an instance of a more generalized parent class.
		
		Defaults to the immediate parent class, if unambiguous (singular).
		"""
		
		if not issubclass(self.__class__, cls):
			raise TypeError("Must demote to a superclass of " + self.__class__.__name__)
		
		return self._as(cls, update, preserve)
