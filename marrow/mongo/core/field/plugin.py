from pkg_resources import iter_entry_points
from typing import Union, Optional, Mapping

from ....package.canonical import name as canon
from ....package.loader import load
from ....schema import Attribute

from .base import Field


class PluginReference(Field):
	"""A Python object reference.
	
	Generally, for safety sake, you want this to come from a list of available plugins in a given namespace. If a
	namespace is given, the default for `explicit` will be `False`.  If `explicit` is `True` (or no namespace is
	defined) object assignments and literal paths will be allowed.
	"""
	
	namespace: Optional[str] = Attribute(default=None)  # The plugin namespace to use when loading.
	explicit: Optional[bool] = Attribute()  # Allow explicit, non-plugin references.
	mapping: Optional[Mapping[str,str]] = Attribute(default=None)  # To ease support for legacy records, textual replacements.
	
	__foreign__ = {'string'}
	
	def __init__(self, *args, **kw):
		if args:
			kw['namespace'] = args[0]
			args = args[1:]
		
		super(PluginReference, self).__init__(*args, **kw)
	
	def to_native(self, obj, name:str, value:str):  # pylint:disable=unused-argument
		"""Transform the MongoDB value into a Marrow Mongo value."""
		
		if self.mapping:
			for original, new in self.mapping.items():
				value = value.replace(original, new)
		
		return load(value, self.namespace)
	
	def to_foreign(self, obj, name:str, value) -> str:  # pylint:disable=unused-argument
		"""Transform to a MongoDB-safe value."""
		
		namespace = self.namespace
		
		try:
			explicit = self.explicit
		except AttributeError:
			explicit = not namespace
		
		if not isinstance(value, str):
			value = canon(value)
		
		if namespace and ':' in value:  # Try to reduce to a known plugin short name.
			for point in iter_entry_points(namespace):  # TODO: Isolate.
				qualname = point.module_name
				
				if point.attrs:
					qualname += ':' + '.'.join(point.attrs)
				
				if qualname == value:
					value = point.name
					break
		
		if ':' in value:
			if not explicit:
				raise ValueError("Explicit object references not allowed.")
			
			return value
		
		if namespace and value not in (i.name for i in iter_entry_points(namespace)):
			raise ValueError('Unknown plugin "' + value + '" for namespace "' + namespace + '".')
		
		return value
