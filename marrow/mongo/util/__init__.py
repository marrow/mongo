# encoding: utf-8

from __future__ import unicode_literals

from collections import OrderedDict
from datetime import datetime, timedelta
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
	"""Return the current time in UTC, with timezone information applied."""
	return datetime.utcnow().replace(tzinfo=utc)


def datetime_period(base=None, hours=None, minutes=None, seconds=None):
	"""Round a datetime object down to the start of a defined period.
	
	The `base` argument may be used to find the period start for an arbitrary datetime, defaults to `utcnow()`.
	"""
	
	if base is None:
		base = utcnow()
	
	base -= timedelta(
			hours = 0 if hours is None else (base.hour % hours),
			minutes = (base.minute if hours else 0) if minutes is None else (base.minute % minutes),
			seconds = (base.second if minutes or hours else 0) if seconds is None else (base.second % seconds),
			microseconds = base.microsecond
		)
	
	return base
