from collections import OrderedDict as odict
from datetime import datetime, timedelta
from operator import attrgetter
from pkg_resources import iter_entry_points, DistributionNotFound

from typeguard import check_argument_types

from ...schema.meta import ElementMeta
from ...package.loader import load


# Conditional dependencies.

try:
	from pytz import utc  # Richer, more capable implementation.
except ImportError:
	from bson.tz_util import utc  # Fallback on hard dependency.


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
		cls.__attributes__ = odict(
					(k, v) for k, v in \
					sorted(cls.__attributes__.items(),
						key=lambda i: i[1].__sequence__)
				)
		
		return cls
	
	return adjust_inner


class Registry:
	def __init__(self, namespace: str):
		assert check_argument_types()
		
		self._namespace = namespace
		self.__path__ = []
	
	@property
	def __all__(self):
		names = []
		
		for point in iter_entry_points(self._namespace):
			try:
				point.require()
			except DistributionNotFound:
				continue
			else:
				names.append(point.name)
		
		return names
	
	def __getattr__(self, name:str):
		if name[0] == '_':
			raise AttributeError()
		
		self.__dict__[name] = load(name, self._namespace)
		return self.__dict__[name]
	
	def __getitem__(self, name:str):
		if name[0] == '_':
			raise IndexError()
		
		if name not in self.__dict__:
			try:
				self.__dict__[name] = load(name, self._namespace)
			except DistributionNotFound:
				raise IndexError()
		
		return self.__dict__[name]
	
	def __dir__(self):
		return super(Registry, self).__dir__() + self.__all__
	
	def __contains__(self, name:str):
		"""Identify if a plugin with the given short name exists."""
		
		if name[0] == '_':
			return False
		
		if name in self.__dict__:
			return True
		
		try:
			self.__getitem__(name)
		except LookupError:
			return False
		
		return True


def utcnow() -> datetime:
	"""Return the current time in UTC, with timezone information applied."""
	return datetime.utcnow().replace(microsecond=0, tzinfo=utc)


def datetime_period(base:datetime=None, *, hours:int=None, minutes:int=None, seconds:int=None) -> datetime:
	"""Round a datetime object down to the start of a defined period.
	
	The `base` argument may be used to find the period start for an arbitrary datetime, defaults to `utcnow()`.
	"""
	
	assert check_argument_types()
	
	if base is None:
		base = utcnow()
	
	base -= timedelta(
			hours = 0 if hours is None else (base.hour % hours),
			minutes = (base.minute if hours else 0) if minutes is None else (base.minute % minutes),
			seconds = (base.second if minutes or hours else 0) if seconds is None else (base.second % seconds),
			microseconds = base.microsecond
		)
	
	return base
