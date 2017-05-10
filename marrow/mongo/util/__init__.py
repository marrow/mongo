# encoding: utf-8

from __future__ import unicode_literals

from collections import OrderedDict
from datetime import datetime
from operator import attrgetter
from bson.tz_util import utc

from marrow.schema.meta import ElementMeta
from ...package.loader import load


SENTINEL = object()  # Singleton value to detect unassigned values.


def adjust_attribute_sequence(*fields):
	"""Move marrow.schema fields around to control positional instantiation order."""
	
	amount = None
	
	if fields and isinstance(fields[0], int):
		amount, fields = fields[0], fields[1:]
	
	def adjust_inner(cls):
		for field in fields:
			if field not in cls.__dict__:
				# TODO: Copy the field definition.
				raise TypeError("Can only override sequence on non-inherited attributes.")
			
			# Adjust the sequence to re-order the field.
			if amount is None:
				cls.__dict__[field].__sequence__ = ElementMeta.sequence
			else:
				cls.__dict__[field].__sequence__ += amount  # Add the given amount.
		
		# Update the attribute collection.
		cls.__attributes__ = OrderedDict(
					(k, v) for k, v in \
					sorted(cls.__attributes__.items(),
						key=lambda i: i[1].__sequence__)
				)
		
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


def utcnow():
	return datetime.utcnow().replace(tzinfo=utc)
