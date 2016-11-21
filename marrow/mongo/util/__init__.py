# encoding: utf-8

from marrow.package.loader import load


SENTINEL = object()  # Singleton value to detect unassigned values.


def adjust_attribute_sequence(amount=10000, *fields):
	"""Move marrow.schema fields around to control positional instantiation order."""
	
	def adjust_inner(cls):
		for field in fields:
			cls.__dict__[field].__sequence__ += amount  # Move this to the back of the bus.
		
		return cls
	
	return adjust_inner


class Registry(object):
	__path__ = []
	
	def __init__(self, namespace):
		self._namespace = namespace
	
	def __getattr__(self, name):
		self.__dict__[name] = load(name, self._namespace)
		return self.__dict__[name]
	
	def __getitem__(self, name):
		return load(name, self._namespace)
